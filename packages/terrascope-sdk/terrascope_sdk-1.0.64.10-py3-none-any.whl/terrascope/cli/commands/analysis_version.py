#!/usr/bin/env python

import click
import asyncio
import os
import json
import yaml
import pandas as pd
import tabulate
import terrascope.cli.lib.utils as tsu
from terrascope.cli.lib.aliased_group import AliasedGroup
import terrascope.cli.lib.workflow as wf
from google.protobuf.json_format import MessageToDict


@click.command(cls=AliasedGroup, help="Analysis 'version' command group")
@click.pass_context
def version(ctx):
    pass


@version.command('get')
@click.pass_context
@click.option('-iV', '--analysis_version_id', type=str)
@click.option('-iA', '--analysis_id', type=str)
@click.option('-nA', '--analysis_name', type=str)
@click.option('-C', '--only_columns', multiple=True)
@click.option('-c', '--append_columns', multiple=True)
@click.option('-T', '--transpose', is_flag=True)
@click.option('-om', '--output_manifest', type=str,
              help="Write manifest to this filename.", default=None)
def analysis_version_get(
        ctx,
        analysis_version_id,
        analysis_id,
        analysis_name,
        only_columns,
        append_columns,
        transpose,
        output_manifest=None,
):

    columns = ['id', 'created_on', 'analysis.name', 'analysis.author']
    if only_columns:
        columns = list(only_columns)
    if append_columns:
        columns = columns + list(append_columns)

    # if they provide an explicit algo version ID, get it.
    analysis_versions = []
    if analysis_version_id:
        analysis_versions += asyncio.run(wf.get_analysis_versions(analysis_version_id=analysis_version_id))

    analysis_ids = []

    # If they give us a uuid, use it.  Otherwise, assume it's a name and look it up.
    if analysis_id:
        analysis_ids = [analysis_id]
    if analysis_name:
        analyses = asyncio.run(wf.list_analyses(analysis_name))
        analysis_ids = [analysis.id for analysis in analyses]

    for analysis_id in analysis_ids:
        analysis_versions += asyncio.run(wf.get_analysis_versions(analysis_id=analysis_id))

    if analysis_versions:
        data = []
        for analysis_version in analysis_versions:
            analysis_version_dict = tsu.protobuf_to_dict(analysis_version)
            data.append(analysis_version_dict)

        df = pd.DataFrame(data=data)
        if 'all' not in columns:
            df = df[tsu.match_columns(df.columns, columns)]
        df = df.rename(columns={'id': 'analysis_version_id'})
        if transpose:
            dfT = df.T
            if 'algorithm_versions' in df.keys():
                algo_ver = df['algorithm_versions'].values[0]
                dfT.drop('algorithm_versions', inplace=True)
                dfT = dfT.append(pd.json_normalize(algo_ver).T)
            df = tabulate.tabulate(dfT, maxcolwidths=[None, 50])

        tsu.set_pandas_display()
        click.secho(f"analysis_id: {analysis_id}", fg='cyan')
        click.echo(df)

    if output_manifest:

        n_versions = len(analysis_versions)
        for analysis_version in analysis_versions:

            manifest = MessageToDict(analysis_version.analysis_manifest)
            analysis_id = analysis_version.analysis.id
            manifest['analysis_id'] = analysis_id
            manifest['analysis_name'] = analysis_version.analysis.name

            output_manifest_fname = output_manifest
            if n_versions > 1:
                fname, ext = os.path.splitext(output_manifest)
                output_manifest_fname = f"{fname}_{analysis_id[:8]}.{ext}"
            with open(output_manifest_fname, 'w') as fp:
                if output_manifest.endswith('json'):
                    json.dump(manifest, fp, indent=4)
                else:
                    yaml.dump(manifest, fp)


@version.command('create')
@click.pass_context
@click.option('-iA', '--analysis_id', type=str)
@click.option('-iv', '--algorithm_version_id', type=str)
@click.option('-nA', '--analysis_name', type=str)
@click.option('-D', '--description', type=str)
@click.option('-V', '--version', type=str)
@click.option('-T', '--tags', type=str, multiple=True)
@click.option('--dry_run', is_flag=True, default=False)
def analysis_version_create(
        ctx,
        analysis_id,
        algorithm_version_id,
        analysis_name,
        description,
        version,
        tags,
        dry_run,
):

    wf.check_environment_complete(raise_on_failure=True)
    manifest = wf.create_analysis_manifest(
        analysis_name,
        algorithm_version_id,
        description,
        version,
        tags
    )
    if not dry_run:
        analysis_version_id = asyncio.run(
            wf.create_analysis_version(
                analysis_id,
                manifest,
            )
        )

        click.echo(f"Your new analysis_version_id is: {analysis_version_id}")
