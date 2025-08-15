import click

from .click_options import description, files, password, source, target, username
from .shipctl_client import ShipctlOrasClient


def manifest(description, source) -> dict:
    manifest = {}
    if description:
        manifest["org.opencontainers.image.description"] = description
    if source:
        manifest["org.opencontainers.image.source"] = source
    return manifest


@click.command()
@password
@username
@target
@files
@description
@source
def upload_artifact(password, username, target, files, description, source):

    client = ShipctlOrasClient()
    client.login(password=password, username=username)

    client.push(
        files=files,
        target=target,
        manifest_annotations=manifest(description, source),
    )
