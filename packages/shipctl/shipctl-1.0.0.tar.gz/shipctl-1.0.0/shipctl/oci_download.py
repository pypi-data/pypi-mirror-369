import click

from .click_options import outdir, password, target, username
from .shipctl_client import ShipctlOrasClient


@click.command()
@password
@username
@target
@outdir
def download_artifact(password, username, target, outdir):
    """
    Download shipctl artifacts from an OCI registry.
    """
    client = ShipctlOrasClient()
    client.login(password=password, username=username)

    result = client.pull(target=target, outdir=outdir)
    click.echo(
        f"Downloaded and extracted {len(result)} artifacts using shipctl client:"
    )
    for file_path in result:
        click.echo(f"  - {file_path}")
