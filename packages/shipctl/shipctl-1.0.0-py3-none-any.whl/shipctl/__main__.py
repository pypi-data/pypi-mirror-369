import click
from .oci_upload import upload_artifact
from .oci_download import download_artifact


@click.group()
def cli():
    pass


cli.add_command(upload_artifact, name="up")
cli.add_command(download_artifact, name="down")

if __name__ == "__main__":
    cli()
