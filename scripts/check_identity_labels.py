"""Check that published agent identities use the canonical label format.

Scans tracked Markdown and this branch's commit trailers for the short form
`Role - Name (AI agent)` and for canonical labels written with the wrong dash,
then reports each occurrence as either a preserved historical record or a live
defect, so a new non-conforming identity cannot land unnoticed.

The canonical format is defined in CODE_OF_CONDUCT.md under
"Agent identity labels":

    <Role> U+2014 <Configured name>_<model>-<variant>_<Harness> (AI agent)

The separator is an em dash (U+2014) with a space on each side. ASCII hyphen,
en dash and figure dash are all rejected, because an agent or editor that emits
a plain hyphen would otherwise produce a label that is neither a recognised
label nor a reported defect.

Usage:
    python scripts/check_identity_labels.py

Exit status is 0 when no defect is found and 1 otherwise.
"""

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

EM = "\u2014"
# Any dash-like character may appear where a separator is expected, so that a
# wrong-dash label is still *detected* and can then be reported as a defect.
ANY_DASH = r"[-\u2010-\u2015\u2212]"
# Strictly the em dash, used to decide whether a label is canonical.
ONLY_EM = EM

# Role is one or two capitalised words, for example "Quality Manager" or
# "UI Designer". Configured name is one or two words whose first letter is
# capitalised and whose remaining letters are lowercase, for example
# "Wang Xiaofeng", "Nils Traeger" or "Yi Tang". Both patterns are required: an
# earlier revision used a lowercase-only name pattern and silently matched
# nothing, so it reported success while missing real occurrences.
ROLE = r"[A-Z][A-Za-z]*(?: [A-Z][A-Za-z]*)*"
NAME = r"[A-Z][a-z]+(?: [A-Z][a-z]+)?"

def short_form(dash: str) -> re.Pattern:
    return re.compile(rf"{ROLE} {dash} {NAME} \(AI agent\)")

def canonical(dash: str) -> re.Pattern:
    return re.compile(
        rf"{ROLE} {dash} {NAME}_[A-Za-z0-9.\-]+_(?:Codex|OpenCode) \(AI agent\)")

OLD_ANY = short_form(ANY_DASH)
NEW_ANY = canonical(ANY_DASH)
OLD_EM = short_form(re.escape(ONLY_EM))
NEW_EM = canonical(re.escape(ONLY_EM))

# Commit trailers that must carry the canonical label.
TRAILER_KEYS = ("Contributed-by", "Implemented-by", "Integrated-by")

# Locations where the short form is correct and must not be rewritten. Each
# entry carries its reason. This list is explicit by file so that any new
# occurrence fails the check and must be consciously classified, rather than
# being absorbed by a broad prefix and hidden.
#
# `docs/team/knowledge/` is deliberately NOT prefixed. It holds living guidance
# such as shared-lessons.md, not dated records, so a short form added there is a
# real defect.
PRESERVE = {
    "docs/team/reviews/p0-requirements-review.md":
        "dated review record of completed runs; carries runtime IDs and per-line evidence",
    "docs/management/p0-breakdown-plan.md":
        "dated assignment record for issue #28; records the base commit and the run as they were",
    "docs/management/p0-ui-requirements-review.md":
        "dated designer review record for issue #28; records base commit, runtime path and unconfirmed activation",
}

# Directories whose contents are dated review records rather than live templates.
PRESERVE_PREFIXES = ("docs/team/reviews/",)


def git(*args: str) -> str:
    # encoding must be explicit: this repository contains em dashes, and
    # text=True alone decodes with the platform default, which fails on a
    # non-UTF-8 locale. Same defect class as scripts/check_requirements.py.
    result = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return result.stdout or ""


def preserved(rel: str) -> bool:
    if rel in PRESERVE:
        return True
    return rel.startswith(PRESERVE_PREFIXES)


