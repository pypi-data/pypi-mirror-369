#!/usr/bin/env python

import click
import asyncio
import yaml
import json
import terrascope.cli.lib.workflow as wf
import terrascope.cli.lib.utils as tsu
from terrascope.cli.lib.aliased_group import AliasedGroup


@click.command(cls=AliasedGroup, help="'tasks' command group")
@click.pass_context
def tasks(ctx):
    pass


@tasks.command('initialize')
@click.pass_context
@click.option('-m', '--manifest_yaml', type=str)
@click.option('-om', '--output_manifest', type=str, help="Can be json or yaml file")
@click.option('-na', '--algorithm_name', type=str)
@click.option('-a', '--author', type=str, default='TERRASCOPE_AUTHOR')
@click.option('-N', '--display_name', type=str)
@click.option('-d', '--docker_version_hash', type=str)
@click.option('-pv', '--value_price', default=wf.VALUE_PRICE_DEFAULT, type=float)
@click.option('-pe', '--execution_price', default=wf.EXECUTION_PRICE_DEFAULT, type=float)
@click.option('-nc', '--algorithm_config_name', default=None, type=str)
@click.option('-nC', '--analysis_config_name', type=str, default=None,
              help="Name used in TS (default to 'display_name' from algo manifest)")
@click.option('-dC', '--analysis_config_desc', type=str, default=None,
              help="Description used in TS (default to 'description' from algo manifest)")
@click.option('-nA', '--analysis_name', default=None, type=str,
              help="Analysis name (defaults to algorithm_name if not provided).")
@click.option('-dA', '--analysis_description', default=None, type=str,
              help="Analysis description (default to 'description' from algo manifest).")
@click.option('--dry_run', is_flag=True, default=False)
@click.option('-V', '--version', type=str, default=None)
@click.option('-v', '--verbose', is_flag=True, default=False)
def tasks_initialize(
        ctx,
        manifest_yaml,
        output_manifest=None,
        algorithm_name=None,
        author=None,
        display_name=None,
        docker_version_hash=None,
        value_price=wf.VALUE_PRICE_DEFAULT,
        execution_price=wf.EXECUTION_PRICE_DEFAULT,
        algorithm_config_name=None,
        analysis_config_name=None,
        analysis_config_desc=None,
        analysis_name=None,
        analysis_description=None,
        dry_run=False,
        version=None,
        verbose=False,
):

    wf.check_environment_complete(raise_on_failure=True)

    # create the manifest
    input_manifest = None
    with open(manifest_yaml, 'r') as fp:
        input_manifest = yaml.safe_load(fp)
    algorithm_name = tsu.override_manifest_param('name', algorithm_name, input_manifest, do_overwrite=True)

    display_name = tsu.override_manifest_param('display_name', display_name, input_manifest, do_overwrite=True)
    author = tsu.get_author(author, raise_on_failure=True)
    visualizer_config_names = input_manifest.get('visualizer_config_names', None)

    # if the author is in the manifest, overwrite it with the command line / env-var value.
    # This is only done in case the user wants to write the manifest to a file,
    # ... we want that file to contain what was actually used.
    if 'author' in input_manifest:
        input_manifest['author'] = author

    image = wf.update_manifest_docker_hash(input_manifest, docker_version_hash)
    manifest = wf.create_algorithm_manifest(input_manifest)

    click.echo("Using the following information:")
    click.echo(f"--> name:         {algorithm_name}")
    click.echo(f"--> author:       {author}")
    click.echo(f"--> display_name: {display_name}")
    click.echo(f"--> image:        {image}")
    click.echo(f"--> prices:       {value_price} / {execution_price}")
    click.echo(f"--> viz-names:    {visualizer_config_names}")

    ############################
    # algorithm and algo version
    ############################
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

    ############################
    # algo config
    ############################
    if not dry_run:

        if not algorithm_config_name:
            algorithm_config_name = algorithm_name
        config_desc = f"Initial algorithm config for {algorithm_config_name}"

        # Get the necessary params from the manifest.
        inputs = input_manifest['inputs'][0]

        try:
            data_type = inputs['data_type_name']
        except Exception:
            click.secho("Data Type must be provided in manifest", fg='red')
            raise

        # Try to find the data source
        data_source = inputs.get('data_source_name', None)
        if data_source is None:
            data_source = inputs.get('data_source_id', None)
        if data_source is None:
            data_source = inputs.get('data_source_ids', [None])[0]

        other_inputs = {}
        for key in ['min_count', 'max_count', 'cloud_paths']:
            if key in inputs:
                other_inputs[key] = inputs[key]

        image_processing_spec = None
        if 'parameters' in inputs:
            image_processing_spec = inputs['parameters'].get('image_processing_spec', None)
        data_parameters = {}
        if image_processing_spec:
            data_parameters['image_processing_spec'] = image_processing_spec

        algorithm_config_id = asyncio.run(
            wf.create_algorithm_config(
                algorithm_version_id,
                algorithm_config_name,
                config_desc,
                tsu.FakeDataSource(data_source),
                data_type,
                data_parameters,
                visualizer_config_names=visualizer_config_names,
                **other_inputs
            )
        )
        tsu.echo_highlight_suffix("You're new algorithm_config_id is: ", algorithm_config_id, 'green')

    ############################
    # analysis and analysis version
    ############################

    if not analysis_name:
        analysis_name = algorithm_name
    if not analysis_description:
        analysis_description = input_manifest['metadata']['description']
    tags = input_manifest['metadata']['tags']

    # create the analysis
    if not dry_run:
        analysis_id = asyncio.run(wf.create_analysis(
            analysis_name,
            author,
        ))
        tsu.echo_highlight_suffix("You're new analysis_id is: ", analysis_id, 'green')

        # create a manifest
        manifest = wf.create_analysis_manifest(analysis_name,
                                               algorithm_version_id,
                                               analysis_description,
                                               tags)
        # create the analysis version
        analysis_version_id = asyncio.run(wf.create_analysis_version(
            analysis_id,
            manifest,
        ))

        tsu.echo_highlight_suffix("You're new analysis_version_id is: ", analysis_version_id, 'green')

    ############################
    # analysis config
    ############################
    if not analysis_config_name:
        analysis_config_name = analysis_name
    if not analysis_config_desc:
        analysis_config_desc = analysis_description

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

    if output_manifest:
        with open(output_manifest, 'w') as fp:
            if output_manifest.endswith('json'):
                json.dump(input_manifest, fp, indent=4)
            else:
                yaml.dump(input_manifest, fp)


