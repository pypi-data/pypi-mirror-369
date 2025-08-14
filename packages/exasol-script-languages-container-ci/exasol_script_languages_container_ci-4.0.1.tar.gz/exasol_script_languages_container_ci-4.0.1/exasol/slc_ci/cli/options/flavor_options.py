import click

flavor_options = [
    click.option("--flavor", type=str, required=True, help="Selects the flavor. ")
]
