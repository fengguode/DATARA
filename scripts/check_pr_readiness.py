#!/usr/bin/env python3
"""Pre-review readiness gate for a candidate branch.

This exists because of how five candidates failed review. Every one of those
failures shared a cause that a reviewer caught and a self-check did not, and
three of the five causes are mechanically detectable. A defect that reaches a
reviewer costs a full review cycle; the same defect caught here costs one
command.

The gate refuses, loudly, on:

G1 ADVERSE DELTAS. A diff that only adds is a different risk from a diff that
   also removes. Measuring insertions and calling the result "an addition" is how
   42 deleted lines of assertion strength passed as a coverage recovery. Every
   file with deletions must be declared, with a per-file reason.

G2 NOTATION-INCOMPLETE SEARCH. A value changed in one notation may exist in
   another, where a string search cannot see it. Changing a pinned interpreter
   from "3.12.14" to "3.12.10" leaves `(3,12,14)` live in two files, and
   `git grep 3.12.14` returns nothing for either. Every declared replaced value
   is searched in each notation it could plausibly take.

G3 UNREFERENCED CITED DOCUMENT. A tracked document citing a tracked document
   that does not exist is a fabricated authority, and the registry checker does
   not detect it.

G4 UNDECLARED EVIDENCE. A quantitative claim whose harness is not in the
   repository is not reproducible by the next reviewer. Any declared sweep must
   state its dimensions and whether its script is tracked.

G5 UNSTATED AUTHORITY SOURCES. Sources read by habit rather than by inventory is
   how the selected decision baseline went unread. The authoritative records
   consulted must be declared.

Usage
-----
    python -X utf8 scripts/check_pr_readiness.py --base origin/main \\
        --manifest .pr-readiness.json [--accept G1,G4]

Manifest shape, committed per branch. Every list may be empty; an absent
manifest is a refusal, because silence is not a declaration.

    {
      "removed_lines": {
        "<path>": "why each deleted line is intended"
      },
      "replaced_values": ["<old value the branch claims to replace>"],
      "cited_documents": ["<tracked path this branch cites>"],
      "sweeps": [
        {"name": "<sweep>", "combinations": <int>,
         "harness_tracked": true, "harness_path": "scripts/<file>"}
      ],
      "authority_sources_read": [
        {"path": "<tracked record>", "lines": "<line or range>"}
      ]
    }

``--accept`` records a deliberate acceptance of the named finding ids. Acceptance
is for findings a reviewer can see and overrule, such as an intentional deletion.
It is not a way to make a defect disappear, and every accepted id is printed.

Exit codes
----------
    0  gate satisfied, or every finding explicitly accepted with --accept
    1  defect found
    2  gate could not run (no base ref, or HEAD equals the base)
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def fail(message: str) -> None:
    print("REFUSED: " + message)


def run_git(*args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=False
    )
    return result.stdout


def notations(value: str) -> dict[str, str]:
    """Every plausible textual notation of a dotted numeric version.

    A pin written ``3.12.14`` in one file is very often written ``(3,12,14)``
    in another, because the check is a version *tuple* rather than a string.
    Searching only the dotted form is a search that cannot see its own subject.
    """
    parts = value.split(".")
    forms = {
        "dotted": value,
        "tuple": "(" + ",".join(parts) + ")",
        "tuple_spaced": "(" + ", ".join(parts) + ")",
        "underscored": value.replace(".", "_"),
        "bare": "".join(parts),
    }
    return forms


def gate_adverse_deltas(base: str, declared: dict) -> list[str]:
    raw = run_git("diff", "--numstat", base, "HEAD")
    findings: list[str] = []
    for line in raw.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        added, removed, path = parts
        if not removed or removed == "0":
            continue
        reason = (declared.get("removed_lines") or {}).get(path)
        if not reason:
            findings.append(
                f"G1 {path}: {removed} line(s) DELETED with no declared reason. "
                "A diff that removes is not an addition. Declare each removed file "
                "under removed_lines with why the removal is intended."
            )
            continue
        print(f"G1 ok {path}: {removed} deletion(s) declared - {reason}")
    return findings


def gate_replaced_values(declared: dict) -> list[str]:
    """Search HEAD, not the base.

    The question is not "did the old value exist before" but "does the old value
    still survive somewhere on this branch in a notation a string search missed".
    """
    findings: list[str] = []
    for old in (declared.get("replaced_values") or []):
        for name, form in notations(old).items():
            raw = run_git("grep", "-n", "--fixed-strings", form, "HEAD", "--", ".")
            hits = [h for h in raw.splitlines() if h.strip()]
            if hits:
                findings.append(
                    f"G2 replaced value {old!r} STILL PRESENT in {name} notation on "
                    f"HEAD, {len(hits)} site(s): " + "; ".join(hits[:4])
                )
            else:
                print(f"G2 ok {old!r}: no surviving {name} notation on HEAD")
    return findings


def gate_cited_documents(declared: dict) -> list[str]:
    findings: list[str] = []
    for ref in (declared.get("cited_documents") or []):
        target = ROOT / ref
        if not target.exists():
            findings.append(
                f"G3 cited document does not exist: {ref}. A tracked document "
                "pointing at a non-existent tracked document is a fabricated "
                "authority."
            )
        else:
            print(f"G3 ok {ref} exists")
    return findings


def gate_evidence(declared: dict) -> list[str]:
    findings: list[str] = []
    for sweep in (declared.get("sweeps") or []):
        name = sweep.get("name", "<unnamed>")
        combos = sweep.get("combinations")
        tracked = bool(sweep.get("harness_tracked"))
        script = sweep.get("harness_path")
        if combos and not tracked:
            findings.append(
                f"G4 sweep {name!r} claims {combos} combinations but its harness is "
                "not tracked. The next reviewer cannot re-run it. Set harness_tracked "
                "and harness_path, or drop the figure."
            )
            continue
        if tracked and script and not (ROOT / script).exists():
            findings.append(
                f"G4 sweep {name!r} declares harness {script!r}, which does not exist."
            )
            continue
        print(f"G4 ok sweep {name!r}: {combos} combinations, harness tracked={tracked}")
    return findings


def gate_authority(declared: dict) -> list[str]:
    findings: list[str] = []
    sources = declared.get("authority_sources_read") or []
    if not sources:
        findings.append(
            "G5 authority_sources_read is empty. Declare every authoritative record "
            "consulted, with line references. Reading the sources you already know "
            "about is how the selected decision baseline went unread."
        )
    for entry in sources:
        path = entry.get("path", "")
        lines = entry.get("lines", "")
        if not (ROOT / path).exists():
            findings.append(f"G5 declared authority source does not exist: {path}")
        else:
            print(f"G5 ok {path}:{lines}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--manifest", default=".pr-readiness.json")
    parser.add_argument(
        "--accept",
        default="",
        help="comma-separated finding ids to accept as deliberate, e.g. G1,G4",
    )
    args = parser.parse_args()

    print(f"base={args.base}")
    head = run_git("rev-parse", "HEAD").strip()
    print(f"head={head}")
    if not head or not run_git("rev-parse", "--verify", args.base).strip():
        print("gate could not run: base ref missing")
        return 2
    if run_git("rev-parse", "--verify", args.base).strip() == head:
        print("gate could not run: HEAD equals the base, nothing to assess")
        return 2

    manifest_path = ROOT / args.manifest
    if not manifest_path.exists():
        fail(
            f"no manifest at {args.manifest}. The gate is not satisfied by absence; "
            "declare removed lines, replaced values, cited documents, sweeps and "
            "authority sources even when each list is empty."
        )
        return 1
    declared = json.loads(manifest_path.read_text(encoding="utf-8"))

    accepted = {a.strip() for a in args.accept.split(",") if a.strip()}
    findings: list[str] = []
    for gate in (
        gate_adverse_deltas,
        gate_replaced_values,
        gate_cited_documents,
        gate_evidence,
        gate_authority,
    ):
        if gate is gate_adverse_deltas:
            findings += gate(args.base, declared)
        else:
            findings += gate(declared)

    unaccepted = [f for f in findings if f.split()[0] not in accepted]
    for finding in findings:
        print("FINDING " + finding)
    if unaccepted:
        fail(f"{len(unaccepted)} finding(s) not accepted")
        return 1
    print("readiness gate satisfied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())