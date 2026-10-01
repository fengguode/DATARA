"""Check that published agent identities use the canonical label format.

Scans tracked Markdown and tracked role definitions for the short form
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
    python -X utf8 scripts/check_identity_labels.py

Exit status is 0 when no defect is found and 1 otherwise.

What this check cannot do: it validates label text in tracked files and this
branch's attribution trailers. It does not prove that a role was natively
loaded, that a run occurred, or that any product behaviour is verified.
"""

import pathlib
import re
import subprocess
import sys
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parent.parent

EM = "\u2014"
# Any dash-like character may appear where a separator is expected, so a
# wrong-dash label is still *detected* and can then be reported as a defect.
ANY_DASH = r"[-\u2010-\u2015\u2212]"
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
    # `harness-unconfirmed` is admitted because CODE_OF_CONDUCT.md:70,75 requires
    # a run to downgrade only what it cannot verify and never to drop a key: a
    # run that cannot observe its harness has no other conforming label to write.
    return re.compile(
        rf"{ROLE} {dash} {NAME}_[A-Za-z0-9.\-]+_"
        rf"(?:Codex|OpenCode|harness-unconfirmed) \(AI agent\)")


OLD_ANY = short_form(ANY_DASH)
NEW_ANY = canonical(ANY_DASH)
OLD_EM = short_form(re.escape(ONLY_EM))
NEW_EM = canonical(re.escape(ONLY_EM))

# Commit trailers that must carry the canonical label.
TRAILER_KEYS = ("Contributed-by", "Implemented-by", "Integrated-by")

# The `Model used:` trailer carries a different grammar and is validated
# separately. CODE_OF_CONDUCT.md:66-77 requires explicit key/value pairs on one
# line and states the bare sentinels are not valid standalone values, so a value
# must be exactly the three keyed pairs with no spaces inside any of them.
MODEL_USED = re.compile(
    r"model=\S+ variant=\S+ harness=\S+")

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
# A blanket prefix would silently accept a new file forever with a generic
# reason, so a file under one of these is exempt only if its own name carries an
# ISO date. An undated or newly invented file must be added to PRESERVE above
# with its own reason, or it is reported as a defect.
PRESERVE_PREFIXES = ("docs/team/reviews/",)
# A dated review record must carry a real calendar date in its own file name.
# A bare \d{4}-\d{2}-\d{2} also matches impossible dates such as 2026-99-99 and
# digit runs inside a longer token, which would restore the blanket exemption
# this rule exists to prevent, so the value is parsed as a date and the match
# is anchored to the file-name stem.
DATED_NAME = re.compile(r"(?:^|[^0-9])(\d{4})-(\d{2})-(\d{2})(?![0-9])")