def self_test() -> bool:
    """Confirm the patterns detect both forms and reject wrong dashes.

    A check that cannot fail is worse than no check, so every pattern is
    exercised before any result is reported.
    """
    roster = [
        "Yi Tang", "Yu Wang", "Feng Guo", "Wang Licun", "Wu Yunzhou",
        "Torsten Maier", "Dennis Windmaier", "Abt Hermann",
        "Wang Xiaofeng", "Wang Bingshan", "Nils Traeger",
    ]
    ok = True

    def fail(msg: str) -> None:
        nonlocal ok
        print(f"  SELF-TEST FAIL: {msg}")
        ok = False

    for name in roster:
        # Short form is detected whatever dash is used.
        for dash, tag in ((EM, "em"), ("-", "ascii"), ("\u2013", "en")):
            if not OLD_ANY.search(f"Worker {dash} {name} (AI agent)"):
                fail(f"short form not detected with {tag} dash: {name}")
        # Canonical form is detected, and only the em-dash form is strict.
        for dash, tag in ((EM, "em"), ("-", "ascii"), ("\u2013", "en")):
            for harness, model in (("Codex", "gpt-6-luna-medium"),
                                   ("OpenCode", "space-bunny-free-max")):
                label = f"Worker {dash} {name}_{model}_{harness} (AI agent)"
                if not NEW_ANY.search(label):
                    fail(f"canonical form not detected with {tag} dash: {name}")
                strict = bool(NEW_EM.search(label))
                if dash == EM and not strict:
                    fail(f"em-dash canonical form rejected as non-strict: {name}")
                if dash != EM and strict:
                    fail(f"{tag}-dash label wrongly accepted as canonical: {name}")

    # A bare placeholder must not be reported as a real identity.
    placeholder = "<Role> " + EM + " <Configured name>_<model>-<variant>_<Harness> (AI agent)>"
    if OLD_ANY.search(placeholder):
        fail("placeholder slot reported as a real short-form identity")

    return ok


def scan_markdown() -> tuple[list, list, list]:
    tracked_md = [p for p in git("ls-files", "*.md").split() if p]
    allowed: list[tuple[str, str, str]] = []
    defects: list[tuple[str, str]] = []
    wrong_dash: list[tuple[str, str]] = []

    for rel in tracked_md:
        text = (ROOT / rel).read_text(encoding="utf-8")
        for number, line in enumerate(text.splitlines(), 1):
            if "(AI agent)" not in line:
                continue
            entry = f"{rel}:{number}"
            # A wrong-dash canonical label is a defect wherever it appears.
            for m in NEW_ANY.finditer(line):
                if not NEW_EM.search(m.group(0)):
                    wrong_dash.append((entry, m.group(0)))
            for m in OLD_ANY.finditer(line):
                if NEW_ANY.search(line):
                    continue
                (allowed if preserved(rel) else defects).append(
                    (entry, m.group(0), PRESERVE.get(rel, "dated review record")))
    return tracked_md, allowed, defects, wrong_dash


def scan_trailers() -> list[tuple[str, str]]:
    """Every attribution trailer on this branch must use the em dash form."""
    bad: list[tuple[str, str]] = []
    log = git("log", "--format=%H%x1f%B%x1e",
              "origin/main..HEAD").strip("\n")
    if not log:
        return bad
    for record in log.split("\x1e"):
        record = record.strip("\n")
        if not record:
            continue
        sha, _, body = record.partition("\x1f")
        for line in body.splitlines():
            key, sep, value = line.partition(":")
            if not sep or key.strip() not in TRAILER_KEYS:
                continue
            value = value.strip()
            if not NEW_EM.search(value):
                bad.append((sha.strip()[:7], line.strip()))
    return bad


def main() -> int:
    print("Identity label check")
    print()

    if not self_test():
        print("Self-test failed; patterns are not trustworthy. No results reported.")
        return 1
    print("Self-test passed: all 11 configured names detected in both forms,")
    print("wrong-dash labels detected and rejected, placeholder slots ignored.")
    print()

    tracked_md, allowed, defects, wrong_dash = scan_markdown()

    print(f"Tracked Markdown files scanned: {len(tracked_md)}")
    print()
    print(f"Short-form identities in preserved records: {len(allowed)}")
    for entry, snippet, reason in allowed:
        print(f"  OK      {entry}")
        print(f"          reason: {reason}")
        print(f"          text:   {snippet}")
    print()
    print(f"Short-form identities in live locations (must be zero): {len(defects)}")
    for entry, snippet in defects:
        print(f"  DEFECT  {entry}  {snippet}")
        print("          Live records must use the canonical label. Add a dated record to")
        print("          PRESERVE with a reason only if it is genuinely historical.")
    print()
    print(f"Canonical labels using a dash other than U+2014 (must be zero): {len(wrong_dash)}")
    for entry, snippet in wrong_dash:
        print(f"  DEFECT  {entry}  {snippet}")
        print(f"          The separator must be an em dash (U+2014), not {snippet!r}.")

    trailer_bad = scan_trailers()
    print()
    print(f"Attribution trailers on this branch not in em-dash form (must be zero): {len(trailer_bad)}")
    for sha, line in trailer_bad:
        print(f"  DEFECT  {sha}  {line}")
        print("          Trailers must use the canonical label with U+2014.")

    print()
    print("This check validates label text only. It does not prove that a role was")
    print("natively loaded, that a run occurred, or that any product behavior is verified.")

    return 1 if (defects or wrong_dash or trailer_bad) else 0


if __name__ == "__main__":
    sys.exit(main())
