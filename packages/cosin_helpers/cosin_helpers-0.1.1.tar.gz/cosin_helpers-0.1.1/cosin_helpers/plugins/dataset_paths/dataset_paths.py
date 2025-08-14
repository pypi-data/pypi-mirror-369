import os
import subprocess
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

def _run_dasgoclient(args):
    """Run dasgoclient and return non-empty lines."""
    proc = subprocess.run(
        ["/cvmfs/cms.cern.ch/common/dasgoclient", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    return [ln for ln in proc.stdout.splitlines() if ln.strip()]

def _list_files(dataset: str):
    # --limit 0 => no truncation even for large datasets
    return _run_dasgoclient(["--query", f"file dataset={dataset}", "--limit", "0"])

def _list_sites(file_path: str):
    return _run_dasgoclient(["--query", f"site file={file_path}"])

def _choose_site(sites: List[str], veto_regions: List[str], veto_tape: bool, veto_tier: List[str]):
    for site in sites:
        # Region check: look at the part after the first underscore (e.g., T2_US_* -> 'US*')
        parts = site.split("_", 1)
        region = parts[1] if len(parts) > 1 else site

        if any(v in region for v in veto_regions):
            continue
        if veto_tape and "Tape" in site:
            continue
        if any(site.startswith(v) for v in veto_tier):
            continue

        return site  # first acceptable site
    return None

def build_file_list(dataset: str, veto_regions: List[str] = ["BR", "RU", "LB", "US"], veto_tape: bool = True, veto_tier: List[str] = ["T1", "T3"], max_workers: int = None, redirector: str = "root://xrootd-cms.infn.it//"):
    files = _list_files(dataset)

    if max_workers is None:
        cpu = os.cpu_count() or 4
        max_workers = min(32, cpu * 8)

    final_files = [None] * len(files)

    def worker(idx_file: Tuple[int, str]):
        idx, f = idx_file
        sites = _list_sites(f)
        chosen = _choose_site(sites, veto_regions, veto_tape, veto_tier)
        if chosen is None:
            raise RuntimeError(f"No allowed sites for file {f} (candidates: {sites})")
        final_files[idx] = f"{redirector}/store/test/xrootd/{chosen}{f}"

    # Parallel site lookups
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(worker, (i, f)) for i, f in enumerate(files)]
        # Raise the first error early with context
        for fut in as_completed(futures):
            fut.result()

    return final_files


if __name__ == "__main__":
    dataset = "/WW_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM"
    print(build_file_list(dataset))