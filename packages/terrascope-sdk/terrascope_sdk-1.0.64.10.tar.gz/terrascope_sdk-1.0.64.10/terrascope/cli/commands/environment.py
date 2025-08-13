
import click
import terrascope.cli.lib.workflow as wf
from terrascope.cli.lib.aliased_group import AliasedGroup


@click.command(cls=AliasedGroup, help="'environment' command group")
@click.pass_context
def environment(ctx):
    pass


@environment.command('check')
@click.pass_context
@click.option('-a', '--check_admin', is_flag=True, default=False)
@click.option('-v', '--verbose', is_flag=True, default=False)
def env_check(ctx, check_admin=False, verbose=False):

    is_complete = wf.check_environment_complete(raise_on_failure=False, print_missing=True, verbose=verbose,
                                                requires_admin=check_admin)
    knot = ''
    if is_complete:
        fg = 'green'
    else:
        fg = 'red'
        knot = 'NOT '
    click.secho(f"Environment is {knot}complete", fg=fg)
