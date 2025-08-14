import typer
import json

from typing_extensions import Annotated
from typing import List
from .briltools import build_ps_weights, build_lumi
from rich.progress import track

app = typer.Typer()

@app.command()
def get_ps_weights(
    trigger: Annotated[str, typer.Argument(help="Trigger name")],
    runs: Annotated[List[int], typer.Option("--runs", "-r", help="Runs")] = None,
    lumijson: Annotated[str, typer.Option("--lumijson", "-l", help="Lumi json file to determine runs, overrides --runs")] = None,
    format: Annotated[str, typer.Option("--format", "-f", help="Output format, only json is supported currently")] = "json",
    max_workers: Annotated[int, typer.Option("--max-workers", "-w", help="Max number of workers")] = None,
):
    if runs is None and lumijson is None:
        raise ValueError("Either --runs or --lumijson must be specified")

    if runs is not None:
        runs = list(map(int, runs))

    if lumijson is not None:
        with open(lumijson) as f:
            runs = json.load(f).keys()

    result = build_ps_weights(trigger, runs, max_workers)
    print(json.dumps(result, indent=4))

@app.command()
def get_lumi(
    lumijson: Annotated[str, typer.Argument(help="Lumi json file")],
    luminame: Annotated[str, typer.Option("--luminame", "-l", help="Name of the era/collection of runs in the lumi json. Trigger overrides this option")] = None,
    trigger: Annotated[List[str], typer.Option("--trigger", "-t", help="Trigger name")] = None,
    normtag: Annotated[str, typer.Option("--normtag", "-n", help="Normtag name")] = "BRIL",
    units: Annotated[str, typer.Option("--units", "-u", help="Units")] = "/pb",
    format: Annotated[str, typer.Option("--format", "-f", help="Output format, only json is supported currently")] = "json",
):
    result = {}
    luminame = luminame or lumijson
    if trigger is not None:
        for t in track(trigger, description="Processing triggers"):
            result[t] = build_lumi(lumijson, t, normtag, units)
    else:
        result[luminame] = build_lumi(lumijson, None, normtag, units)

    print(json.dumps(result, indent=4))

    

