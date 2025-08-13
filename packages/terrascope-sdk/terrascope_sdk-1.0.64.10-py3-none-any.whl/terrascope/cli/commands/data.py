#!/usr/bin/env python

import click
import asyncio
import re
import yaml
import pandas as pd
import tabulate
import terrascope.cli.lib.workflow as wf
import terrascope.cli.lib.utils as tsu
from terrascope.cli.lib.aliased_group import AliasedSuperGroup, AliasedGroup


@click.command(cls=AliasedGroup, help='Data source command group')
@click.pass_context
def source(ctx):
    pass


@source.command('get')
@click.pass_context
@click.option('-n', '--source_name', type=str)
def data_source_get(ctx, source_name):

    wf.check_environment_complete(raise_on_failure=True)

    data_sources = asyncio.run(wf.list_data_sources())

    data = []
    for data_source in data_sources:
        data_source = tsu.protobuf_to_dict(data_source)
        if re.search(source_name, data_source['id']):
            data.append(data_source)
    df = pd.DataFrame(data)
    click.secho("Supported Data Sources:", fg='cyan')
    click.echo(tabulate.tabulate(df.T, maxcolwidths=[None, 40]))


@source.command('list')
@click.pass_context
def data_source_list(ctx):

    wf.check_environment_complete(raise_on_failure=True)

    data_sources = asyncio.run(wf.list_data_sources())

    data = []
    for data_source in data_sources:
        data.append(tsu.protobuf_to_dict(data_source))
    df = pd.DataFrame(data)
    pd.set_option('display.max_rows', None)
    click.secho("Supported Data Sources:", fg='cyan')
    click.echo(df[['id', 'name']])


@click.command(cls=AliasedGroup, help='Data type command group')
@click.pass_context
def type(ctx):
    pass


@type.command('get')
@click.pass_context
@click.option('-n', '--type_name', type=str)
def data_type_get(ctx, type_name):

    wf.check_environment_complete(raise_on_failure=True)

    data_types = asyncio.run(wf.list_data_types())

    data = []
    for data_type in data_types:
        data_type = tsu.protobuf_to_dict(data_type)
        if re.search(type_name, data_type['name']):
            data.append(data_type)
    df = pd.DataFrame(data)

    click.secho("Supported Data Types:", fg='cyan')
    click.echo(tabulate.tabulate(df.T, maxcolwidths=[None, 40]))


@type.command('list')
@click.pass_context
def data_type_list(ctx):

    wf.check_environment_complete(raise_on_failure=True)

    data_types = asyncio.run(wf.list_data_types())

    data = []
    for data_type in data_types:
        data.append(tsu.protobuf_to_dict(data_type))
    df = pd.DataFrame(data)
    pd.set_option('display.max_rows', None)
    click.secho("Supported Data Types:", fg='cyan')
    click.echo(df[['name', 'sensor_type', 'data_source_ids']])


@type.command('create')
@click.pass_context
@click.option('-f', '--definition_file', type=str, default=None)
@click.option('-n', '--name', type=str, default=None)
@click.option('-d', '--description', type=str, default=None)
@click.option('-s', '--schema', type=str, default=None)
@click.option('-ds', '--data_source_ids', default=None)
@click.option('-S', '--sensor_type', type=str, default=None)
def data_type_create(
        ctx,
        definition_file=None,
        name=None,
        description=None,
        schema=None,
        data_source_ids=None,
        sensor_type=''
):

    wf.check_environment_complete(raise_on_failure=True)

    if definition_file:
        with open(definition_file) as fp:
            data_type_def = yaml.safe_load(fp)
        if not name:
            name = data_type_def['name']
        if not description:
            description = data_type_def.get('description', '')
        if not schema:
            schema = data_type_def.get('schema', '')
        if not data_source_ids:
            data_source_ids = data_type_def.get('data_source_ids', '')
        if not sensor_type:
            sensor_type = data_type_def.get('sensor_type', '')

    data_type = asyncio.run(wf.create_data_type(name=name, description=description,
                                                schema=schema, data_source_ids=data_source_ids,
                                                sensor_type=sensor_type))
    click.echo(data_type)


@click.command(cls=AliasedSuperGroup, help="'data' super group")
@click.pass_context
def data(ctx):
    pass


data.add_command(source)
data.add_command(type)
