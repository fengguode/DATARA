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

import os
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
# line, and its stated recovery rule is precise: split the value on whitespace
# into three tokens, then split each token on its first `=`, yielding keys drawn
# from {model, variant, harness}. Bare sentinels are not valid standalone values.
# That rule is implemented as a parser below rather than as one regex, because
# the key order is unconstrained and the documented recovery is the contract.
MODEL_USED = re.compile(
    r"model=\S+ variant=\S+ harness=\S+")
MODEL_KEYS = ("model", "variant", "harness")
HARNESS_VALUES = ("Codex", "OpenCode", "harness-unconfirmed")


def model_used_ok(value: str) -> bool:
    """Validate a `Model used:` value by the documented recovery rule.

    Three whitespace-separated tokens, each `key=value` split on its FIRST `=`,
    keys exactly {model, variant, harness} with no duplicates, no empty values,
    and a harness drawn from the documented set. Key order is not constrained,
    because the document does not constrain it.
    """
    tokens = value.split()
    if len(tokens) != 3:
        return False
    seen: dict[str, str] = {}
    for token in tokens:
        key, sep, val = token.partition("=")
        if not sep or key not in MODEL_KEYS or not val:
            return False
        if key in seen:
            return False
        seen[key] = val
    if set(seen) != set(MODEL_KEYS):
        return False
    return seen["harness"] in HARNESS_VALUES

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
# A blanket prefix would silently accept a new file forever, so a file under one
# of these is exempt only if its own name carries a real ISO date.
#
# Stated limit, which a previous version of this comment denied: a file under
# docs/team/reviews/ whose name carries any real date earns the exemption with the
# generic reason "dated review record", so a newly invented file is accepted in one
# keystroke by naming it with a date. That is weaker than the PRESERVE list above,
# which requires a per-file reason. The residual is deliberate: these are dated
# records of completed runs, the directory is review-only, and requiring a real
# date still rejects the shapes that matter. Tighten it by moving each reviewed
# file into PRESERVE with its own reason, and the prefix rule with it.
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

    # git is a hard prerequisite: every case below, and the file scan itself,
    # shells out to it. Probe it FIRST, so a missing or too-old git is reported
    # as a self-test failure with an actionable message instead of escaping as
    # a traceback from whichever call site happens to run first. That is the
    # failure mode base_ref()'s own docstring says must never happen: a crash
    # that discards results already computed.
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError, OSError) as exc:
        print(f"  SELF-TEST FAIL: git is required and did not work here "
              f"({type(exc).__name__}: {exc}). Install git and ensure it is on "
              f"PATH; git 2.28+ is needed for --initial-branch.")
        return False

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

    # Exercise the REAL reporting function, not a copy of its loops. Two earlier
    # attempts failed here: literals asserted nothing, and a second copy of the
    # unpack loops was not the copy that runs, so the historical arity bug still
    # printed "Self-test passed" and exited 0. There is now exactly one place
    # these lists are unpacked -- report_findings -- and the self-test calls it
    # with every list non-empty, so a wrong arity raises for real.
    # Every list is forced non-empty: an empty list never executes its loop body,
    # so a wrong arity would not raise. The report is captured rather than
    # printed, because the self-test must not emit findings of its own.
    try:
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            report_findings(
                PRESERVE_SAMPLE or [("selftest.md:1", "text", "reason")],
                defects_sample() or [("selftest.md:2", "text", "reason")],
                wrong_dash_sample() or [("selftest.md:3", "text")],
                unrecognised_sample() or [("selftest.md:4", "text")],
            )
    except ValueError as exc:
        fail(f"report_findings unpacking is inconsistent: {exc}")

    # The trailer path must be exercised at its call site, not only through the
    # patterns. Each case below asserts the EXPECTED verdict, so a regression
    # that makes the check accept a bad value, or reject a good one, fails here.
    good_label = (f"Worker {EM} Torsten Maier_space-bunny-free-max_OpenCode (AI agent)")
    good_model = "model=opencode/space-bunny-free variant=max harness=OpenCode"
    # The trailer and file-scan cases below need git, already probed above.

    # Every key in TRAILER_KEYS is exercised, not just Contributed-by. Dropping
    # a single key from that tuple was previously invisible because every case
    # used the same key, so the tuple could be shortened without failing here.
    for key in TRAILER_KEYS:
        for body, expect_defect, why in (
            (f"{key}: {good_label}", False, f"a conforming {key} label"),
            (f"{key}: {good_label} (relayed by Reviewer {EM} Dennis Windmaier (AI agent))",
             True, f"a {key} label plus a relaying note"),
            (f"{key}: work done by {good_label} yesterday",
             True, f"a {key} label wrapped in prose"),
            (f"{key}: {good_label} zzz qqq",
             True, f"a {key} label plus trailing tokens"),
        ):
            found = _trailer_probe(why.replace(" ", "-").replace(":", ""), body)
            if bool(found) is not expect_defect:
                fail(f"trailer scan verdict wrong for {why}: "
                     f"expected {'defect' if expect_defect else 'clean'}, "
                     f"got {len(found)} finding(s)")

    for body, expect_defect, why in (
        (f"Model-used: {good_model}", False, "a conforming Model used: value"),
        (f"Model-used: space-bunny-free-max (OpenCode)", True, "free-text Model used:"),
        (f"Model-used: model-unconfirmed", True, "a bare sentinel, not keyed pairs"),
        (f"Model-used: model=opencode/space-bunny-free", True, "missing keys"),
        # A-5: the documented recovery rule, not a loose regex.
        (f"Model-used: variant=max model=opencode/space-bunny-free harness=OpenCode",
         False, "key order is unconstrained and must be accepted"),
        ("Model-used: model=opencode/space-bunny-free variant=max harness=banana",
         True, "harness outside the documented set"),
        ("Model-used: model=x variant=max harness=OpenCode extra=1",
         True, "a fourth key"),
        ("Model-used: model=x model=y variant=max harness=OpenCode",
         True, "a duplicated key"),
        ("Model-used: model= variant=max harness=OpenCode",
         True, "an empty model value"),
        ("Model-used: model=model-unconfirmed variant=variant-unconfirmed"
         " harness=harness-unconfirmed", False, "the all-unconfirmed keyed form"),
        # A-6: the prose spelling in a commit body is a defect, not an
        # alternative form, because the trailer grammar never sees it.
        (f"Model used: {good_model}", True, "the prose spelling in a commit body"),
    ):
        found = _trailer_probe(why.replace(" ", "-").replace(":", ""), body)
        if bool(found) is not expect_defect:
            fail(f"trailer scan verdict wrong for {why}: "
                 f"expected {'defect' if expect_defect else 'clean'}, "
                 f"got {len(found)} finding(s)")

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


