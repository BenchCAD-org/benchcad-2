"""Regenerate CONTRIBUTORS.md — the per-family provenance board.

For every designs/<family>/ it records the chain the lifecycle leaves behind:
  proposed by   = author + date of the earliest `[family] <name>` issue
  implemented   = author + number of the merged PR that closed it (the
                  implementer also verified the issue's evidence at claim time)
  verified by   = reviewer(s) who APPROVED that PR
Sources: GitHub REST API (token via GITHUB_TOKEN). Manual edits are overwritten.
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
CLOSE_RE = re.compile(r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)", re.I)


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
    families = sorted(
        d.name for d in (root / "designs").iterdir() if (d / "family.json").exists()
    )
    issues = [i for i in paged(f"{API}/issues?state=all&labels=family") if "pull_request" not in i]
    pulls = [p for p in paged(f"{API}/pulls?state=closed") if p.get("merged_at")]

    rows = []
    for fam in families:
        meta = json.loads((root / "designs" / fam / "family.json").read_text())
        src = (meta.get("source") or "").split("—")[0].split(";")[0].strip()

        cand = [i for i in issues if i["title"].startswith(f"[family] {fam}")]
        issue = min(cand, key=lambda i: i["created_at"]) if cand else None

        proposed = implemented = verified = "—"
        if issue:
            proposed = f"[@{issue['user']['login']}](https://github.com/{issue['user']['login']}) · {issue['created_at'][:10]} · #{issue['number']}"
            pr = next(
                (p for p in pulls
                 if (m := CLOSE_RE.search(p.get("body") or "")) and int(m.group(1)) == issue["number"]
                 or p["head"]["ref"] == f"family/{fam}"),
                None,
            )
            if pr:
                implemented = f"[@{pr['user']['login']}](https://github.com/{pr['user']['login']}) · #{pr['number']}"
                approvers = {
                    r["user"]["login"]
                    for r in paged(f"{API}/pulls/{pr['number']}/reviews")
                    if r["state"] == "APPROVED" and r["user"]["login"] != pr["user"]["login"]
                }
                if approvers:
                    verified = " ".join(
                        f"[@{a}](https://github.com/{a})" for a in sorted(approvers)
                    )
        else:
            proposed = "bootstrap (pre-SOP)"
        contributor = meta.get("contributor", "—")
        rows.append(
            f"| `{fam}` | [@{contributor}](https://github.com/{contributor}) | {proposed} | {implemented} | {verified} | {src} |"
        )

    out = f"""# Contributors — the provenance board

**Auto-generated** by `.github/workflows/credits.yml` from the issues and PRs
themselves (SOP 📒 records) — do not edit by hand. Merged family ⇒ the row
below, named credit in the dataset card of the release that ships it, and
co-authorship on the BenchCAD 2.0 paper (see [CONTRIBUTING.md](CONTRIBUTING.md)).

| Family | Design author | Proposed | Implemented | Verified | Primary source |
|---|---|---|---|---|---|
{chr(10).join(rows)}

*Proposed = family-issue author · Implemented = merged-PR author (who also
verified the issue's evidence at claim time, per CONTRIBUTING.md) · Verified =
approving [reviewer](REVIEWING.md).
"bootstrap (pre-SOP)" marks the reference designs that predate this workflow.*
"""
    (root / "CONTRIBUTORS.md").write_text(out)
    print(f"CONTRIBUTORS.md: {len(rows)} families")


if __name__ == "__main__":
    main(Path(__file__).resolve().parents[2])
