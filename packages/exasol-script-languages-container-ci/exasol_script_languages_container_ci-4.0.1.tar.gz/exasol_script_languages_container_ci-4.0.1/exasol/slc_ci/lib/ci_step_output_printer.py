from inspect import cleandoc
from pathlib import Path
from typing import Callable, Protocol

import docker


class CIStepOutputPrinterProtocol(Protocol):

    def print_exasol_docker_images(self):
        raise NotImplementedError()

    def print_file(self, filename: Path):
        raise NotImplementedError()


def _get_exasol_docker_images():
    docker_client = docker.from_env()
    try:
        exa_images = [
            str(img) for img in docker_client.images.list() if "exasol" in str(img)
        ]
        return exa_images
    finally:
        docker_client.close()


class CIStepOutputPrinter(CIStepOutputPrinterProtocol):

    def __init__(self, writer: Callable[[str], None]):
        self._writer = writer

    def print_exasol_docker_images(self):
        """
        Prints all docker images with "exasol" in it's name to stdout.
        :return: None
        """

        self._writer(
            cleandoc(
                """
            {seperator}
            Printing docker images
            {seperator}
            {images}"""
            ).format(seperator=20 * "=", images="\n".join(_get_exasol_docker_images()))
        )

    def print_file(self, filename: Path):
        """
        Print the file's content to the writer.
        """
        with open(filename) as f:
            self._writer(f.read())
