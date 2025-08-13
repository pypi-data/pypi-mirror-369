#!/usr/bin/env python

import click
import asyncio
import pandas as pd
import yaml
import json
import terrascope.cli.lib.utils as tsu
from terrascope.cli.lib.aliased_group import AliasedSuperGroup
import terrascope.cli.lib.workflow as wf
from terrascope.cli.commands.analysis_version import version
from terrascope.cli.commands.analysis_computation import computation
from terrascope.cli.commands.analysis_config import config


@click.command(cls=AliasedSuperGroup, help="'analysis' super-group")
@click.pass_context
def analysis(ctx):
    pass


analysis.add_command(version)
analysis.add_command(computation)
analysis.add_command(config)


@analysis.command('get')
@click.pass_context
@click.option('-iA', '--analysis_id', type=str, default=None)
@click.option('-nA', '--analysis_name', type=str, default=None)
@click.option('-t', '--truncate', type=int, default=36,
              help="Truncate columns to this many chars. Use 0 for no truncation. (a full UUID is 36).")
@click.option('-v', '--verbose', is_flag=True, default=False)
def analysis_get(ctx, analysis_id, analysis_name, truncate=False, verbose=False):

    wf.check_environment_complete(raise_on_failure=True, verbose=verbose)
    analyses = []
    if analysis_id:
        analyses += asyncio.run(wf.get_analyses([analysis_id]))
    if analysis_name:
        analyses += asyncio.run(wf.list_analyses(analysis_name))

    data = []
    for analysis in analyses:
        analysis_dict = tsu.protobuf_to_dict(analysis)
        created_on = analysis_dict.get('created_on', '        ')[:-8]
        data.append([analysis.name, analysis.id, created_on, analysis.author])

    tsu.set_pandas_display()
    df = pd.DataFrame(data=data, columns=['name', 'analysis_id', 'created', 'author'])
    click.echo(df)


@analysis.command('create')
@click.pass_context
@click.option('-nA', '--analysis_name', type=str)
@click.option('-a', '--author', type=str, default='TERRASCOPE_AUTHOR')
@click.option('-d', '--display_name', type=str)
@click.option('--dry_run', is_flag=True, default=False)
def analysis_create(
        ctx,
        analysis_name,
        author,
        display_name,
        dry_run,
):
    author = tsu.get_author(author, raise_on_failure=True)
    click.echo("Using the following information:")
    click.echo(f"--> analysis_name: {analysis_name}")
    click.echo(f"--> author:        {author}")
    click.echo(f"--> display_name:  {display_name}")

    # create the manifest
    if not dry_run:
        analysis_id = asyncio.run(wf.create_analysis(
            analysis_name,
            author,
            display_name,
        ))
        tsu.echo_highlight_suffix("You're new analysis_id is: ", analysis_id, 'green')


@analysis.command('register')
@click.pass_context
@click.option('-nA', '--analysis_name', type=str)
@click.option('-iv', '--algorithm_version_id', type=str)
@click.option('-a', '--author', type=str, default='TERRASCOPE_AUTHOR')
@click.option('-D', '--description', type=str)
@click.option('-nC', '--analysis_config_name', type=str)
@click.option('-ic', '--algorithm_config_id', type=str)
@click.option('-V', '--version', type=str)
@click.option('-T', '--tags', type=str, multiple=True)
@click.option('--dry_run', is_flag=True, default=False)
def analysis_register(
        ctx,
        analysis_name,
        algorithm_version_id,
        author,
        description,
        analysis_config_name,
        algorithm_config_id,
        version,
        tags,
        dry_run,
):

    author = tsu.get_author(author, raise_on_failure=True)
    click.echo("Using the following information:")
    click.echo(f"--> analysis_name: {analysis_name}")
    click.echo(f"--> author:        {author}")

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
                                           description,
                                           version,
                                           tags)
    # create the analysis version
    if not dry_run:
        analysis_version_id = asyncio.run(wf.create_analysis_version(
            analysis_id,
            manifest,
        ))

        tsu.echo_highlight_suffix("You're new analysis_version_id is: ", analysis_version_id, 'green')

    # create a config
    if analysis_config_name is not None:

        analysis_config_desc = f"The {analysis_config_name}"  # :)
        algo_config_name = analysis_config_name
        click.echo("Using the following information:")
        click.echo(f"--> analysis_version_id:      {analysis_version_id}")
        click.echo(f"--> algorithm_config_id:      {algorithm_config_id}")
        click.echo(f"--> analysis_config_name:     {analysis_config_name}")
        click.echo(f"--> analysis_config_desc:     {analysis_config_desc}")
        click.echo(f"--> algo_config_name:         {algo_config_name}")

        if not dry_run:
            analysis_config_id = asyncio.run(
                wf.create_analysis_config(
                    analysis_version_id,
                    algorithm_config_id,
                    analysis_config_name,
                    analysis_config_desc,
                    algo_config_name,
                )
            )
            tsu.echo_highlight_suffix("You're new analysis_config_id is: ", analysis_config_id, 'green')


