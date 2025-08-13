#!/usr/bin/env python

import click
import asyncio
import pandas as pd
import yaml
import terrascope.cli.lib.utils as tsu
from terrascope.cli.lib.aliased_group import AliasedGroup
import terrascope.cli.lib.workflow as wf


@click.group(cls=AliasedGroup, help="Algorithm 'config' command group")
@click.pass_context
def config(ctx):
    pass


@config.command('get')
@click.pass_context
@click.option('-ic', '--algorithm_config_id', type=str, default=None,
              help="UUID of the algorithm config to look up.")
@click.option('-iv', '--algorithm_version_id', type=str, default=None,
              help="UUID of an algorithm version to look up associated algorithm configs.")
@click.option('-n', '--algorithm_name', type=str, default=None,
              help="Name of the algorithm to look up.  All matching algo versions will be queried")
@click.option('-C', '--only_columns', multiple=True,
              help="Include only the listed columns in output.")
@click.option('-c', '--append_columns', multiple=True,
              help="Append these columns to those shown by default.")
@click.option('-T', '--transpose', is_flag=True,
              help="Display the result in transpose (helpful to show algorithms with long string values).")
def algorithm_config_get(
        ctx,
        algorithm_config_id,
        algorithm_version_id,
        algorithm_name,
        only_columns,
        append_columns,
        transpose,
):
    algorithm_version_ids = []
    if algorithm_version_id is not None:
        algorithm_version_ids.append([algorithm_version_id, None, None])

    # if requested by name, we'll look up the available version ids and run all of them.
    if algorithm_name is not None:
        algos = asyncio.run(wf.list_algorithms(algorithm_name))
        for algo in algos:
            algorithm_versions = asyncio.run(wf.get_algorithm_versions(algo.id))
            for algorithm_version in algorithm_versions:
                algorithm_version_ids.append([algorithm_version.id, algo.name, algo.id])

    for algorithm_version_info in algorithm_version_ids:
        algorithm_version_id = algorithm_version_info[0]
        algorithm_configs = asyncio.run(wf.get_algorithm_configs(algorithm_version_id=algorithm_version_id))
        _print_algorithm_configs(algorithm_version_info, algorithm_configs, only_columns, append_columns, transpose)

    if algorithm_config_id:
        algorithm_configs = asyncio.run(wf.get_algorithm_configs(algorithm_config_id=algorithm_config_id))
        algorithm_version_info = [algorithm_version_id, None, None]
        _print_algorithm_configs(algorithm_version_info, algorithm_configs, only_columns, append_columns, transpose)


def _print_algorithm_configs(
        algorithm_version_info,
        algorithm_configs,
        only_columns,
        append_columns,
        transpose
):

    algo_version_id, algo_name, algo_id = algorithm_version_info
    click.secho(f"name: {algo_name}", fg='magenta')
    click.secho(f"      algo_id:         {algo_id}", fg='magenta')
    click.secho(f"      algo_version_id: {algo_version_id}", fg='magenta')

    columns = ['name', 'id', 'description', 'created_on']
    if only_columns:
        columns = list(only_columns)
    if append_columns:
        columns = columns + list(append_columns)

    algorithm_configs = tsu.protobuf_to_dict(algorithm_configs[0])
    if 'algorithm_configs' in algorithm_configs:
        algorithm_configs = algorithm_configs['algorithm_configs']
    else:
        algorithm_configs = [algorithm_configs]

    data = []
    for algorithm_config in algorithm_configs:
        data.append(algorithm_config)
    df = pd.DataFrame(data)
    if 'all' not in columns:
        df = df[tsu.match_columns(df.columns, columns)]
    if transpose:
        df = df.T.rename(columns={0: ""})
    df = df.rename(columns={'id': 'algorithm_config_id'})
    tsu.set_pandas_display()
    click.secho(f"algorithm_version_id: {algo_version_id}", fg='cyan')
    click.echo(df)


@config.command('create')
@click.pass_context
@click.option('-iv', '--algorithm_version_id', type=str)
@click.option('-m', '--manifest_yaml', type=str)
@click.option('-nc', '--config_name', type=str)
@click.option('-d', '--config_desc', type=str)
@click.option('-s', '--data_source', type=str)
@click.option('-t', '--data_type', type=str)
@click.option('-p', '--image_processing_spec', type=str, default=None)
@click.option('--dry_run', is_flag=True)
def algorithm_config_create(
        ctx,
        algorithm_version_id,
        manifest_yaml,
        config_name,
        config_desc,
        data_source,
        data_type,
        image_processing_spec=None,
        dry_run=False,
):

    wf.check_environment_complete(raise_on_failure=True)
    input_manifest = None
    with open(manifest_yaml, 'r') as fp:
        input_manifest = yaml.safe_load(fp)

    if not data_source:
        try:
            data_source = input_manifest['inputs'][0]['data_source_name']
        except Exception:
            click.secho("Data source must be provided in manifest or on commandline", fg='red')
            raise

    if not data_type:
        try:
            data_type = input_manifest['inputs'][0]['data_type_name']
        except Exception:
            click.secho("Data Type must be provided in manifest or on command line", fg='red')
            raise

    # image proc spec isn't always required.  if not given, check the manifest.  use it if it's provided.
    if not image_processing_spec:
        image_processing_spec = input_manifest['inputs'][0]['parameters'].get('image_processing_spec', None)
    data_parameters = {}
    if image_processing_spec:
        data_parameters['image_processing_spec'] = image_processing_spec

    click.echo("Using the following information:")
    click.echo(f"--> algorithm_version_id:     {algorithm_version_id}")
    click.echo(f"--> config_name:              {config_name}")
    click.echo(f"--> config_desc:              {config_desc}")
    click.echo(f"--> data_source:              {data_source}")
    click.echo(f"--> data_type:                {data_type}")
    click.echo(f"--> image_processing_spec:    {image_processing_spec}")

    if not dry_run:
        algorithm_config_id = asyncio.run(
            wf.create_algorithm_config(
                algorithm_version_id,
                config_name,
                config_desc,
                data_source,
                data_type,
                data_parameters,
            )
        )
        tsu.echo_highlight_suffix("You're new algorithm_config_id is: ", algorithm_config_id, 'green')


@config.command('deactivate')
@click.pass_context
@click.option('-ic', '--algorithm_config_ids', type=str, multiple=True, required=True,
              help="UUIDs of the algorithm_configs to deactivate")
def algorithm_config_deactivate(
        ctx,
        algorithm_config_ids,
):

    response = asyncio.run(wf.deactivate_algorithm_configs(algorithm_config_ids=algorithm_config_ids))

    click.echo("Deactivation response code: ", nl=False)
    if response:
        click.secho(f" {response} (FAILURE)", fg='red')
    else:
        click.secho(f" {response} (SUCCESS)", fg='green')
