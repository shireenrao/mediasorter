# src/mediasorter/console.py
from pathlib import Path
import click

from . import __version__, sorter


@click.command(no_args_is_help=True)
@click.option(
    "--source",
    "-s",
    default=Path.cwd(),
    help="Source directory of Images/Videos",
    show_default=True,
    type=click.Path(exists=True),
)
@click.option(
    "--target",
    "-t",
    help="Target directory of Images/Videos",
    required=True,
    type=click.Path(exists=True),
)
@click.option(
    "--format",
    "-f",
    default="%Y/%B/%Y_%m_%d",
    help="Directory format for how images/videos are saved to target",
    show_default=True,
)
@click.option(
    "--debug",
    "-d",
    is_flag=True,
    default=False,
)
@click.version_option(version=__version__)
def main(source, target, format, debug):
    """The mediasorter Python project."""
    click.echo(
        f"Sorting and Copy files from {source} to {target} using format {format}"
    )
    if debug:
        click.echo(f"Debug is {debug}")
    sorter.run(source, target, format, debug)
