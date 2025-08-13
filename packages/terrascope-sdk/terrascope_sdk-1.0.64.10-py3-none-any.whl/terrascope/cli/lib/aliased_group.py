
import click


class AliasedBase(click.Group):
    """click.Group class to overload methods for partial command string parsing and help formatting

    """

    def get_command(self, ctx, cmd_name):
        """Overload of the get_command() method.

        It's handy to be able to type an abbreviation for commands, so
        this method overloads the get_command() method to check the
        input and see if it is an abbeviation of a command.  If it
        finds a match, it returns that.  If the input is too short and
        matches multiple commands it will fail.
        """
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx)
                   if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))

    def format_commands(self, ctx, formatter):
        """Extra format methods for multi methods that adds all the commands
        after the options.
        """
        commands = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)

            # What is this, the tool lied about a command.  Ignore it
            if cmd is None:
                continue
            if cmd.hidden:
                continue

            commands.append((subcommand, cmd))

        # allow for 3 times the default spacing
        if len(commands):
            limit = formatter.width - 6 - max(len(cmd[0]) for cmd in commands)

            rows = []
            for subcommand, cmd in commands:
                help = cmd.get_short_help_str(limit)
                rows.append((cmd, subcommand, help))

            if rows:
                cmds = []
                groups = []
                super_groups = []
                for row in rows:
                    cmd, subcmd, help = row
                    if isinstance(cmd, AliasedSuperGroup):
                        super_groups.append((subcmd, help))
                    elif isinstance(cmd, AliasedGroup):
                        groups.append((subcmd, help))
                    else:
                        cmds.append((subcmd, help))

                if super_groups:
                    with formatter.section(("Command Super-Groups")):
                        formatter.write_dl(super_groups)
                if groups:
                    with formatter.section(("Command Groups")):
                        formatter.write_dl(groups)
                if cmds:
                    with formatter.section(("Commands")):
                        formatter.write_dl(cmds)


class AliasedGroup(AliasedBase):
    """Alias for AliasedBase to be used for command groups

    All this does is provide a distinct type of command group,
    so that the formatter in AliasedBase knows what type of
    command it's dealing with.  It just allows for a clearer
    help message.
    """
    pass


class AliasedSuperGroup(AliasedBase):
    """Alias for AliasedBase to be used for command super-groups

    All this does is provide a distinct type of command group,
    so that the formatter in AliasedBase knows what type of
    command it's dealing with.  It just allows for a clearer
    help message.
    """
    pass
