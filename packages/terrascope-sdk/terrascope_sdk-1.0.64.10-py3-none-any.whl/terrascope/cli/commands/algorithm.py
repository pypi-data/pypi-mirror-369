#!/usr/bin/env python

import click
import asyncio
import pandas as pd
import yaml
import json
import terrascope.cli.lib.utils as tsu
from terrascope.cli.lib.aliased_group import AliasedSuperGroup
import terrascope.cli.lib.workflow as wf
from terrascope.cli.commands.algorithm_version import version
from terrascope.cli.commands.algorithm_computation import computation
from terrascope.cli.commands.algorithm_config import config


@click.command(cls=AliasedSuperGroup, help="'algorithm' super-group")
@click.pass_context
def algorithm(ctx):
    pass


algorithm.add_command(version)
algorithm.add_command(computation)
algorithm.add_command(config)


@algorithm.command('get', help="Get algorithm info")
@click.pass_context
@click.option('-ia', '--algorithm_id', type=str, default=None)
@click.option('-na', '--algorithm_name', type=str, default=None)
@click.option('-t', '--truncate', type=int, default=36,
              help="Truncate columns to this many chars. Use 0 for no truncation. (a full UUID is 36).")
@click.option('-v', '--verbose', is_flag=True, default=False)
def algorithm_get(ctx, algorithm_id=None, algorithm_name=None, truncate=0, verbose=False):

    wf.check_environment_complete(raise_on_failure=True, verbose=verbose)
    algos = []
    if algorithm_id:
        algos += asyncio.run(wf.get_algorithms(algorithm_ids=[algorithm_id]))
    if algorithm_name:
        algos += asyncio.run(wf.list_algorithms(algorithm_name=algorithm_name))

    data = []
    for algo in algos:
        row = [algo.name, algo.id, algo.author]
        if truncate:
            row = [v[:truncate] for v in row]
        data.append(row)

    df = pd.DataFrame(data=data, columns=['name', 'algorithm_id', 'author'])
    tsu.set_pandas_display()
    click.echo(df)


@algorithm.command('create', help="Create an algorithm object (no manifest)")
@click.pass_context
@click.option('-na', '--algorithm_name', type=str)
@click.option('-a', '--author', type=str, default='TERRASCOPE_AUTHOR')
@click.option('-dn', '--display_name', type=str)
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.option('--dry_run', is_flag=True, default=False)
def algorithm_create(
        ctx,
        algorithm_name,
        author,
        display_name,
        verbose=False,
        dry_run=False,
):

    wf.check_environment_complete(raise_on_failure=True, verbose=verbose)

    author = tsu.get_author(author, raise_on_failure=True)
    click.echo("Using the following information:")
    click.echo(f"--> name:         {algorithm_name}")
    click.echo(f"--> author:       {author}")
    click.echo(f"--> display_name: {display_name}")

    # create the manifest
    if not dry_run:
        algorithm_id = asyncio.run(wf.create_algorithm(
            algorithm_name,
            author,
            display_name,
        ))
        tsu.echo_highlight_suffix("You're new algorithm_id is: ", algorithm_id, 'green')


@algorithm.command('register', help="Create an algorithm, and register it. (with manifest)")
@click.pass_context
@click.option('-m', '--manifest_yaml', type=str)
@click.option('-om', '--output_manifest', type=str, help="Can be json or yaml file")
@click.option('-na', '--algorithm_name', type=str)
@click.option('-a', '--author', type=str, default='TERRASCOPE_AUTHOR')
@click.option('-dn', '--display_name', type=str)
@click.option('-d', '--docker_version_hash', type=str)
@click.option('-pv', '--value_price', default=wf.VALUE_PRICE_DEFAULT, type=float)
@click.option('-pe', '--execution_price', default=wf.EXECUTION_PRICE_DEFAULT, type=float)
@click.option('-nc', '--config_name', default=None, type=str,
              help="Specify this to create an initial algorithm config.")
