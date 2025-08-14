import click

docker_options = [
    click.option(
        "--docker-user",
        type=str,
        required=True,
        help="Docker user name",
    ),
    click.option(
        "--docker-password",
        type=str,
        required=True,
        help="Docker password.",
    ),
]
