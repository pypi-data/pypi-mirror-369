import subprocess
import os
import json
import pandas as pd
import io
from concurrent.futures import ThreadPoolExecutor, as_completed

from typing import List, Dict

def _run_bril(args: List[str]) -> str:
    brilcommand = "singularity -s exec  --env PYTHONPATH=/home/bril/.local/lib/python3.10/site-packages /cvmfs/unpacked.cern.ch/gitlab-registry.cern.ch/cms-cloud/brilws-docker:latest brilcalc"

    # Append args to the brilcommand
    brilcommand = brilcommand + " " + " ".join(args)

    proc = subprocess.run(
        [brilcommand],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True,
        executable="/bin/bash",
    )
    return proc.stdout

def _ps_from_csv(csv: str):
    df = pd.read_csv(io.StringIO(csv),
        index_col="cmsls",
        usecols=["cmsls", "totprescval"],
        dtype={"cmsls": int, "totprescval": float}
    )
    return df.to_dict()["totprescval"]

def _lumi_from_csv(csv: str, units: str = "/pb") -> float:
    head_idx = csv.find("#run:fill")
    header = csv[head_idx:csv.find("\n", head_idx)].split(",")
    df = pd.read_csv(io.StringIO(csv.split("\n\n")[0]),
        comment="#",
        names=header
    )
    return df[f"recorded({units})"].sum()
        

def build_ps_weights(
    trigger: str,
    runs: List[int],
    max_workers: int = None,
) -> Dict[int, Dict[str, float]]:
    args = ["trg", "--prescale", "--hltpath", f"{trigger}_v*", "--output-style", "csv", "-r"]

    if max_workers is None:
        cpu = os.cpu_count() or 4
        max_workers = min(32, cpu * 8)

    ps_weights = dict.fromkeys(runs, None)

    def worker(idx_run: int):
        run = runs[idx_run]
        bril_result = _run_bril(args + [str(run)])

        ps_weights[run] = _ps_from_csv(bril_result)


    with ThreadPoolExecutor(max_workers=None) as ex:
        futures = [ex.submit(worker, i) for i in range(len(runs))]
        # Raise the first error early with context
        for fut in as_completed(futures):
            fut.result()

    return ps_weights

def build_lumi(
    lumijson: str,
    trigger: str = None,
    normtag: str = "BRIL",
    units: str = "/pb",
) -> float:
    args = ["lumi", "-u", units, "-i", lumijson, "--normtag", f"/cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_{normtag}.json", "--output-style", "csv"]

    if trigger is not None:
        args = args + ["--hltpath", f"{trigger}_v*"]

    return _lumi_from_csv(_run_bril(args), units)

def build_pu_hist():
    pass
    


if __name__ == "__main__":

    trigger = "HLT_PFJet40"
    runs = [395616, 395617]

    print(build_ps_weights(trigger, runs))

    print(build_lumi("/eos/user/j/jecpcl/public/jec4prompt/daily_dials/daily_dials.json", trigger))


