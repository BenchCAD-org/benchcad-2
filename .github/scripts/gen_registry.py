"""Regenerate registry.json — the single machine-readable index of every
family name this project knows about, so duplicates are caught by bots, not
by humans reading 17 wanted lists.

Sources, in precedence order (first hit wins for status):
  merged    designs/<family>/ on main
  proposed  every [family]/[proposal] issue (open or closed)
  wanted    the wanted-list tables inside [category] issues
Each entry: {name, status, ref, category, anchor}.
"""

import json
import os
import re
import urllib.request
from pathlib import Path

REPO = os.environ.get("GITHUB_REPOSITORY", "BenchCAD-org/benchcad-2")
API = f"https://api.github.com/repos/{REPO}"
HDR = {
    "Authorization": "Bearer " + os.environ["GITHUB_TOKEN"],
    "Accept": "application/vnd.github+json",
}
ROW = re.compile(r"^\|\s*([a-z0-9_]+)\s*\|\s*([^|]+)\|")


def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=HDR)))


def paged(url):
    out, page = [], 1
    while True:
        batch = get(f"{url}{'&' if '?' in url else '?'}per_page=100&page={page}")
        out += batch
        if len(batch) < 100:
            return out
        page += 1


def main(root: Path):
    reg = {}

    def add(name, status, ref, category="", anchor=""):
        if name not in reg:  # precedence: merged > proposed > wanted
            reg[name] = dict(name=name, status=status, ref=ref,
                             category=category, anchor=anchor.strip())

    for d in sorted((root / "designs").iterdir()):
        if (d / "family.json").exists():
            meta = json.loads((d / "family.json").read_text())
            add(d.name, "merged", f"designs/{d.name}", anchor=meta.get("standard") or "")

    fam_issues = [i for i in paged(f"{API}/issues?state=all&labels=family")
                  if "pull_request" not in i]
    for i in fam_issues:
        m = re.match(r"\[(?:family|proposal)\]\s+([a-z0-9_]+)", i["title"])
        if m:
            cat = next((l["name"][4:] for l in i["labels"] if l["name"].startswith("cat:")), "")
            add(m.group(1), "proposed", f"#{i['number']}", category=cat)

    for c in [i for i in paged(f"{API}/issues?state=all&labels=category")
              if "pull_request" not in i]:
        cat = next((l["name"][4:] for l in c["labels"] if l["name"].startswith("cat:")), "")
        body = c.get("body") or ""
        if "## Wanted list" not in body:
            continue
        for line in body.split("## Wanted list", 1)[1].splitlines():
            m = ROW.match(line.strip())
            if m and m.group(1) not in ("family",):
                add(m.group(1), "wanted", f"#{c['number']}", category=cat, anchor=m.group(2))

    out = sorted(reg.values(), key=lambda e: e["name"])
    (root / "registry.json").write_text(json.dumps(out, indent=0, ensure_ascii=False) + "\n")
    by = {}
    for e in out:
        by[e["status"]] = by.get(e["status"], 0) + 1
    print(f"registry.json: {len(out)} names {by}")


if __name__ == "__main__":
    main(Path(__file__).resolve().parents[2])
