#!/usr/bin/env python

import click
import asyncio
import os
import terrascope.cli.lib.utils as tsu
from terrascope.cli.lib.aliased_group import AliasedGroup
import terrascope.cli.lib.workflow as wf


@click.group(cls=AliasedGroup, help="Algorithm 'computation' command group")
@click.pass_context
def computation(ctx):
    pass


@computation.command(name='get')
@click.pass_context
@click.option('-ip', '--algorithm_computation_id', type=str)
@click.option('-v', '--verbose', is_flag=True)
def algorithm_computation_get(ctx, algorithm_computation_id, verbose):

    wf.check_environment_complete(raise_on_failure=True)

    algorithm_computation_info = asyncio.run(
        wf.get_algorithm_computation_info([algorithm_computation_id])
    )[0]
    info = tsu.protobuf_to_dict(algorithm_computation_info)

    click.secho(algorithm_computation_id, fg='cyan')
    for k, v in info.items():
        click.echo(f"{k:20s} {v}")


@computation.command(name='create')
@click.pass_context
@click.option('-ic', '--algorithm_config_id', type=str)
@click.option('-iac', '--aoi_collection_id', type=str)
@click.option('-it', '--toi_id', type=str)
@click.option('-s', '--start_date', type=str)
@click.option('-e', '--end_date', type=str)
@click.option('-af', '--aoi_file', type=str)
@click.option('-d', '--date_format', type=str, default='%Y-%m-%d')
@click.option('-f', '--frequency', type=click.IntRange(min=2, max=3, clamp=False), default=3,
              help="HOURLY=2, DAILY=3")
@click.option('--dry_run', is_flag=True)
@click.option('-v', '--verbose', is_flag=True)
def algorithm_computation_create(
        ctx,
        algorithm_config_id,
        start_date,
        end_date,
        aoi_file,
        date_format,
        frequency,
        dry_run,
        verbose,
        aoi_collection_id=None,
        toi_id=None,
):

    wf.check_environment_complete(raise_on_failure=True)
    click.echo("Using the following information:")
    click.echo(f"--> algorithm_config_id:      {algorithm_config_id}")
    click.echo(f"--> start_date:               {start_date}")
    click.echo(f"--> end_date:                 {end_date}")
    click.echo(f"--> aoi_file:                 {aoi_file}")
    click.echo(f"--> date_format:              {date_format}")
    click.echo(f"--> frequency:                {frequency}")
    click.echo(f"--> aoi_collectin_id:         {aoi_collection_id}")
    click.echo(f"--> toi_id:                   {toi_id}")

    if not dry_run:

        if aoi_collection_id and toi_id:
            computation_id = asyncio.run(
                wf.create_algorithm_computation(
                    algorithm_config_id,
                    toi_id,
                    aoi_collection_id,
                )
            )
        else:
            computation_id = asyncio.run(
                wf.create_algorithm_computation_aoi_toi(
                    algorithm_config_id,
                    start_date,
                    end_date,
                    aoi_file,
                    date_format=date_format,
                    frequency=frequency,
                )
            )

        tsu.echo_highlight_suffix("computation_id: ", computation_id, 'green')


@computation.command(name='run')
@click.pass_context
@click.option('-ip', '--algorithm_computation_id', type=str)
@click.option('--dry_run', is_flag=True)
@click.option('-v', '--verbose', is_flag=True)
def algorithm_computation_run(
        ctx,
        algorithm_computation_id,
        dry_run,
        verbose,
):

    wf.check_environment_complete(raise_on_failure=True)
    click.echo(f"Running algorithm_computation_id={algorithm_computation_id}  (dry_run={dry_run})")
    if not dry_run:
        asyncio.run(wf.run_algorithm_computations([algorithm_computation_id]))


@computation.command(name='download')
@click.pass_context
@click.option('-ip', '--algorithm_computation_id', type=str)
@click.option('-a', '--source_aoi_version', type=str)
@click.option('-os', '--min_observation_start_ts', type=str)
@click.option('-oe', '--max_observation_start_ts', type=str)
@click.option('-d', '--download_dir', type=str)
@click.option('-c', '--clobber', is_flag=True, help="Overwrite existing output")
def algorithm_computation_download(
    ctx,
    algorithm_computation_id,
    source_aoi_version=None,
    min_observation_start_ts=None,
    max_observation_start_ts=None,
    download_dir=None,
    clobber=False,
):
    wf.check_environment_complete(raise_on_failure=True)

    if os.path.exists(download_dir):
        if not clobber:
            click.secho(f"Directory: {download_dir} exists. Run with '-c' to overwrite.  Exiting.", fg='red')
            raise RuntimeError("Output file already exists.")
        else:
            click.secho(f"Directory: {download_dir} exists.  I'm removing it.", fg='yellow')
            os.rmdir(download_dir)

    asyncio.run(
        wf.download_algorithm_computation_results(
            algorithm_computation_ids=[algorithm_computation_id], source_aoi_version=source_aoi_version,
            min_observation_start_ts=min_observation_start_ts, max_observation_start_ts=max_observation_start_ts,
            download_dir=download_dir
        )
    )

    if not os.path.exists(download_dir):
        click.secho("NOT written", fg='red')
    else:
        click.secho("written.", fg='green')