@click.option('--dry_run', is_flag=True, default=False)
@click.option('-V', '--version', type=str, default=None)
@click.option('-v', '--verbose', is_flag=True, default=False)
def algorithm_register(
        ctx,
        manifest_yaml,
        output_manifest=None,
        algorithm_name=None,
        author=None,
        display_name=None,
        docker_version_hash=None,
        value_price=wf.VALUE_PRICE_DEFAULT,
        execution_price=wf.EXECUTION_PRICE_DEFAULT,
        config_name=None,
        dry_run=False,
        version=None,
        verbose=False,
):

    wf.check_environment_complete(raise_on_failure=True, verbose=verbose)
    # create the manifest
    input_manifest = None
    with open(manifest_yaml, 'r') as fp:
        input_manifest = yaml.safe_load(fp)
    algorithm_name = tsu.override_manifest_param('name', algorithm_name, input_manifest, do_overwrite=True)
    display_name = tsu.override_manifest_param('display_name', display_name, input_manifest, do_overwrite=True)
    author = tsu.get_author(author, raise_on_failure=True)
    # if the author is in the manifest, overwrite it with the command line / env-var value.
    # This is only done in case the user wants to write the manifest to a file,
    # ... we want that file to contain what was actually used.
    if 'author' in input_manifest:
        input_manifest['author'] = author
    new_version = input_manifest['metadata']['version']
    if version:
        new_version = tsu.set_version(version, input_manifest, do_overwrite=True)

    visualizer_config_names = input_manifest.get('visualizer_config_names', None)
    image = wf.update_manifest_docker_hash(input_manifest, docker_version_hash)
    manifest = wf.create_algorithm_manifest(input_manifest)

    click.echo("Using the following information:")
    click.echo(f"--> name:         {algorithm_name}")
    click.echo(f"--> version:      {new_version}")
    click.echo(f"--> author:       {author}")
    click.echo(f"--> display_name: {display_name}")
    click.echo(f"--> image:        {image}")
    click.echo(f"--> prices:       {value_price} / {execution_price}")
    click.echo(f"--> vis-names:    {visualizer_config_names}")

    # create the manifest
    if not dry_run:
        algorithm_id, algorithm_version_id = asyncio.run(wf.new_algorithm(
            algorithm_name,
            author,
            display_name,
            manifest,
            value_price=value_price,
            execution_price=execution_price,
            visualizer_config_names=visualizer_config_names,
        ))
        tsu.echo_highlight_suffix("You're new algorithm_id is: ", algorithm_id, 'green')
        tsu.echo_highlight_suffix("You're new algorithm_version_id is: ", algorithm_version_id, 'green')

        if config_name:
            algorithm_config_id = create_config(algorithm_version_id, config_name, input_manifest)
            tsu.echo_highlight_suffix("You're new algorithm_config_id is: ", algorithm_config_id, 'green')

    if output_manifest:
        with open(output_manifest, 'w') as fp:
            if output_manifest.endswith('json'):
                json.dump(input_manifest, fp, indent=4)
            else:
                yaml.dump(input_manifest, fp)


@algorithm.command('update', help="Update an existing algorithm with manifest or pricing.")
@click.pass_context
@click.option('-m', '--manifest_yaml', type=str, required=True)
@click.option('-ia', '--algorithm_id', type=str, required=True)
@click.option('-om', '--output_manifest', type=str)
@click.option('-d', '--docker_version_hash', type=str, default=None)
@click.option('-pv', '--value_price', default=wf.VALUE_PRICE_DEFAULT, type=float)
@click.option('-pe', '--execution_price', default=wf.EXECUTION_PRICE_DEFAULT, type=float)
@click.option('--dry_run', is_flag=True, default=False)
@click.option('-nc', '--config_name', default=None, type=str,
              help="Specify this to create an initial algorithm config.")