@tasks.command('update')
@click.pass_context
@click.option('-ia', '--algorithm_id', type=str, help="Algorithm ID to update")
@click.option('-iA', '--analysis_id', type=str, help="Analysis ID to update")
@click.option('-m', '--manifest_yaml', type=str)
@click.option('-om', '--output_manifest', type=str, help="Can be json or yaml file")
@click.option('-na', '--algorithm_name', type=str)
@click.option('-a', '--author', type=str, default='TERRASCOPE_AUTHOR')
@click.option('-N', '--display_name', type=str)
@click.option('-d', '--docker_version_hash', type=str)
@click.option('-pv', '--value_price', default=wf.VALUE_PRICE_DEFAULT, type=float)
@click.option('-pe', '--execution_price', default=wf.EXECUTION_PRICE_DEFAULT, type=float)
@click.option('-nc', '--algorithm_config_name', type=str, default=None)
@click.option('-nC', '--analysis_config_name', type=str, default=None,
              help="Name used in TS (default to 'display_name' from algo manifest)")
@click.option('-dC', '--analysis_config_desc', type=str, default=None,
              help="Description used in TS (default to 'description' from algo manifest)")
@click.option('-nA', '--analysis_name', default=None, type=str,
              help="Analysis name (defaults to algorithm_name if not provided).")
@click.option('-dA', '--analysis_description', default=None, type=str,
              help="Description which appears in TS (default to 'description' from algo manifest).")
