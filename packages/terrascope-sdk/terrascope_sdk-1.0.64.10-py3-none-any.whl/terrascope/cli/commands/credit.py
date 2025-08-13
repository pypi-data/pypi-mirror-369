#!/usr/bin/env python

import click
import asyncio
import pandas as pd
import terrascope.cli.lib.workflow as wf
import terrascope.cli.lib.utils as tsu
from terrascope.cli.lib.aliased_group import AliasedGroup


@click.command(cls=AliasedGroup, help="'credit' command group")
@click.pass_context
def credit(ctx):
    pass


@credit.command('get')
@click.pass_context
@click.option('-iv', '--algorithm_version_id', type=str)
def credit_get(ctx, algorithm_version_id):

    wf.check_environment_complete(raise_on_failure=True)
    click.echo("I'm sorry.  credit 'get' command is not yet implemented")

    if 0:
        source_id = '12bb3434-4696-4796-9428-7b9886ef76da'
        algo_credits = asyncio.run(wf.get_credit(source_id))
        data = []
        for algo_credit in algo_credits:
            data.append(tsu.protobuf_to_dict(algo_credit))
        df = pd.DataFrame(data)
        click.secho(f"Credit source ID: {source_id}", fg='cyan')
        click.echo(df)


@credit.command('set')
@click.pass_context
@click.option('-iv', '--algorithm_version_id', type=str)
@click.option('-pv', '--value_price', type=float)
@click.option('-pe', '--execution_price', type=float)
@click.option('--dry_run', is_flag=True)
def credit_set(ctx, algorithm_version_id, value_price, execution_price, dry_run):

    wf.check_environment_complete(raise_on_failure=True)

    if not dry_run:
        asyncio.run(
            wf.set_credit(algorithm_version_id=algorithm_version_id,
                          value_price=value_price,
                          execution_price=execution_price)
        )
