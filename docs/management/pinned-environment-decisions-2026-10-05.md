# Pinned environment decisions, 2026-10-05

Dated record of the interpreter pin change and the pinned dependency set. This
record exists because `scripts/milestone_a_runner.py` cites it; a rule that cites
a document which does not exist is a fabricated authority.

Attribution: Primary Coordinator — Yi Tang_space-bunny-free-xhigh_OpenCode (AI agent)
Model-used: model=opencode/space-bunny-free variant=xhigh harness=OpenCode
Agent-run: unavailable — this runtime exposes no execution link or session id
Assignment: #392

## D1 — The interpreter pin moves from 3.12.14 to 3.12.10

**Decision.** The candidate interpreter pin is **3.12.10**.

**Founder instruction.** On 5 October 2026 the founder directed: *"find a suitable
python version which is working in current environment"*, and authorised
installing what was needed. **3.12.10** was selected and recorded at the time as
the nearest official 3.12.x interpreter that actually runs on this host.

**Why the original pin was unsatisfiable.** `3.12.14` has **no official Windows
build**. python.org publishes source only for 3.12.11 and later, verified against
the FTP listing, the release pages, and the nuget.org `python` package index. A
pin that no obtainable interpreter can satisfy is not a pin; it is a permanent
refusal.

**What was changed, and where — all four sites.**

| File | Line | Form | Was | Now |
| --- | --- | --- | --- | --- |
| `scripts/milestone_a_runner.py` | 157 | `platform.python_version() ==` | `3.12.14` | `3.12.10` |
| `scripts/milestone_a_runner.py` | 226 | `require(platform.python_version() ==` | `3.12.10` | already correct |
| `scripts/milestone_a.ps1` | 18 | `sys.version_info[:3] == (3,12,…)` | `(3,12,14)` | `(3,12,10)` |
| `scripts/milestone_a.sh` | 55 | `sys.version_info[:3] == (3,12,…)` | `(3,12,14)` | `(3,12,10)` |

**A defect this record exists to prevent.** The first attempt changed only
`milestone_a_runner.py:226` and left the other three sites at `3.12.14`. Those
three are **invisible to a plain text search for `3.12.14`** at the two wrapper
sites, because they express the version as a **tuple literal** `(3,12,14)` with
no dots. The defect survived a reviewer reading the diff and survived the author
reading their own change. The gate condition in `CODE_OF_CONDUCT.md` §"Pre-review
readiness gate" — *a replaced value is searched in every notation it could take* —
exists because of this. A version tuple is the standard way to express this
value in Python, so the tuple notation is not exotic; it is the **more** likely
form.

**What was deliberately not done.** The gate was **not removed**. An unpinned
interpreter must still be refused; removing the check would convert a wrong
interpreter into a silent one, which is worse than a refusal.

## D2 — `typing_extensions` is now pinned

`typing_extensions` was **absent** from `requirements-milestone-a.txt` while being
installed as a transitive dependency of Django. That made the pinned set
**incomplete**: the file claimed a fully reproducible resolved set
(`"Pins are exact == for every distribution in the resolved set, including the
transitive ones"`), and an unpinned transitive dependency falsifies that claim.
Any environment could resolve a different `typing_extensions` and still satisfy
the file.

**Decision.** `typing_extensions==4.16.0` is pinned, matching the version present
in the verified environment.

**Consequence — the lock value changes.** The pinned command prints
`pinned_dependency_lock_sha256`, defined as the SHA-256 of
`requirements-milestone-a.txt` itself. **Any historical evidence quoting the
previous value refers to a different file and must not be compared against a run
of the current one.** The superseded value is recorded here rather than deleted.

## D3 — A recorded conflict resolved by phasing, not by adding persistence

`SR70` conflicted with the Milestone A requirement set: it requires persistence,
and Milestone A explicitly makes none. The founder selected **phasing** — SR70 is
satisfied in a later increment and Milestone A introduces no persistence.

**This record does not waive SR70.** It is a dated commitment with a named
successor increment, not a removed requirement.

## Verification performed for this record

- All four pin sites searched in **both** notations (dotted and tuple), not one.
- The two wrapper files were opened and read at the cited lines; neither site
  matched a dotted search before this change.
- `docs/management/pinned-environment-decisions-2026-10-05.md` is created by this
  change, so the citation at `milestone_a_runner.py:219` now resolves.
- The 3.12.10 interpreter is installed at
  `C:\Users\guofe\AppData\Local\Programs\Python\Python31210` and its `sys.version_info[:3]`
  is `(3, 12, 10)`, matching all four sites.

**Not verified here.** The full pinned command has **not** been run end to end
against every phase on this branch; that is tracked separately, and no claim of a
pinned-command pass is made by this record.