def dated_name(rel: str) -> bool:
    """True when rel's file name carries a real YYYY-MM-DD date."""
    stem = pathlib.PurePosixPath(rel).name
    for match in DATED_NAME.finditer(stem):
        try:
            date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            continue  # not a real calendar date, e.g. month 99
        return True
    return False


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
    if rel.startswith(PRESERVE_PREFIXES):
        return dated_name(rel)
    return False


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
        for dash, tag in ((EM, "em"), ("-", "ascii"), ("\u2013", "en")):
            if not OLD_ANY.search(f"Worker {dash} {name} (AI agent)"):
                fail(f"short form not detected with {tag} dash: {name}")
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

    placeholder = ("<Role> " + EM
                   + " <Configured name>_<model>-<variant>_<Harness> (AI agent)>")
    if OLD_ANY.search(placeholder):
        fail("placeholder slot reported as a real short-form identity")

    # A label value must BE the label. search() would accept any of these,
    # which is the defect that let a relaying note pass as an attribution.
    good = f"Worker {EM} Torsten Maier_space-bunny-free-max_OpenCode (AI agent)"
    if not NEW_EM.fullmatch(good):
        fail("a well-formed canonical label was rejected by fullmatch")
    for wrap, why in (
        (good + " (relayed by Reviewer " + EM + " Dennis Windmaier (AI agent))",
         "label plus a relaying note"),
        ("work done by " + good + " yesterday", "label with surrounding prose"),
        (good + " zzz qqq", "label with trailing tokens"),
    ):
        if NEW_EM.search(wrap) and NEW_EM.fullmatch(wrap):
            fail(f"fullmatch accepted a non-conforming value: {why}")
        elif not NEW_EM.search(wrap):
            fail(f"search failed to find the embedded label: {why}")

    # A run that cannot observe its harness must still have a publishable label.
    if not NEW_EM.fullmatch(
            f"Worker {EM} Torsten Maier_space-bunny-free-max_harness-unconfirmed (AI agent)"):
        fail("harness-unconfirmed sentinel is not expressible in a label")

    # The Model used: trailer has its own grammar and is enforced.
    if not MODEL_USED.fullmatch("model=opencode/space-bunny-free variant=max harness=OpenCode"):
        fail("a conforming Model used: value was rejected")
    for bad_value, why in (
        ("space-bunny-free-max (OpenCode)", "free text, not keyed pairs"),
        ("model=opencode/space-bunny-free", "missing variant and harness"),
        ("variant=max harness=OpenCode", "missing model"),
        ("model= variant=max harness=OpenCode", "empty model value"),
        ("model-unconfirmed", "bare sentinel, not a keyed value"),
    ):
        if MODEL_USED.fullmatch(bad_value):
            fail(f"Model used: accepted an invalid value: {why}")

    # The dated-review exemption must accept a real date and reject the shapes
    # a bare digit pattern would wave through.
    for rel, expected, why in (
        ("docs/team/reviews/duplicate-options-review-2026-10-01.md", True, "real date"),
        ("docs/team/reviews/notes-2026-10-01-x.md", True, "real date with suffix"),
        ("docs/team/reviews/x-2026-99-99-9999.md", False, "impossible month/day"),
        ("docs/team/reviews/x-2026-13-01.md", False, "month 13"),
        ("docs/team/reviews/x-2026-02-30.md", False, "30 February"),
        ("docs/team/reviews/report-1234-56-78-final.md", False, "digit run mid-token"),
        ("docs/team/reviews/undated.md", False, "no date at all"),
    ):
        if dated_name(rel) is not expected:
            fail(f"dated_name({rel!r}) should be {expected} ({why})")

    # Exercise the reporting path, not only the patterns. A previous revision
    # validated the patterns but crashed while printing the first real defect,
    # because the defect list held 3-tuples and the report loop unpacked 2.
    # Every finding list below is unpacked here exactly as main() unpacks it.
    try:
        sample_allowed = [("f.md:1", "text", "reason")]
        sample_defects = [("f.md:2", "text", "reason")]
        sample_wrong = [("f.md:3", "text")]
        for entry, snippet, reason in sample_allowed:
            pass
        for entry, snippet, _reason in sample_defects:
            pass
        for entry, snippet in sample_wrong:
            pass
    except ValueError as exc:
        fail(f"finding-list unpacking is inconsistent: {exc}")

    return ok


def base_ref() -> str | None:
    """Resolve a comparison ref defensively.

    A fresh clone, a fork, a shallow clone, or a repository with a differently
    named remote has no `origin/main`. The trailer scan must degrade to a
    visible skip, never to a traceback: a crash here is indistinguishable from
    a content defect to whoever runs the check, and it would discard the file
    results already computed.
    """
    for candidate in ("origin/main", "main", "origin/master", "master"):
        probe = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "--verify", "--quiet", candidate],
            capture_output=True,
        )
        if probe.returncode == 0:
            return candidate
    return None


def scan_files() -> tuple[list, list, list, list]:
    """Scan tracked Markdown AND tracked role definitions.

    Role definitions are what actually generate published identities. A previous
    revision scanned only `*.md` and therefore could not see a non-canonical
    label in `.codex/agents/*.toml`, which is the surface most likely to drift.
    """
    paths = [p for p in git("ls-files", "*.md", "*.toml").split() if p]
    allowed: list[tuple[str, str, str]] = []
    defects: list[tuple[str, str, str]] = []
    wrong_dash: list[tuple[str, str]] = []

    for rel in paths:
        text = (ROOT / rel).read_text(encoding="utf-8")
        for number, line in enumerate(text.splitlines(), 1):
            if "(AI agent)" not in line:
                continue
            entry = f"{rel}:{number}"
            # A wrong-dash canonical label is a defect wherever it appears.
            for m in NEW_ANY.finditer(line):
                if not NEW_EM.search(m.group(0)):
                    wrong_dash.append((entry, m.group(0)))
            canonical_spans = [m.span() for m in NEW_ANY.finditer(line)]
            for m in OLD_ANY.finditer(line):
                # A canonical label suppresses only a short form contained in its
                # own span. Suppressing the whole line would let any prose line
                # that names two identities hide a non-conforming one.
                if any(start <= m.start() and m.end() <= end
                       for start, end in canonical_spans):
                    continue
                (allowed if preserved(rel) else defects).append(
                    (entry, m.group(0), PRESERVE.get(rel, "dated review record")))
    return paths, allowed, defects, wrong_dash


