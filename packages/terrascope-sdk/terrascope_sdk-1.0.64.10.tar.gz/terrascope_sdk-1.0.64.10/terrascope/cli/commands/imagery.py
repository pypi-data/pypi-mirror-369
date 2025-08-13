#!/usr/bin/env python

import click
import asyncio
import pandas as pd
import numpy as np
import terrascope.cli.lib.workflow as wf
import terrascope.cli.lib.utils as tsu
from terrascope.cli.lib.aliased_group import AliasedGroup
import shapely.wkb as shp_wkb
import shapely.wkt as shp_wkt
import base64
import geopandas as gpd
import sys
import timezonefinder as tzf
import pytz


@click.command(cls=AliasedGroup, help="'imagery' command group")
@click.pass_context
def imagery(ctx):
    pass


class MatchChoice(click.Choice):
    def convert(self, value, param, ctx):
        for choice in self.choices:
            if choice.startswith(value.upper()):
                return choice
        self.fail(f"'{value}' does not match any options: {self.choices}", param, ctx)


@imagery.command('search')
@click.pass_context
@click.option('-S', '--shp_file')
@click.option('--aoi_id', default=None, help="aoi_id of geom in shp_file (default to first AOI if None)")
@click.option('-g', '--geom_wkt')
@click.option('-ts', '--datetime_start', type=pd.to_datetime)
@click.option('-te', '--datetime_end', type=pd.to_datetime)
@click.option('-d', '--data_source_id')
@click.option('-p', '--product_spec_name')
@click.option('-v', '--verbose', is_flag=True)
@click.option('-s', '--search_service', default='SCENE', type=MatchChoice(['SCENE', 'CATALOG']))
@click.option('-o', '--out_csv', default=None)
@click.option('-q', '--quiet', is_flag=True, help="Do not print to stdout")
def imagery_search(
        ctx,
        shp_file,
        aoi_id,
        geom_wkt,
        datetime_start,
        datetime_end,
        data_source_id,
        product_spec_name,
        verbose,
        search_service='SCENE',
        out_csv=None,
        quiet=False,
):

    if geom_wkt is None:
        if shp_file is None:
            click.secho("Must provide with geom_wkt or a shp_file", fg='red')
            sys.exit(1)

        gdf = gpd.read_file(shp_file)
        if aoi_id is not None:
            if 'aoi_id' in gdf.keys():
                this_aoi = gdf['aoi_id'] == aoi_id
            elif 'Name' in gdf.keys():
                this_aoi = gdf['Name'] == aoi_id
            else:
                this_aoi = np.zeros(len(gdf)).astype(bool)
                this_aoi[0] = True
            geom = gdf[this_aoi]['geometry'].values[0]

        else:
            # if they don't give an aoi_id, just use the first 1
            geom = gdf['geometry'].values[0]

        geom_wkt = geom.wkt

    else:
        geom = shp_wkt.loads(geom_wkt)

    scenes = asyncio.run(
        wf.search_imagery(
            geom_wkt,
            datetime_start,
            datetime_end,
            data_source_id,
            product_spec_name,
            search_service=search_service,
        ))
    scenes = tsu.protobuf_to_dict(scenes)

    if not scenes:
        click.secho("No matching scenes were found.", fg='yellow')
        sys.exit()

    scenes = scenes.get('results', [])

    data = []
    tf = tzf.TimezoneFinder()
    centroid = geom.centroid
    timezone_str = tf.timezone_at(lng=centroid.x, lat=centroid.y)
    timezone = pytz.timezone(timezone_str)

    for scene in scenes:

        wkb = scene['image_geom_wkb']
        geom = shp_wkb.loads(base64.b64decode(wkb))
        centroid = geom.centroid

        utc = pd.to_datetime(scene['acquired_ts'])
        local = utc.astimezone(timezone)
        this_scene = [
            utc.strftime('%Y-%m-%dT%H:%M:%S'),
            local.strftime('%Y-%m-%dT%H:%M:%S'),
            centroid.x,
            centroid.y,
            scene['metadata'].get('aoi_coverage_percent', np.nan),
            scene['metadata'].get('cloud_cover', np.nan),
            scene['metadata'].get('sat_azimuth', np.nan),
            scene['metadata'].get('sat_elevation', np.nan),
            scene['metadata'].get('sun_azimuth', np.nan),
            scene['metadata'].get('sun_elevation', np.nan),
        ]
        if verbose:
            this_scene += [
                scene['id'],
                scene['provider_scene_id'],
                scene['image_geom_wkb'],
            ]
        data.append(this_scene)

    columns = ['acquired_utc', 'acquired_local', 'lon', 'lat', 'aoi_cov%',
               'cloud_frac', 'sat_az', 'sat_el', 'sun_az', 'sun_el']
    if verbose:
        columns += ['id', 'provider_scene_id', 'wkb']
    df = pd.DataFrame(data, columns=columns)
    if not quiet:
        click.echo(df.to_string(float_format='%.2f'))
    if out_csv:
        df.to_csv(out_csv)
