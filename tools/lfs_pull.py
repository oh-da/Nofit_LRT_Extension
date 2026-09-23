#!/usr/bin/env python3
"""Fetch Git LFS objects in this checkout without the git-lfs CLI.

This environment has no ``git-lfs`` binary, so every LFS-tracked file sits as a
pointer stub after a normal clone or pull::

    version https://git-lfs.github.com/spec/v1
    oid sha256:<64 hex chars>
    size <bytes>

Pushing new LFS objects from this environment is blocked (see the note in
.gitattributes), but *downloading* them is not: GitHub's LFS batch API is
plain HTTPS and answers anonymously for a public repo, reachable through the
same proxy as everything else. This script walks the given paths, finds
pointer files, resolves them to signed download URLs in batches, and
overwrites each pointer with the real content (checksum-verified against the
pointer's own oid).

Usage:
    python3 tools/lfs_pull.py                       # whole checkout
    python3 tools/lfs_pull.py Input/BusRavKav/2025   # just one subtree
    python3 tools/lfs_pull.py --dry-run              # list only, no download
"""

import argparse
import hashlib
import os
import subprocess
import sys

import requests

POINTER_PREFIX = b"version https://git-lfs.github.com/spec/v1\n"


def find_pointers(paths):
    pointers = []
    for start in paths:
        if os.path.isfile(start):
            candidates = [start]
        else:
            candidates = []
            for dirpath, dirnames, filenames in os.walk(start):
                if ".git" in dirnames:
                    dirnames.remove(".git")
                candidates.extend(os.path.join(dirpath, name) for name in filenames)
        for fp in candidates:
            try:
                with open(fp, "rb") as f:
                    head = f.read(200)
            except OSError:
                continue
            if head.startswith(POINTER_PREFIX):
                pointers.append(fp)
    return pointers


def parse_pointer(fp):
    oid = size = None
    with open(fp, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("oid sha256:"):
                oid = line.split(":", 1)[1].strip()
            elif line.startswith("size "):
                size = int(line.split(" ", 1)[1].strip())
    if not oid or size is None:
        raise ValueError(f"{fp}: not a well-formed LFS pointer")
    return oid, size


def lfs_batch_endpoint():
    url = subprocess.check_output(["git", "remote", "get-url", "origin"], text=True).strip()
    if url.startswith("git@"):
        host, path = url[len("git@"):].split(":", 1)
        url = f"https://{host}/{path}"
    if url.endswith(".git"):
        url = url[:-4]
    return url + ".git/info/lfs/objects/batch"


def batch_download(endpoint, session, oids_and_sizes):
    resp = session.post(
        endpoint,
        json={
            "operation": "download",
            "transfers": ["basic"],
            "objects": [{"oid": oid, "size": size} for oid, size in oids_and_sizes],
        },
        headers={
            "Accept": "application/vnd.git-lfs+json",
            "Content-Type": "application/vnd.git-lfs+json",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["objects"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", default=["."], help="files or directories to scan (default: whole checkout)")
    ap.add_argument("--dry-run", action="store_true", help="list pointer files found, without downloading")
    ap.add_argument("--batch-size", type=int, default=50, help="objects per LFS batch request")
    args = ap.parse_args()

    pointers = find_pointers(args.paths)
    if not pointers:
        print("No LFS pointer files found under the given paths.")
        return

    print(f"{len(pointers)} LFS pointer file(s) found.")
    by_oid = {}
    for fp in pointers:
        oid, size = parse_pointer(fp)
        by_oid.setdefault(oid, []).append((fp, size))

    if args.dry_run:
        for oid, entries in by_oid.items():
            for fp, size in entries:
                print(f"  {fp}  ({size:,} bytes, {oid[:12]}...)")
        return

    endpoint = lfs_batch_endpoint()
    session = requests.Session()
    oids = list(by_oid)
    ok = failed = 0

    for i in range(0, len(oids), args.batch_size):
        chunk = oids[i:i + args.batch_size]
        results = batch_download(endpoint, session, [(oid, by_oid[oid][0][1]) for oid in chunk])
        for obj in results:
            oid = obj["oid"]
            action = obj.get("actions", {}).get("download")
            if not action:
                message = obj.get("error", {}).get("message", "no download action returned")
                for fp, _ in by_oid[oid]:
                    print(f"  FAILED {fp}: {message}")
                    failed += 1
                continue
            r = session.get(action["href"], timeout=180, stream=True)
            r.raise_for_status()
            data = r.content
            if hashlib.sha256(data).hexdigest() != oid:
                for fp, _ in by_oid[oid]:
                    print(f"  FAILED {fp}: downloaded content does not match the pointer's oid")
                    failed += 1
                continue
            for fp, _ in by_oid[oid]:
                with open(fp, "wb") as f:
                    f.write(data)
                print(f"  pulled {fp} ({len(data):,} bytes)")
                ok += 1

    print(f"Done: {ok} file(s) pulled, {failed} failed.")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
