"""Command line interface for ss-utils-logging."""

from pathlib import Path
from typing import Annotated

import typer

from .logging_config import generate_config_files

app = typer.Typer()


@app.command()
def main(
    config_dir: Annotated[Path, typer.Argument(help="The directory to generate logging configuration files in")],
    overwrite: bool = False,
):
    """
    Generate logging configuration files.
    """
    typer.echo(f"Generating logging configuration files in {config_dir.resolve()} (overwrite={overwrite})")
    generate_config_files(config_dir, overwrite)


if __name__ == "__main__":
    typer.run(main)
