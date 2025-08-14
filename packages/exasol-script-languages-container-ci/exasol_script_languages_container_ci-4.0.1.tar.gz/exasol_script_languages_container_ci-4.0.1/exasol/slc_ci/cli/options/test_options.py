import click

test_set_options = [
    click.option(
        "--test-set-name",
        type=str,
        required=True,
        help="Name of the test-set to execute",
    ),
]