def _purge(root: pathlib.Path) -> None:
    """Remove a fixture repo completely.

    `shutil.rmtree(ignore_errors=True)` silently fails here: git marks its
    object files read-only, so Windows refuses the delete and the directory
    survives. Ten fixture repos per run leaked on every invocation, including
    clean passing ones, until this was caught. Clear the read-only bit first and
    report rather than swallow a failure, because a leaked repo is a silent
    failure that accumulates.
    """
    import shutil
    import stat

    def _force(func, path, _exc):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    if not root.exists():
        return
    try:
        shutil.rmtree(root, onerror=_force)
    except OSError:
        # Last resort: leave it, but do not pretend it was removed.
        print(f"  WARNING: could not remove fixture repo {root}; delete it manually")


def _fixture_repo(tag: str) -> pathlib.Path:
    """A throwaway repo with a known short form, used to drive the real scans.

    The self-test must exercise the call sites, because the defects it is meant
    to catch live in the call sites: reinstating the M-1 regression, making the
    Model-used key unreachable, or loosening the date anchor all leave every
    compiled pattern untouched and pass a pattern-only test.
    """
    import tempfile
    root = pathlib.Path(tempfile.mkdtemp(prefix=f"labelchk-{tag}-"))
    try:
        (root / "scripts").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "team" / "reviews").mkdir(parents=True, exist_ok=True)
        (root / "scripts" / "check_identity_labels.py").write_text(
            pathlib.Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")
        for cmd in (["init", "--quiet", "--initial-branch=main", "."],
                    ["config", "user.email", "selftest@example.invalid"],
                    ["config", "user.name", "SelfTest"]):
            subprocess.run(["git", "-C", str(root), *cmd], capture_output=True, check=True)
        (root / "README.md").write_text("# fixture\n", encoding="utf-8")
        (root / "docs" / "live.md").write_text(
            f"Worker {EM} Torsten Maier (AI agent)\n", encoding="utf-8")
        (root / "docs" / "team" / "reviews" / "r-2026-10-01.md").write_text(
            f"Reviewer {EM} Dennis Windmaier (AI agent)\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "-A"], capture_output=True, check=True)
        subprocess.run(["git", "-C", str(root), "commit", "--quiet", "-m", "fixture"],
                       capture_output=True, check=True)
        # A second commit, so main..HEAD is non-empty and the trailer scan runs.
        subprocess.run(["git", "-C", str(root), "branch", "base"], capture_output=True)
        subprocess.run(["git", "-C", str(root), "checkout", "--quiet", "-b", "probe"],
                       capture_output=True, check=True)
        return root
    except BaseException:
        # A missing or too-old git must not strand a directory, and must not
        # escape as a traceback that discards the file results already computed.
        _purge(root)
        raise


def _git_in(root: pathlib.Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=True)


def defects_sample() -> list:
    """Real defects from the production scan_files, on a throwaway repo."""
    root = _fixture_repo("defects")
    try:
        (root / "docs" / "defect.md").write_text(
            f"Worker {EM} Torsten Maier (AI agent)\n", encoding="utf-8")
        _git_in(root, "add", "-A")
        _git_in(root, "commit", "--quiet", "-m", "live short form")
        _git_in(root, "commit", "--allow-empty", "--quiet", "-m", "probe")
        global ROOT
        saved = ROOT
        try:
            ROOT = _RootShim(root)
            return scan_files()[2]
        finally:
            ROOT = saved
    finally:
        _purge(root)


def wrong_dash_sample() -> list:
    """Real wrong-dash findings from the production scan_files."""
    root = _fixture_repo("dash")
    try:
        (root / "docs" / "dash.md").write_text(
            f"Worker - Torsten Maier_space-bunny-free-max_OpenCode (AI agent)\n",
            encoding="utf-8")
        _git_in(root, "add", "-A")
        _git_in(root, "commit", "--quiet", "-m", "ascii dash")
        _git_in(root, "commit", "--allow-empty", "--quiet", "-m", "probe")
        global ROOT
        saved = ROOT
        try:
            ROOT = _RootShim(root)
            return scan_files()[3]
        finally:
            ROOT = saved
    finally:
        _purge(root)


def unrecognised_sample() -> list:
    """Real 'unrecognised identity text' findings from the production scan."""
    root = _fixture_repo("unrec")
    try:
        (root / "docs" / "bad.md").write_text(
            f"Worker {EM} Torsten Maier_opencode/space-bunny-free_OpenCode (AI agent)\n",
            encoding="utf-8")
        _git_in(root, "add", "-A")
        _git_in(root, "commit", "--quiet", "-m", "malformed label")
        _git_in(root, "commit", "--allow-empty", "--quiet", "-m", "probe")
        global ROOT
        saved = ROOT
        try:
            ROOT = _RootShim(root)
            return scan_files()[4]
        finally:
            ROOT = saved
    finally:
        _purge(root)


def _files_sample(tag: str, index: int) -> list:
    """Call the REAL scan_files against a throwaway repo and return one of its
    finding lists.

    A private copy of scan_files used to live here, which is why a mutation in
    scan_files itself -- suppressing wrong-dash detection, say -- was invisible
    to the self-test, and why defects_sample() could silently return the wrong
    list. The production function is now called directly, via the same ROOT swap
    _trailer_probe uses.
    """
    root = _fixture_repo(tag)
    global ROOT
    saved = ROOT
    try:
        _git_in(root, "commit", "--allow-empty", "--quiet", "-m", "probe")
        ROOT = _RootShim(root)
        return scan_files()[index]
    finally:
        ROOT = saved
        _purge(root)


def _trailer_probe(tag: str, body: str) -> list:
    """Call the REAL scan_trailers over a throwaway repo whose HEAD carries `body`.

    The M-1 and M-2 defects live inside scan_trailers, not in the compiled
    patterns. A self-test that re-implements the scan cannot detect a change to
    the scan, so this temporarily points ROOT at the fixture and calls the
    production function itself. A regression in scan_trailers therefore fails
    here, which is the entire point.
    """
    root = _fixture_repo(tag)
    global ROOT
    saved = ROOT
    try:
        _git_in(root, "commit", "--allow-empty", "--quiet", "-m", f"probe\n\n{body}")
        ROOT = _RootShim(root)
        return scan_trailers("main")
    finally:
        ROOT = saved
        _purge(root)


class _RootShim:
    """Minimal stand-in so git("-C", str(ROOT), ...) targets the fixture repo."""

    def __init__(self, real: pathlib.Path):
        self._real = real

    def __str__(self) -> str:
        return str(self._real)

    def __truediv__(self, other):
        return self._real / other


PRESERVE_SAMPLE = [("f.md:1", "text", "reason")]


def _looks_like_identity(line: str) -> bool:
    """True when a line appears to intend an identity rather than describe one.

    The unrecognised-identity check must not fire on the documentation that
    defines the grammar. A template such as
    `<Role> <Configured name>_<model>-<variant>_<Harness> (AI agent)` and a
    sentence explaining the ` (AI agent)` suffix both contain the suffix, and
    reporting them would flag the very documents that specify the rule.

    An intended instance carries a role-like word, a separator, and an
    underscore-delimited tail. A template has angle brackets or a backticked
    slot where a value belongs; prose about the grammar names the fields instead
    of supplying them.
    """
    if "<" in line and ">" in line:
        return False
    if "`" in line:
        return False
    for marker in ("suffix", "separator", "delimited", "non-conforming",
                   "machine key", "recoverable", "template", "field rules"):
        if marker in line:
            return False
    # The underscore-delimited tail is the discriminator: an instance always has
    # model-variant_harness, a template slot is bracketed, and prose has neither.
    if not re.search(r"_[A-Za-z0-9][^_\s]*_[A-Za-z]", line):
        return False
    return bool(re.search(rf"[A-Za-z][A-Za-z ]*\s{re.escape(EM)}\s", line))


def scan_files() -> tuple[list, list, list, list, list]:
    """Scan tracked Markdown AND tracked role definitions.

    Role definitions are what actually generate published identities. A previous
    revision scanned only `*.md` and therefore could not see a non-canonical
    label in `.codex/agents/*.toml`, which is the surface most likely to drift.
    """
    paths = [p for p in git("ls-files", "*.md", "*.toml").split() if p]
    allowed: list[tuple[str, str, str]] = []
    defects: list[tuple[str, str, str]] = []
    wrong_dash: list[tuple[str, str]] = []
    unrecognised: list[tuple[str, str]] = []

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
            matched = bool(canonical_spans)
            for m in OLD_ANY.finditer(line):
                # A canonical label suppresses only a short form contained in its
                # own span. Suppressing the whole line would let any prose line
                # that names two identities hide a non-conforming one.
                if any(start <= m.start() and m.end() <= end
                       for start, end in canonical_spans):
                    continue
                matched = True
                (allowed if preserved(rel) else defects).append(
                    (entry, m.group(0), PRESERVE.get(rel, "dated review record")))
            # A line that claims to carry an identity but matches neither form is
            # reported rather than passed over. Previously a forbidden '/' or '#'
            # in the model slot, a lowercase role, or a space in the model token
            # made the label match nothing at all, so the line was never examined
            # and the run was green. A malformed label is still a published
            # identity; ignoring it is the same defect as accepting it.
            #
            # A template slot or prose about the grammar is not an identity, and
            # reporting those would make the check unusable: the Code of Conduct
            # documents the form with `<Role>` placeholders and explains the
            # fields, and neither is a published identity. So a line is only
            # reported when it looks like an intended instance -- it carries the
            # suffix and a plausible role/name shape -- rather than a template or
            # an explanation.
            if not matched and _looks_like_identity(line):
                unrecognised.append((entry, line.strip()))
    return paths, allowed, defects, wrong_dash, unrecognised


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
            if not sep:
                continue
            key = key.strip()
            if key == "Model-used":
                if not model_used_ok(value.strip()):
                    bad.append((sha.strip()[:7], line.strip()))
            elif re.fullmatch(r"Model\s+used", key, re.IGNORECASE):
                # CODE_OF_CONDUCT.md:81 requires the hyphenated key inside a
                # trailer so `git interpret-trailers` accepts it. The prose
                # spelling appearing in a commit body is therefore a defect, not
                # an alternative form: it is unchecked by the trailer grammar
                # and would otherwise pass in silence.
                bad.append((sha.strip()[:7], line.strip()))
    return bad


def report_findings(allowed, defects, wrong_dash, unrecognised) -> None:
    """Print the file-scan findings.

    This is the ONLY place these four lists are unpacked. A previous revision
    unpacked them here and again, independently, inside self_test(): reinstating
    the wrong arity in main()'s copy still printed "Self-test passed" and exited
    0, because the copy the self-test exercised was not the copy that ran. A
    duplicated loop cannot guard the original, so the self-test now calls this
    function and any arity mismatch here fails the self-test for real.
    """
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
    print()
    print(f"Identity text matching neither the canonical nor the short form "
          f"(must be zero): {len(unrecognised)}")
    for entry, snippet in unrecognised:
        print(f"  DEFECT  {entry}  {snippet}")
        print("          A line carrying '(AI agent)' must be a recognised identity.")
        print("          A forbidden '/' or '#' in the model slot, a lowercase role, or a")
        print("          space in the model token makes the label match nothing, which is")
        print("          why this is checked rather than inferred from a missing match.")


def main() -> int:
    # --allow-skip is the only way to accept a trailer scan that could not run.
    # It is a flag rather than a default because "not checked" and "passed" must
    # not share an exit status, and because accepting the gap should be a
    # visible decision by whoever runs the check.
    allow_skip = "--allow-skip" in sys.argv[1:]
    if any(a not in ("--allow-skip",) for a in sys.argv[1:]):
        print(f"Unknown argument. Usage: {pathlib.Path(__file__).name} [--allow-skip]")
        return 1
    print("Identity label check")
    if allow_skip:
        print("(--allow-skip given: a skipped trailer scan will not fail the run)")
    print()

    if not self_test():
        print("Self-test failed; patterns are not trustworthy. No results reported.")
        return 1
    print("Self-test passed: all 11 configured names detected in both forms,")
    print("wrong-dash labels detected and rejected, placeholder slots ignored,")
    print("report_findings unpacking consistent, every trailer key exercised,")
    print("date and sentinel rules checked, git prerequisite confirmed.")
    print()

    paths, allowed, defects, wrong_dash, unrecognised = scan_files()

    print(f"Tracked Markdown and role-definition files scanned: {len(paths)}")
    print()
    report_findings(allowed, defects, wrong_dash, unrecognised)

    ref = base_ref()
    # A skip is not a pass. Exit 0 for a trailer scan that never ran would let a
    # green status stand for a check that did not execute, which is how four
    # negative controls once passed vacuously. Distinct status 2, overridable
    # only by an explicit --allow-skip, so the exemption is a decision.
    trailer_checked = True
    if ref is None:
        print()
        print("Trailer check SKIPPED: no base ref found (tried origin/main, main,")
        print("origin/master, master). This is a tooling limitation, not a pass.")
        trailer_bad: list[tuple[str, str]] = []
        trailer_checked = False
    else:
        trailer_bad = scan_trailers(ref)
        ahead = git("rev-list", "--count", f"{ref}..HEAD").strip()
        print()
        if ahead in ("", "0"):
            print(f"Trailer check inspected nothing: HEAD is {ref}, or has no commits")
            print("beyond it. Report this as not checked, not as a pass.")
            trailer_checked = False
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
    print("Exit status: 0 pass, 1 defect found, 2 not fully checked (see --allow-skip).")
    print("Known limit: a file under docs/team/reviews/ is exempt on a real date alone,")
    print("without its own reason. Requires git on PATH, 2.28+ for --initial-branch.")
    print("Untracked Markdown is not scanned, so a new unpublished record is not checked.")

    if defects or wrong_dash or unrecognised or trailer_bad:
        return 1
    if not trailer_checked and not allow_skip:
        print()
        print("NOT CHECKED: the trailer scan did not run, so this is not a pass.")
        print("Re-run against a full clone with a base ref, or pass --allow-skip to")
        print("accept the gap deliberately.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
