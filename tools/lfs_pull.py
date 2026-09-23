"""Pull Git LFS objects without the git-lfs client (the remote Claude environment has none).

Usage:  python3 tools/lfs_pull.py Input/path/to/file.ext [more pointer files ...]
Each argument must be an LFS pointer file as checked out by plain git; the object is fetched
from GitHub's LFS batch API (public read), verified by sha256 and written over the pointer.
Before committing, restore the pointers:  git checkout -- Input/ && git clean -fdq Input/
Never `git add` a pulled Input file: the repository has no git-lfs filter here, so the content
would be committed as a plain blob.
"""
import sys, json, hashlib, subprocess, urllib.request, os
repo = "https://github.com/oh-da/Nofit_LRT_Extension.git/info/lfs/objects/batch"
paths = sys.argv[1:]
objs = {}
for p in paths:
    with open(p, 'rb') as f:
        lines = f.read(400).decode('utf-8','replace').splitlines()
    if not lines or not lines[0].startswith("version https://git-lfs"):
        print("not a pointer:", p); continue
    oid = [l for l in lines if l.startswith("oid")][0].split(":")[1]
    size = int([l for l in lines if l.startswith("size")][0].split()[1])
    objs[oid] = (p, size)
body = json.dumps({"operation":"download","transfers":["basic"],
                   "objects":[{"oid":o,"size":s} for o,(p,s) in objs.items()]}).encode()
req = urllib.request.Request(repo, data=body, headers={
    "Accept":"application/vnd.git-lfs+json","Content-Type":"application/vnd.git-lfs+json"})
resp = json.load(urllib.request.urlopen(req, timeout=120))
for o in resp["objects"]:
    p, size = objs[o["oid"]]
    href = o["actions"]["download"]["href"]
    subprocess.run(["curl","-sS","-L","-m","900","-o",p+".tmp",href], check=True)
    h = hashlib.sha256(open(p+".tmp","rb").read()).hexdigest()
    if h != o["oid"]:
        print("HASH MISMATCH", p); os.remove(p+".tmp"); continue
    os.replace(p+".tmp", p)
    print("ok", p, os.path.getsize(p))
