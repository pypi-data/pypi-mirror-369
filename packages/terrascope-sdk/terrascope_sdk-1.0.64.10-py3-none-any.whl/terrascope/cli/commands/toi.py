#!/usr/bin/env python

import click
import asyncio
import pandas as pd
import terrascope.cli.lib.workflow as wf
import terrascope.cli.lib.utils as tsu
from terrascope.cli.lib.aliased_group import AliasedGroup


@click.command(cls=AliasedGroup, help="'toi' command group")
@click.pass_context
def toi(ctx):
    pass


@toi.command('get')
@click.pass_context
@click.option('-i', '--toi_ids', multiple=True, type=str)
@click.option('-v', '--verbose', is_flag=True)
def toi_get(ctx, toi_ids, verbose):

    tois = asyncio.run(wf.get_tois(toi_ids))
    data = []
    for toi in tois:
        data.append(tsu.protobuf_to_dict(toi))
    df = pd.DataFrame(data)
    columns = ['id', 'start_local', 'finish_local']
    df = df[columns]

    if verbose:
        click.echo(tois)
    click.echo(df)


@toi.command('create')
@click.pass_context
@click.option('-s', '--start_date', type=str)
@click.option('-e', '--end_date', type=str)
@click.option('-d', '--date_format', type=str, default='%Y-%m-%d')
@click.option('-f', '--frequency', type=click.Choice([2, 3]),
              help="HOURLY=2, DAILY=3", default=3)
def toi_create(ctx, start_date, end_date, date_format, frequency):

    if not start_date or not end_date:
        raise RuntimeError("Must provide start_date or end-date to 'create' a TOI")

    toi_id = asyncio.run(
        wf.create_toi(start_date, end_date, date_format=date_format, frequency=frequency)
    )
    tsu.echo_highlight_suffix("Your new toi_id is: ", toi_id, 'green')


@toi.command('delete')
@click.pass_context
@click.option('-i', '--toi_ids', multiple=True)
def toi_delete(ctx, toi_ids):

    asyncio.run(wf.delete_tois(toi_ids))
