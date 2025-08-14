import click

from cockup import __version__
from cockup.src.backup import backup
from cockup.src.config import read_config
from cockup.src.console import rprint, rprint_point
from cockup.src.hooks import select_and_run_hooks
from cockup.src.restore import restore
from cockup.src.zap import get_zap_dict

HELP = "Yet another backup tool for various configurations."
HELP_LIST = "List potential configs of installed Homebrew casks."
HELP_RESTORE = "Restore configurations from backup."
HELP_BACKUP = "Perform backup operations using specified YAML configuration file."
HELP_HOOK = "Run the selected hooks defined in the configuration."
HELP_HOOKS = "Alias for the `hook` command"


@click.group(
    context_settings=dict(help_option_names=["-h", "--help"]),
    invoke_without_command=True,
)
@click.version_option(
    version=__version__, prog_name="cockup", message="%(prog)s v%(version)s"
)
@click.pass_context
def main(ctx):
    f"""
    {HELP}
    """

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit(0)


@main.command("list", short_help=HELP_LIST)
@click.argument("casks", nargs=-1, type=click.STRING)
def list_command(casks):
    f"""
    {HELP_LIST}
    """

    rprint_point("Retrieving potential configs from Homebrew...")
    zap_dict = get_zap_dict(list(casks))
    for package, items in zap_dict.items():
        rprint()  # Print a newline for better readability
        rprint_point(f"{package}:")
        for item in items:
            rprint(f"  {item}")


@main.command("restore", short_help=HELP_RESTORE)
@click.argument("config_file", type=click.Path(exists=True))
def restore_command(config_file: str):
    f"""
    {HELP_RESTORE}

    Example: cockup restore config.yaml
    """

    cfg = read_config(config_file)

    if not cfg:
        return

    restore(cfg)


@main.command("backup", short_help=HELP_BACKUP)
@click.argument("config_file", type=click.Path(exists=True))
def backup_command(config_file: str):
    f"""
    {HELP_BACKUP}

    Example: cockup backup config.yaml
    """

    cfg = read_config(config_file)

    if not cfg:
        return

    backup(cfg)


@main.command("hook", short_help=HELP_HOOK)
@click.argument("config_file", type=click.Path(exists=True))
def hook_command(config_file: str):
    f"""
    {HELP_HOOK}

    Example: cockup hook config.yaml
    """

    cfg = read_config(config_file)

    if not cfg:
        return

    select_and_run_hooks(cfg)


@main.command("hooks", short_help=HELP_HOOKS)
@click.argument("config_file", type=click.Path(exists=True))
def hooks_command(config_file: str):
    return hook_command(config_file)


if __name__ == "__main__":
    main()
