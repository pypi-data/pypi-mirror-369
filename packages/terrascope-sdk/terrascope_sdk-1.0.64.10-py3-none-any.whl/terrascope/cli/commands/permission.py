#!/usr/bin/env python

import click
import asyncio
import pandas as pd
import terrascope.cli.lib.workflow as wf
import terrascope.cli.lib.utils as tsu
from terrascope.cli.lib.aliased_group import AliasedGroup
from terrascope_api.models.permission_pb2 import Permission


@click.command(cls=AliasedGroup, help="'permission' command group")
@click.pass_context
def permission(ctx):
    pass


@permission.command('get')
@click.pass_context
@click.option('-iC', '--analysis_config_id', type=str)
def permission_get(ctx, analysis_config_id):

    click.echo("I'm sorry.  permission 'get' command is not yet implemented")
    if 0:
        wf.check_environment_complete(raise_on_failure=True)
        permissions = asyncio.run(wf.get_permissions(analysis_config_id))
        data = []
        for permission in permissions:
            data.append(tsu.protobuf_to_dict(permission))
        df = pd.DataFrame(data)
        click.secho(f"analysis_config_id: {analysis_config_id}", fg='cyan')
        click.echo(df)


@permission.command('set')
@click.pass_context
@click.option('-iC', '--analysis_config_id', type=str)
@click.option('-u', '--user_emails', multiple=True, type=str)
@click.option('-p', '--public', is_flag=True, default=False)
# @click.option('-t', '--permission_type', type=click.Choice([Permission.Type.READ]),
#              default=Permission.Type.READ)
@click.option('--dry_run', is_flag=True)
def permission_set(ctx, analysis_config_id, user_emails, public, dry_run):

    permission_type = Permission.Type.READ

    wf.check_environment_complete(raise_on_failure=True)

    if not dry_run:
        # user_ids = asyncio.run(wf.get_userid_from_email(user_emails))
        asyncio.run(
            wf.analysis_permission_create(
                analysis_config_id,
                user_emails,
                permission_type=permission_type,
                public=public,
                public_confirm=public,
            )
        )