@click.option('--dry_run', is_flag=True, default=False)
@click.option('-v', '--verbose', is_flag=True, default=False)
def tasks_update(
        ctx,
        algorithm_id,
        analysis_id,
        manifest_yaml,
        output_manifest=None,
        algorithm_name=None,
        author=None,
        display_name=None,
        docker_version_hash=None,
        value_price=wf.VALUE_PRICE_DEFAULT,
        execution_price=wf.EXECUTION_PRICE_DEFAULT,
        algorithm_config_name=None,
        analysis_config_name=None,
        analysis_config_desc=None,
        analysis_name=None,
        analysis_description=None,
        dry_run=False,
        verbose=False,
):

    wf.check_environment_complete(raise_on_failure=True)

    # create the manifest
    input_manifest = None
    with open(manifest_yaml, 'r') as fp:
        input_manifest = yaml.safe_load(fp)
    algorithm_name = tsu.override_manifest_param('name', algorithm_name, input_manifest, do_overwrite=True)

    if algorithm_config_name is None:
        algorithm_config_name = algorithm_name

    display_name = tsu.override_manifest_param('display_name', display_name, input_manifest, do_overwrite=True)
    author = tsu.get_author(author, raise_on_failure=True)
    visualizer_config_names = input_manifest.get('visualizer_config_names', None)

    # if the author is in the manifest, overwrite it with the command line / env-var value.
    # This is only done in case the user wants to write the manifest to a file,
    # ... we want that file to contain what was actually used.
    if 'author' in input_manifest:
        input_manifest['author'] = author

    image = wf.update_manifest_docker_hash(input_manifest, docker_version_hash)
    manifest = wf.create_algorithm_manifest(input_manifest)

    click.echo("Using the following information:")
    click.echo(f"--> algorithm_id: {algorithm_id}")
    click.echo(f"--> analysis_id:  {analysis_id}")
    click.echo(f"--> image:        {image}")
    click.echo(f"--> prices:       {value_price} / {execution_price}")
    click.echo(f"--> viz-names:    {visualizer_config_names}")

    ############################
    # algorithm and algo version
    ############################
    if not dry_run:

        tsu.echo_highlight_suffix("Updating existing algorithm_id: ", algorithm_id, 'green')

        algorithm_version_id = asyncio.run(wf.update_algorithm(
            algorithm_id,
            manifest,
            value_price=value_price,
            execution_price=execution_price,
            visualizer_config_names=visualizer_config_names,
        ))
        tsu.echo_highlight_suffix("Your updated algorithm_version_id is: ", algorithm_version_id, 'green')

    ############################
    # algo config
    ############################
    if not dry_run:

        if not algorithm_config_name:
            algorithm_config_name = algorithm_name
        config_desc = f"Initial algorithm config for {algorithm_config_name}"

        # Get the necessary params from the manifest.
        inputs = input_manifest['inputs'][0]

        try:
            data_type = inputs['data_type_name']
        except Exception:
            click.secho("Data Type must be provided in manifest", fg='red')
            raise

        data_source = inputs.get('data_source_name', None)
        if data_source is None:
            data_source = inputs.get('data_source_ids', [None])[0]

        other_inputs = {}
        for key in ['min_count', 'max_count', 'cloud_paths']:
            if key in inputs:
                other_inputs[key] = inputs[key]

        image_processing_spec = None
        if 'parameters' in inputs:
            image_processing_spec = inputs['parameters'].get('image_processing_spec', None)
        data_parameters = {}
        if image_processing_spec:
            data_parameters['image_processing_spec'] = image_processing_spec

        algorithm_config_id = asyncio.run(
            wf.create_algorithm_config(
                algorithm_version_id,
                algorithm_config_name,
                config_desc,
                tsu.FakeDataSource(data_source),
                data_type,
                data_parameters,
                visualizer_config_names=visualizer_config_names,
                **other_inputs
            )
        )
        tsu.echo_highlight_suffix("You're new algorithm_config_id is: ", algorithm_config_id, 'green')

    ############################
    # analysis version
    ############################

    if not analysis_name:
        analysis_name = algorithm_name
    if not analysis_description:
        analysis_description = input_manifest['metadata']['description']
    tags = input_manifest['metadata']['tags']

    # create the analysis
    if not dry_run:
        tsu.echo_highlight_suffix("Updating existing analysis_id: ", analysis_id, 'green')

        # create a manifest
        manifest = wf.create_analysis_manifest(analysis_name,
                                               algorithm_version_id,
                                               analysis_description,
                                               tags)
        # create the analysis version
        analysis_version_id = asyncio.run(wf.create_analysis_version(
            analysis_id,
            manifest,
        ))

        tsu.echo_highlight_suffix("You're new analysis_version_id is: ", analysis_version_id, 'green')

    ############################
    # analysis config
    ############################
    if not analysis_config_name:
        analysis_config_name = analysis_name
    if not analysis_config_desc:
        analysis_config_desc = analysis_description

    click.echo("Using the following information:")
    click.echo(f"--> analysis_version_id:      {analysis_version_id}")
    click.echo(f"--> algorithm_config_id:      {algorithm_config_id}")
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

    if output_manifest:
        with open(output_manifest, 'w') as fp:
            if output_manifest.endswith('json'):
                json.dump(input_manifest, fp, indent=4)
            else:
                yaml.dump(input_manifest, fp)


@tasks.command('idtrace')
@click.pass_context
@click.option('-iA', '--analysis_id', type=str, help="Analysis ID to trace")
@click.option('-iV', '--analysis_version_id', type=str, help="Analysis version ID to trace")
@click.option('-nA', '--analysis_name', default=None, type=str,
              help="Analysis name (defaults to algorithm_name if not provided).")
