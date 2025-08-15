import click

from . import __version__
from .create_new import create_new
from .deploy import deploy
from .model_update import model_update


@click.group(name="engine-tools")
@click.version_option(version=__version__, prog_name="nomnomdata-engine-tools")
def cli():
    """Used for building/deploying engines"""


cli.add_command(create_new)
cli.add_command(deploy)
cli.add_command(model_update)
