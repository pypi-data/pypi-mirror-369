import click


def password(function):
    function = click.option(
        "--password",
        help="Password for authentication.",
        type=str,
        required=True,
        envvar="SHIPCTL_OCI_PASSWORD",
    )(function)
    return function


def username(function):
    function = click.option(
        "--username",
        help="Username for authentication.",
        type=str,
        required=True,
        envvar="SHIPCTL_OCI_USERNAME",
    )(function)
    return function


def target(function):
    function = click.option(
        "--target",
        help="Target OCI artifact.",
        type=str,
        required=True,
        envvar="SHIPCTL_OCI_TARGET",
    )(function)
    return function


def outdir(function):
    function = click.option(
        "--outdir",
        help="Output directory for artifacts.",
        type=str,
        default="./artifacts",
        envvar="SHIPCTL_OCI_OUTDIR",
    )(function)
    return function


def files(function):
    function = click.option(
        "--files",
        help="Files to upload.",
        type=str,
        multiple=True,
        envvar="SHIPCTL_OCI_FILES",
    )(function)
    return function


def description(function):
    function = click.option(
        "--description",
        help="Description of the artifact.",
        type=str,
        envvar="SHIPCTL_OCI_DESCRIPTION",
    )(function)
    return function


def source(function):
    function = click.option(
        "--source",
        help="Source repository of the artifact.",
        type=str,
        envvar="SHIPCTL_OCI_SOURCE_REPO",
    )(function)
    return function