@click.option('-V', '--version', type=str, default=None)
@click.option('-v', '--verbose', is_flag=True, default=False)
def algorithm_update(
        ctx,
        manifest_yaml,
        algorithm_id,
        output_manifest=None,
        docker_version_hash=None,
        value_price=wf.VALUE_PRICE_DEFAULT,
        execution_price=wf.EXECUTION_PRICE_DEFAULT,
        config_name=None,
        dry_run=False,
        version=None,
        verbose=False,
):

    wf.check_environment_complete(raise_on_failure=True, verbose=verbose)
    command_line_version = version

    # create the manifest
    input_manifest = None
    with open(manifest_yaml, 'r') as fp:
        input_manifest = yaml.safe_load(fp)
    algorithm_version = input_manifest['metadata']['version']
    visualizer_config_names = input_manifest.get('visualizer_config_names', None)
    if command_line_version:
        if command_line_version in ['patch', 'minor', 'major']:
            level = command_line_version
            current_algorithm_version = asyncio.run(wf.get_current_algorithm_version(algorithm_id=algorithm_id))
            new_algorithm_version = tsu.increment_version(current_algorithm_version, level=level)
            click.echo(f"The current algorithm version is: {current_algorithm_version}.")
            click.echo(f"Auto-incrementing at {level}-level to: {new_algorithm_version}")
        else:
            new_algorithm_version = command_line_version
        algorithm_version = tsu.set_version(new_algorithm_version, input_manifest, do_overwrite=True)

    image = wf.update_manifest_docker_hash(input_manifest, docker_version_hash)
    manifest = wf.create_algorithm_manifest(input_manifest)

    click.echo("Using the following information:")
    click.echo(f"--> algorithm_id:  {algorithm_id}")
    click.echo(f"--> image:         {image}")
    click.echo(f"--> prices:        {value_price} / {execution_price}")
    click.echo(f"--> version:       {algorithm_version}")
    click.echo(f"--> viz-names:     {visualizer_config_names}")

    # create the manifest
    if not dry_run:
        algorithm_version_id = asyncio.run(wf.update_algorithm(
            algorithm_id,
            manifest,
            value_price=value_price,
            execution_price=execution_price,
            visualizer_config_names=visualizer_config_names,
        ))
        tsu.echo_highlight_suffix("Your updated algorithm_version_id is: ", algorithm_version_id, 'green')

        if config_name:
            algorithm_config_id = create_config(algorithm_version_id, config_name, input_manifest)
            tsu.echo_highlight_suffix("You're new algorithm_config_id is: ", algorithm_config_id, 'green')

    if output_manifest:
        with open(output_manifest, 'w') as fp:
            if output_manifest.endswith('json'):
                json.dump(input_manifest, fp, indent=4)
            else:
                yaml.dump(input_manifest, fp)


def create_config(algorithm_version_id, config_name, input_manifest):

    # use a canned description as this is the first config for this algo version
    config_desc = f"Initial algorithm config for {config_name}"

    # if a config_name is provided, then we'll create an initial config
    # Get the necessary params from the manifest.
    try:
        data_source = input_manifest['inputs'][0]['data_source_name']
    except Exception:
        click.secho("Data source must be provided in manifest", fg='red')
        raise

    try:
        data_type = input_manifest['inputs'][0]['data_type_name']
    except Exception:
        click.secho("Data Type must be provided in manifest", fg='red')
        raise

    image_processing_spec = None
    if 'parameters' in input_manifest['inputs'][0]:
        image_processing_spec = input_manifest['inputs'][0]['parameters'].get('image_processing_spec', None)
    data_parameters = {}
    if image_processing_spec:
        data_parameters['image_processing_spec'] = image_processing_spec

    algorithm_config_id = asyncio.run(
        wf.create_algorithm_config(
            algorithm_version_id,
            config_name,
            config_desc,
            tsu.FakeDataSource(data_source),
            data_type,
            data_parameters,
        )
    )
    return algorithm_config_id
