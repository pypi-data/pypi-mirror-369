#!/usr/bin/env python

import click
import sys
import asyncio
import pandas as pd
import terrascope.cli.lib.workflow as wf
import terrascope.cli.lib.utils as tsu
from terrascope.cli.lib.aliased_group import AliasedGroup


@click.command(cls=AliasedGroup, help="Analysis 'config' command group")
@click.pass_context
def config(ctx):
    pass


@config.command('get')
@click.pass_context
@click.option('-iC', '--analysis_config_id', type=str)
@click.option('-iV', '--analysis_version_id', type=str)
@click.option('-C', '--only_columns', multiple=True)
@click.option('-c', '--append_columns', multiple=True)
@click.option('-T', '--transpose', is_flag=True)
def analysis_config_get(
        ctx,
        analysis_config_id,
        analysis_version_id,
        only_columns,
        append_columns,
        transpose,
):

    ana_configs = asyncio.run(wf.get_analysis_configs(analysis_version_id=analysis_version_id,
                                                      analysis_config_id=analysis_config_id))

    columns = ['name', 'id', 'description', 'created_on']
    if only_columns:
        columns = list(only_columns)
    if append_columns:
        columns = columns + list(append_columns)

    data = []
    for ana_config in ana_configs:
        pbdict = tsu.protobuf_to_dict(ana_config)
        if 'analysis_configs' in pbdict:
            pbdict = pbdict['analysis_configs'][0]
        data.append(pbdict)
    df = pd.DataFrame(data)
    if 'all' not in columns:
        df = df[tsu.match_columns(df.columns, columns)]
    df = df.rename(columns={'id': 'analysis_config_id'})
    if transpose:
        df = df.T

    tsu.set_pandas_display()
    click.secho(f"analysis_version_id: {analysis_version_id}", fg='cyan')
    click.echo(df)


@config.command('list')
@click.pass_context
@click.option('-nC', '--analysis_config_name', type=str)
@click.option('-C', '--only_columns', multiple=True)
@click.option('-c', '--append_columns', multiple=True)
@click.option('-T', '--transpose', is_flag=True)
def analysis_config_list(
        ctx,
        analysis_config_name,
        only_columns,
        append_columns,
        transpose,
):

    ana_configs = asyncio.run(wf.list_analysis_configs(analysis_config_name=analysis_config_name))

    columns = ['name', 'id', 'created_on']
    if only_columns:
        columns = list(only_columns)
    if append_columns:
        columns = columns + list(append_columns)

    data = []
    for ana_config in ana_configs:
        pbdict = tsu.protobuf_to_dict(ana_config)
        if 'analysis_configs' in pbdict:
            pbdict = pbdict['analysis_configs'][0]
        data.append(pbdict)
    df = pd.DataFrame(data)
    if 'all' not in columns:
        df = df[tsu.match_columns(df.columns, columns)]
    df = df.rename(columns={'id': 'analysis_config_id'})
    if transpose:
        df = df.T

    tsu.set_pandas_display()

    click.echo(df)


@config.command('create')
@click.pass_context
@click.option('-iV', '--analysis_version_id', type=str)
@click.option('-ic', '--algorithm_config_id', type=str)
@click.option('-nC', '--analysis_config_name', type=str, help="This is the analysis name shown in the UI")
@click.option('-dC', '--analysis_config_desc', type=str, help="This is the TS description shownin the UI")
@click.option('--dry_run', is_flag=True)
def analysis_config_create(
        ctx,
        analysis_version_id,
        algorithm_config_id,
        analysis_config_name,
        analysis_config_desc,
        dry_run,
):

    wf.check_environment_complete(raise_on_failure=True)

    click.echo("Using the following information:")
    click.echo(f"--> analysis_version_id:      {analysis_version_id}")
    click.echo(f"--> algorithm_config_id:      {algorithm_config_id}")
    click.echo(f"--> analysis_config_name:     {analysis_config_name}")
    click.echo(f"--> analysis_config_desc:     {analysis_config_desc}")

    if not dry_run:
        analysis_config_id = asyncio.run(
            wf.create_analysis_config(
                analysis_version_id,
                algorithm_config_id,
                analysis_config_name,
                analysis_config_desc,
            )
        )
        tsu.echo_highlight_suffix("You're new analysis_config_id is: ", analysis_config_id, 'green')


@config.command('deactivate')
@click.pass_context
@click.option('-iC', '--analysis_config_ids', type=str, multiple=True, required=False,
              help="UUIDs of the analysis_configs to deactivate")
@click.option('-nC', '--analysis_config_name', type=str, required=False,
              help="Name of the analysis_config to deactivate (will match all)")
def analysis_config_deactivate(
        ctx,
        analysis_config_ids,
        analysis_config_name,
):

    if analysis_config_name:
        ana_configs = asyncio.run(wf.list_analysis_configs(analysis_config_name=analysis_config_name))

        data = []
        for ana_config in ana_configs:
            data.append([ana_config.id, ana_config.name])
        df = pd.DataFrame(data=data, columns=['analysis_config_id', 'analysis_config_name'])
        click.secho("I found these analysis_configs:", fg='red')
        click.echo(df)
        stdin = input("  DELETE ALL ?  [Y/N]: ")

        if stdin in ('Y', 'y'):
            click.secho("OK.  Deactivating analysis_configs", fg='red')
        else:
            click.secho("OK.  Exiting.", fg='red')
            sys.exit(0)

        analysis_config_ids += tuple(df['analysis_config_id'].values)

    response = asyncio.run(wf.deactivate_analysis_configs(analysis_config_ids=analysis_config_ids))

    click.echo("Deactivation response code: ", nl=False)
    if response:
        click.secho(f" {response} (FAILURE)", fg='red')
    else:
        click.secho(f" {response} (SUCCESS)", fg='green')
