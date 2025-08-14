import typer
import json
from typing_extensions import Annotated
from typing import List

from .plugins.dataset_paths.typer_interface import app as dataset_paths_app
from .plugins.briltools.typer_interface import app as briltools_app

from .__init__ import __version__

app = typer.Typer()

app.add_typer(dataset_paths_app)
app.add_typer(briltools_app)

@app.command()
def version(
    verbose: Annotated[bool, typer.Option(is_flag=True, help="Print verbose version (not implemented)")] = False
):
    if verbose:
        print(__version__)
    else:
        print(__version__)

if __name__ == "__main__":
    app()