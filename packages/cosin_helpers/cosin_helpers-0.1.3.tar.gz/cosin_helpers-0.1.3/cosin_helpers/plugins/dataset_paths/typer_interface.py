import typer
import json

from typing_extensions import Annotated
from typing import List
from .dataset_paths import build_file_list

app = typer.Typer()

@app.command()
def dataset_paths(
    dataset: Annotated[List[str], typer.Argument(help="Name of the dataset in DAS")],
    veto_regions: Annotated[List[str], typer.Option("--veto-regions", "-r", help="Veto regions")] = ["BR", "RU", "LB", "US"],
    veto_tape: Annotated[bool, typer.Option("--veto-tape", "-t", help="Veto tape sites")] = True,
    veto_tier: Annotated[List[str], typer.Option("--veto-tier", "-v", help="Veto tier sites")] = ["T3"],
    max_workers: Annotated[int, typer.Option("--max-workers", "-w", help="Max number of workers")] = None,
    redirector: Annotated[str, typer.Option("--redirector", "-R", help="Redirector")] = "root://xrootd-cms.infn.it//",
    format: Annotated[str, typer.Option("--format", "-f", help="Output format, only json and plaintext is supported currently")] = "plaintext",
    # dump_json: Annotated[bool, typer.Option("--json", "-j", help="Output as JSON")] = False,
):
    result = {}
    for d in dataset:
        result[d] = build_file_list(d, veto_regions, veto_tape, veto_tier, max_workers, redirector)

    if format == "json":
        print(json.dumps(result, indent=4))
    else:
        for d in dataset:
            print(f"{d}:")
            for f in result[d]:
                print(f"  {f}")
