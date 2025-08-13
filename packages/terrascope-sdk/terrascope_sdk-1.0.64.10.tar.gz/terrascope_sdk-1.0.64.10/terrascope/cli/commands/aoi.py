#!/usr/bin/env python

import click
import asyncio
import pandas as pd
import terrascope.cli.lib.workflow as wf
import terrascope.cli.lib.utils as tsu
from terrascope.cli.lib.aliased_group import AliasedGroup


@click.command(cls=AliasedGroup, help="'aoi' command group")
@click.pass_context
def aoi(ctx):
    pass


@aoi.command('get')
@click.pass_context
@click.option('-i', '--aoi_collection_id', type=str)
@click.option('-v', '--verbose', is_flag=True)
def aoi_get(ctx, aoi_collection_id, verbose):

    aoi_collection = asyncio.run(wf.get_aoi_collection(aoi_collection_id))
    data = []
    for aoi in aoi_collection:
        data.append(tsu.protobuf_to_dict(aoi))
    df = pd.DataFrame(data)

    if verbose:
        click.echo(aoi_collection)
    click.echo(df.T)


@aoi.command('list')
@click.pass_context
@click.option('-v', '--verbose', is_flag=True, default=False)
def aoi_list(ctx, verbose=False):

    aoi_collections = asyncio.run(wf.list_aoi_collections())
    aoi_collections = tsu.protobuf_to_dict(aoi_collections)['aoi_versions']
    data = []
    for aoi_collection in aoi_collections:
        data.append(aoi_collection)
    df = pd.DataFrame(data)

    if verbose:
        tsu.set_pandas_display()
    else:
        df = df[['aoi_id', 'aoi_name', 'timezone']]

    click.echo(df)


@aoi.command('create')
@click.pass_context
@click.option('-a', '--aoi_file', type=str)
def aoi_create(ctx, aoi_file):

    aoi_collection_id = asyncio.run(wf.create_aoi_collection(aoi_file))
    tsu.echo_highlight_suffix("Your new aoi_collection_id is: ", aoi_collection_id, 'green')


@aoi.command('update')
@click.pass_context
@click.option('-i', '--aoi_collection_id', type=str, required=True)
@click.option('-a', '--aoi_file', type=str)
def aoi_update(ctx, aoi_collection_id, aoi_file):

    aoi_collection_id = asyncio.run(wf.upload_aoi(aoi_collection_id, aoi_file))
    tsu.echo_highlight_suffix("Your updated aoi_collection_id is: ", aoi_collection_id, 'green')


@aoi.command('delete')
@click.pass_context
@click.option('-i', '--aoi_collection_ids', multiple=True)
def aoi_delete(ctx, aoi_collection_ids):

    click.secho("I'm sorry.  It is not possible to delete an aoi_collection", fg='red')
    # asyncio.run(wf.delete_aois(aoi_collection_ids))