@click.option('--dry_run', is_flag=True, default=False)
@click.option('-v', '--verbose', is_flag=True, default=False)
def tasks_idtrace(
        ctx,
        analysis_id,
        analysis_version_id,
        analysis_name=None,
        dry_run=False,
        verbose=False,
):

    wf.check_environment_complete(raise_on_failure=True)

    # if they provide the analysis_version_id, look up the analysis_id and go from there.
    if analysis_version_id and not analysis_id and not analysis_name:
        analysis_version = asyncio.run(wf.get_analysis_versions(analysis_version_id=analysis_version_id))[0]
        analysis_version_dict = tsu.protobuf_to_dict(analysis_version)
        analysis_id = analysis_version_dict.get('analysis.id', None)

    ###############################################
    # ana id - get versions, then configs
    # If they give us a uuid, use it.  Otherwise, assume it's a name and look it up.
    if analysis_id:
        analyses = asyncio.run(wf.get_analyses([analysis_id]))
    if analysis_name:
        analyses = asyncio.run(wf.list_analyses(analysis_name))
    analysis_ids = [[analysis.id, analysis.name, analysis.author] for analysis in analyses]

    click.secho(f"input analysis_id:   {analysis_id}", fg='cyan')
    click.secho(f"input analysis_name: {analysis_name}", fg='cyan')
    indent = '  '
    for analysis_id, name, author in analysis_ids:

        click.secho("{:30s}  {:36s}  {:30.30s}".format("name", "analysis_id", "author"), fg='cyan')
        click.echo(f"{name:<30s}  {analysis_id:36s}  {author:30.30s}")

        ###################################################
        # get the analysis_version_id
        analysis_versions = asyncio.run(wf.get_analysis_versions(analysis_id=analysis_id))

        for analysis_version in analysis_versions:
            analysis_version_dict = tsu.protobuf_to_dict(analysis_version)

            analysis_version_dict['created_on'] = analysis_version_dict['created_on'][:-8]
            columns = ['analysis_version_id', 'created_on', 'analysis.name']
            click.secho(f"{indent}" + "{:36s} {:20s} {:20s}".format(*columns), fg='yellow')
            columns[0] = 'id'
            click.echo(f"{indent}" + "{:36s} {:20s} {:20s}".format(*[analysis_version_dict[c] for c in columns]))

            # if the use provided an analysis_version_id, only show that one
            if analysis_version_id and analysis_version_dict['id'] != analysis_version_id:
                continue

            analysis_version_detail = asyncio.run(wf.get_analysis_versions(analysis_version_id=analysis_version_dict['id']))[0]
            analysis_version_detail_dict = tsu.protobuf_to_dict(analysis_version_detail)
            algorithm_versions = analysis_version_detail_dict.get('algorithm_versions', None)
            for algorithm_version in algorithm_versions:
                algorithm_id = algorithm_version.get('algorithm', {}).get('id', None)
                algorithm_name = algorithm_version.get('algorithm', {}).get('name', None)
                click.secho(f"{indent}" + "{:26s}".format("--> algorithm_id: "), fg='magenta', nl=False)
                click.echo(f"{algorithm_id} ({algorithm_name})")
                algorithm_version_id = algorithm_version.get('id', None)
                version = algorithm_version.get('version', None)
                click.secho(f"{indent}" + "{:26s}".format("--> algorithm_version_id: "), fg='magenta', nl=False)
                click.echo(f"{algorithm_version_id} ({version})")

            ###################################################
            # get the analysis_config_id
            analysis_configs = asyncio.run(wf.get_analysis_configs(analysis_version_id=analysis_version_dict['id']))

            for analysis_config in analysis_configs:
                ac_dict = tsu.protobuf_to_dict(analysis_config)
                # analysis_config_id = ac_dict['id']
                ac_dict['created_on'] = ac_dict['created_on'][:-8]
                columns = ['analysis_config_id', 'created_on', 'name']
                click.secho(f"{indent}{indent}" + "{:36s} {:28s} {:20s}".format(*columns), fg='yellow')
                columns[0] = 'id'
                click.echo(f"{indent}{indent}" + "{:36s} {:28s} ".format(*[ac_dict[c] for c in columns[:2]]), nl=False)
                click.secho("{:20s}".format(ac_dict['name']), fg='magenta')
                for node in ac_dict.get('algorithm_config_nodes', []):
                    algorithm_config_id = node['algorithm_config_id']
                    click.secho(f"{indent}{indent}" + "{:26s}".format("--> algorithm_config_id: "),
                                fg='magenta', nl=False)
                    click.echo(f"{algorithm_config_id} ({node['name']})")


tasks.add_command(tasks_update)
tasks.add_command(tasks_initialize)
tasks.add_command(tasks_idtrace)