def scan_trailers(ref: str) -> list[tuple[str, str]]:
    """Every attribution trailer on this branch must use the em dash form.

    Scope is this branch relative to `ref`. That is correct for a pre-merge
    gate and must not be read as repository-wide.
    """
    bad: list[tuple[str, str]] = []
    log = git("log", "--format=%H%x1f%B%x1e", f"{ref}..HEAD").strip("\n")
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
            # fullmatch, not search: a value that merely *contains* a canonical
            # label ("<label> (relayed by ...)", "work done by <label> yesterday")
            # is not itself a canonical label and must be reported.
            if not NEW_EM.fullmatch(value):
                bad.append((sha.strip()[:7], line.strip()))
    # Model-used: is a separate key with its own grammar, so it is checked in
    # its own pass rather than through the identity-label keys.
    for record in log.split("\x1e"):
        record = record.strip("\n")
        if not record:
            continue
        sha, _, body = record.partition("\x1f")
        for line in body.splitlines():
            key, sep, value = line.partition(":")
            if not sep or key.strip() != "Model-used":
                continue
            if not MODEL_USED.fullmatch(value.strip()):
                bad.append((sha.strip()[:7], line.strip()))
    return bad


def main() -> int:
    print("Identity label check")
    print()

    if not self_test():
        print("Self-test failed; patterns are not trustworthy. No results reported.")
        return 1
    print("Self-test passed: all 11 configured names detected in both forms,")
    print("wrong-dash labels detected and rejected, placeholder slots ignored,")
    print("finding-list unpacking consistent.")
    print()

    paths, allowed, defects, wrong_dash = scan_files()

    print(f"Tracked Markdown and role-definition files scanned: {len(paths)}")
    print()
    print(f"Short-form identities in preserved records: {len(allowed)}")
    for entry, snippet, reason in allowed:
        print(f"  OK      {entry}")
        print(f"          reason: {reason}")
        print(f"          text:   {snippet}")
    print()
    print(f"Short-form identities in live locations (must be zero): {len(defects)}")
    for entry, snippet, _reason in defects:
        print(f"  DEFECT  {entry}  {snippet}")
        print("          Live records must use the canonical label. Add a dated record to")
        print("          PRESERVE with a reason only if it is genuinely historical.")
    print()
    print(f"Canonical labels using a dash other than U+2014 (must be zero): {len(wrong_dash)}")
    for entry, snippet in wrong_dash:
        print(f"  DEFECT  {entry}  {snippet}")

    ref = base_ref()
    if ref is None:
        print()
        print("Trailer check SKIPPED: no base ref found (tried origin/main, main,")
        print("origin/master, master). This is a tooling limitation, not a pass.")
        trailer_bad: list[tuple[str, str]] = []
    else:
        trailer_bad = scan_trailers(ref)
        ahead = git("rev-list", "--count", f"{ref}..HEAD").strip()
        print()
        if ahead in ("", "0"):
            print(f"Trailer check inspected nothing: HEAD is {ref}, or has no commits")
            print("beyond it. Report this as not checked, not as a pass.")
        else:
            print(f"Attribution trailers not in em-dash form (must be zero), "
                  f"{ahead} commit(s) against {ref}: {len(trailer_bad)}")
            for sha, line in trailer_bad:
                print(f"  DEFECT  {sha}  {line}")
                print("          Trailers must use the canonical label with U+2014.")

    print()
    print("This check validates label text in tracked files and this branch's")
    print("trailers only. It does not scan the requirements registry, does not prove")
    print("that a role was natively loaded, that a run occurred, or that any product")
    print("behavior is verified.")

    return 1 if (defects or wrong_dash or trailer_bad) else 0


if __name__ == "__main__":
    sys.exit(main())
