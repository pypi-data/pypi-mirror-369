#!/usr/bin/env python

import click
from terrascope.cli.lib.aliased_group import AliasedGroup
from terrascope.cli.commands.algorithm import algorithm
from terrascope.cli.commands.analysis import analysis
from terrascope.cli.commands.aoi import aoi
from terrascope.cli.commands.environment import environment
from terrascope.cli.commands.permission import permission
from terrascope.cli.commands.credit import credit
from terrascope.cli.commands.toi import toi
from terrascope.cli.commands.data import data
from terrascope.cli.commands.imagery import imagery
from terrascope.cli.commands.visualization import visualization
from terrascope.cli.commands.manifest import manifest
from terrascope.cli.commands.tasks import tasks


@click.command(cls=AliasedGroup)
@click.pass_context
def main(ctx):
    pass


main.add_command(algorithm)
main.add_command(analysis)
main.add_command(aoi)
main.add_command(environment)
main.add_command(permission)
main.add_command(credit)
main.add_command(toi)
main.add_command(data)
main.add_command(imagery)
main.add_command(visualization)
main.add_command(manifest)
main.add_command(tasks)


if __name__ == '__main__':
    main(obj={})
