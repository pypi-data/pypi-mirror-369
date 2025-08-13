#!/usr/bin/env python

import click
import asyncio
import uuid
import terrascope.cli.lib.workflow as wf
import terrascope.cli.lib.utils as tsu
from terrascope.cli.lib.aliased_group import AliasedGroup


@click.command(cls=AliasedGroup, help="'visualization' command group")
@click.pass_context
def visualization(ctx):
    pass


@visualization.command('get')
@click.pass_context
@click.option('-nz', '--visualizer_config_name', type=str)
@click.option('-v', '--verbose', is_flag=True)
def visualization_get(ctx, visualizer_config_name, verbose):

    visualizer_config_id = str(uuid.uuid5(uuid.NAMESPACE_OID, visualizer_config_name))

    if verbose:
        pass
    click.secho("WARNING: This is a convenience function which computes the ID as ", fg='red')
    click.secho("         uuid.uuid5(visualizer_config_name).  If you misspelled the name, ", fg='red')
    click.secho("         then the ID will not actually exist in the system.", fg='red')
    tsu.echo_highlight_suffix(f"visualizer_config_id:  '{visualizer_config_name}' --> ",
                              visualizer_config_id, 'green')


@visualization.command('create')
@click.option('-nz', '--visualizer_config_names', multiple=True, type=str)
@click.option('-iv', '--algorithm_version_id', type=str)
@click.option('-v', '--verbose', is_flag=True)
@click.pass_context
def visualization_create(ctx, visualizer_config_names, algorithm_version_id, verbose=False):

    visualizer_config_ids = asyncio.run(
        wf.create_visualizer_config_algo(visualizer_config_names, algorithm_version_id)
    )
    tsu.echo_highlight_suffix("Your new visualizer_config_id is: ", visualizer_config_ids, 'green')
