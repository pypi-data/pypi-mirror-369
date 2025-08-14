import click


@click.group()
def cli():
    """
    EXASLC_CI - Exasol Script Languages Continuous Integration

    Provides a CLI to build/test/deploy and release Exasol's Script-Languages-Containters in a Github CI environment.

    Examples:

        Print this help message:

            $ exaslc-ci --help

        Get the list of available flavors and write to $GITHUB_OUT:

            $ exaslc-ci get-flavors --github-output-var flavors
    """
    pass