@analysis.command('update')
@click.pass_context
@click.option('-iA', '--analysis_id', type=str, help="Analysis ID to update")
@click.option('-iv', '--algorithm_version_id', type=str, help='Algorithm version ID to use in analysis')
@click.option('-ic', '--algorithm_config_id', type=str, help='Algorithm config ID to use in analysis config')
@click.option('-m', '--manifest_yaml', type=str)
@click.option('-om', '--output_manifest', type=str, help="Can be json or yaml file")
@click.option('-nC', '--analysis_config_name', type=str, default=None,
              help="Name used in TS (default to 'display_name' from algo manifest)")
@click.option('-dC', '--analysis_config_desc', type=str, default=None,
              help="Description used in TS (default to 'description' from algo manifest)")
@click.option('-dA', '--analysis_description', default=None, type=str,
              help="Description which appears in TS (default to 'description' from algo manifest).")
@click.option('--dry_run', is_flag=True, default=False)
@click.option('-V', '--version', type=str, default=None)
@click.option('-v', '--verbose', is_flag=True, default=False)
def analysis_update(
        ctx,
        analysis_id,
        algorithm_version_id,
        algorithm_config_id,
        manifest_yaml,
        output_manifest=None,
        algorithm_config_name=None,
        analysis_config_name=None,
        analysis_config_desc=None,
        analysis_name=None,
        analysis_description=None,
        dry_run=False,
        version=None,
        verbose=False,
):

    # create the manifest
    input_manifest = None
    with open(manifest_yaml, 'r') as fp:
        input_manifest = yaml.safe_load(fp)

    command_line_version = version

    ############################
    # analysis version
    ############################

    analysis = asyncio.run(wf.get_analyses([analysis_id]))[0]

    if not analysis_description:
        analysis_description = input_manifest['metadata']['description']
    tags = input_manifest['metadata']['tags']

    analysis_version = version  # default
    if command_line_version in ['patch', 'minor', 'major']:
        level = command_line_version
        current_analysis_version = asyncio.run(wf.get_current_analysis_version(analysis_id=analysis_id))
        analysis_version = tsu.increment_version(current_analysis_version, level=level)
        click.echo(f"The current analyais version is: {current_analysis_version}.")
        click.echo(f"Auto-incrementing at {level}-level to: {analysis_version}")

    # create the analysis
    if not dry_run:
        tsu.echo_highlight_suffix("Updating existing analysis_id: ", analysis_id, 'green')

        # create a manifest
        manifest = wf.create_analysis_manifest(analysis.name,
                                               algorithm_version_id,
                                               analysis_description,
                                               analysis_version,
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
        analysis_config_name = analysis.name
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


@analysis.command('display')
@click.pass_context
@click.option('-iA', '--analysis_id', type=str)
@click.option('-nA', '--analysis_name', type=str)
@click.option('-d1', '--date_min', type=str,
              default=(pd.to_datetime("now") - pd.to_timedelta(24, unit='h')).strftime("%Y-%m-%d"))
@click.option('-d2', '--date_max', type=str)
def analysis_display(ctx, analysis_id, analysis_name, date_min=None, date_max=None):

    wf.check_environment_complete(raise_on_failure=True)

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

        click.secho(f"name: {name}   analysis_id: {analysis_id}   author: {author}", fg='cyan')

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

            ###################################################
            # get the analysis_computations_ids
            #
            # If you're thinking this whole block should be indented to query for *this* analysis_config_id
            # I agree.  But, we don't actually have the config ID returned with the computation info
            # So, there isn't a way I can find to determine which analysis_config_id was used for each
            # computation.  We'll just show all that match the date range.
            ###################################################
            if date_min is not None:
                date_min = pd.to_datetime(date_min)
            if date_max is not None:
                date_max = pd.to_datetime(date_max)
            analysis_computation_infos = asyncio.run(wf.get_analysis_computation_info())

            for analysis_computation_info in analysis_computation_infos:
                info = tsu.protobuf_to_dict(analysis_computation_info)
                info['analysis_computation_id'] = info['id']

                submitted_on = info['submitted_on'][:19]
                if date_min is not None and (submitted_on < date_min.isoformat()):
                    continue
                if date_max is not None and (submitted_on > date_max.isoformat()):
                    continue

                del info['id']
                # if they asked for a specific one, just print that.  otherwise print all.
                if analysis_id == info['analysis_id']:
                    for i, (k, v) in enumerate(sorted(info.items())):
                        msg = f"{indent}{indent}{indent}--> {k:24s} {v}"
                        if i == 0:
                            click.secho(msg, fg='red')
                        else:
                            click.echo(f"{indent}{msg}")
