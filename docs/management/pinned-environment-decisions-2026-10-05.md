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

**What was changed, and where — all four sites.** The **Was** column is
`origin/main` (`9a1693b`). The **Now (line)** column gives the line **at `68fcb39`**,
and each row also names the **form** of the assertion, which does not drift at all.

| File | Was (`9a1693b`) | Now (line) | Form | Was | Now |
| --- | --- | --- | --- | --- | --- |
| `scripts/milestone_a_runner.py` | 157 | 197 | `platform.python_version() ==` | `3.12.14` | `3.12.10` |
| `scripts/milestone_a_runner.py` | 218 | 266 | `require(platform.python_version() ==` | `3.12.14` | `3.12.10` |
| `scripts/milestone_a.ps1` | 18 | 18 | `sys.version_info[:3] == (3,12,…)` | `(3,12,14)` | `(3,12,10)` |
| `scripts/milestone_a.sh` | 55 | 55 | `sys.version_info[:3] == (3,12,…)` | `(3,12,14)` | `(3,12,10)` |

**Read the form column, not the line column, when checking this table.** The line
numbers are accurate at `68fcb39` and will drift the moment a commit inserts lines
above them. That has already happened twice on this branch: an earlier version of
this table carried `184` and `253`, which were correct at `a98a31d` and wrong by
exactly the 13 lines that commit inserted. A third revision of this table is
therefore not a fix; the durable form is the assertion's *shape*, which is what
the form column gives.

A fifth site was found by review of the first version of this change and fixed
with it: `scripts/milestone_a.sh:178` printed the resolved-dependency evidence
list from a hard-coded alternation that omitted `typing_extensions`, so once that
pin was added the evidence block showed **7 of 8 pins**. It is a hard-coded
enumeration of the pinned set in the same style as the version pins, and a new
pin silently invalidated it — the same defect class, in the same file. See D2.

**This enumeration is still hard-coded and remains a known residual risk.** A
ninth pin added to the lock file would drop out of that evidence block again, with
no error. The runner's own `inventory()` does not have this problem — it walks the
lock file line by line and reports every pin it finds — so the correct fix is to
make the shell evidence block walk the lock file too, rather than restating it.
Recorded as a known residual rather than fixed here, because the shell block is on
the legacy combined path and not the Windows pinned path.

**A defect this record exists to prevent.** The first attempt changed only
`milestone_a_runner.py`'s `main()` interpreter gate and left the other three
sites at `3.12.14`. Those
three are **invisible to a plain text search for `3.12.14`** at the two wrapper
sites, because they express the version as a **tuple literal** `(3,12,14)` with
no dots. The defect survived a reviewer reading the diff and survived the author
reading their own change. A version tuple is the standard way to express this
value in Python, so the tuple notation is not exotic; it is the **more** likely
form.

Independently reproduced on the parent commit:
`git grep -n '3\.12\.14' 9a1693b -- scripts/milestone_a.ps1 scripts/milestone_a.sh`
returns **nothing, exit 1**, while `git grep '3,12,14' 9a1693b` returns both
wrapper sites.

**The rule that generalises this** — that a replaced value must be searched in
every notation it could take — is **proposed, not standing**. It is being added to
the Code of Conduct in PR #396, which is **unmerged**; no such section exists in
`CODE_OF_CONDUCT.md` on `main` today. It is cited here as the rule this change
follows, not as an authority already in force. A review of this branch found the
first version of this record citing that section as though it existed, which is
the same fabricated-authority defect this record was created to prevent.

**What was deliberately not done.** The gate was **not removed**. An unpinned
interpreter must still be refused; removing the check would convert a wrong
interpreter into a silent one, which is worse than a refusal.

## D2 — `typing_extensions` is now pinned

`typing_extensions` was **absent** from `requirements-milestone-a.txt` while being
installed as a transitive dependency. That made the pinned set **incomplete**:
the file claimed a fully reproducible resolved set
(`"Pins are exact == for every distribution in the resolved set, including the
transitive ones"`), and an unpinned transitive dependency falsifies that claim.
Any environment could resolve a different `typing_extensions` and still satisfy
the file.

**Which package actually requires it — corrected.** An earlier draft of this
record said `typing_extensions` is *"a transitive dependency of Django"*. **That
is false.** Django 5.2.17 declares only `asgiref>=3.8.1`, `sqlparse>=0.3.1` and
`tzdata; sys_platform == "win32"`. The live requirement on this interpreter comes
from **`psycopg`**: `typing-extensions>=4.6; python_version < "3.13"`.

This matters for a reason beyond accuracy: because psycopg's marker is
`python_version < "3.13"`, **`typing_extensions` is not required at all on Python
3.13**. The pin is still correct to add — it makes the resolved set explicit
rather than marker-dependent — but a maintainer who believed the Django story
would mis-predict which interpreters need it.

**Decision.** `typing_extensions==4.16.0` is pinned, matching the version present
in the verified environment.

**Consequence — the lock value changes.** The pinned command prints
`lock_sha256`, defined as the SHA-256 of the bytes of
`requirements-milestone-a.txt` as they sit in the working tree. **Any historical
evidence quoting a previous value refers to a different file and must not be
compared against a run of the current one.**

The current value is `885474fea81cedef49fcc6138d9710e8bd7d9547c5914449c9d06e300d3c4f87`.

**Read this before quoting any value: `lock_sha256` is not portable.** The runner
hashes working-tree bytes via `lock.read_bytes()`, and a checkout with
`core.autocrlf=true` produces **CRLF** while an LF checkout produces different
bytes and therefore a different hash. On this branch the CRLF working tree yields
the value above; the LF blob in the repository yields `957b7c68...`. This is
pre-existing on `main` and not introduced here, but it means *"the current
value"* is a statement about a checkout, not about the repository. Quote the hash
together with the line-ending form it was taken under, or do not quote it at all.

**A correction, made after this number was already wrong once.** An earlier
version of this record asserted a **superseded** hash as the current one. It was
caught on re-review and is recorded here rather than quietly replaced, because a
hash stated as current and wrong is worse than no hash: it lets two runs be
compared when they are not comparable.

**Note on the token's name.** The runner prints `lock_sha256`; the requirements
header and the `milestone_a.sh` combined path call the same value
`pinned_dependency_lock_sha256`. Two names for one token, pre-existing on `main`
and not introduced here, but a real confusion risk for anyone grepping evidence.

## Scope of this record

This record covers **the interpreter pin and the pinned dependency set only.**

An earlier draft also carried a section on the **SR70** conflict, describing SR70
as *"it requires persistence"* and stating that phasing was selected with *"a
named successor increment"*. **Both were removed as incorrect on review:**

- SR70 is `[SR][backend]Reject invalid model output before assessment persistence`
  (`docs/management/system-requirements.md:62`). It is a requirement to **reject**
  invalid model output *before* it reaches persistence — a validation gate. It
  does **not** require the system to persist anything; persistence is the thing
  whose entrance it guards. The draft inverted its meaning.
- No successor increment was ever named, so the claim asserted a traceability
  link that does not exist.

The phasing decision belongs in requirement-traceability documentation with the
real SR70 wording and a real successor ID. Asserting it here, in a record cited as
the authority for the interpreter pin, would have made a reader who trusted the
pin decision inherit an unfounded assertion about a P0 backend requirement.

**This record does not waive SR70 or any other requirement.**

## Verification performed for this record

- All four pin sites searched in **both** notations (dotted and tuple). The
  tuple-only sites do not match a dotted search; that was verified on the parent
  commit, not assumed.
- The two wrapper files were opened and read at the cited lines.
- `docs/management/pinned-environment-decisions-2026-10-05.md` is created by this
  change, so the runner's citation of this file now resolves, and the target is
  **tracked at `HEAD`**, not merely present in a working tree.
- The requirements file was diffed against the **installed** distribution set in
  the 3.12.10 environment; all eight non-`pip` distributions are pinned exactly
  and `pip` is reported separately by the runner.
- `lock_sha256` was confirmed equal to an independently computed SHA-256 of the
  requirements file, and confirmed to **change** when a pin changes.

**Citations in this record are given as file plus form, not file plus line
number**, wherever a line number would drift as the cited file grows. The site
table above is the one exception: it carries both the `origin/main` line and the
line at this head, so a reader can check either. An earlier version of this record
cited bare line numbers that all became wrong when a later commit inserted lines
above them — the same defect class as citing a document that does not exist, in a
milder form, and the reason the convention changed.

## Known defects in this branch's history, recorded rather than erased

**`be793e7`, the first commit on this branch, is defective and was not rewritten.**

- Its **Git author** is `Worker - Torsten Maier`, with an ASCII hyphen, while its
  `Implemented-by` trailer names the Primary Coordinator. The two disagree, and
  the author's dash is non-canonical.
- Its **published commit message contains two literal `@@EM@@` placeholder
  tokens** where an em dash belongs, visible on the pull request.
- Its message asserts **"328 tests, OK"**, a figure that no later run on this
  branch reproduces; the current count is 316.

**Why history was not rewritten.** Two completed independent reviews cite
`be793e7`, `cfdf898` and `78be377` as the heads they reviewed. Rebasing to
correct the author and the message would change every SHA on the branch and
invalidate those reviews' head bindings — trading a cosmetic defect in one old
commit for a broken evidence trail across the whole pull request. The defect is
recorded here instead.

**`scripts/check_identity_labels.py` does not catch any of this.** It regex-scans
commit *message lines* for trailer keys. It never reads the Git author (`%an`) and
never inspects the message body, so its exit 0 proves nothing about either defect.
**A green identity-label result is not evidence that attribution metadata is
correct**, and this branch is a concrete demonstration.

**Host observation, not a repository fact.** The 3.12.10 interpreter on the
machine this change was produced and verified on lives at
`C:\Users\guofe\AppData\Local\Programs\Python\Python31210`. That is a property of
one host, not of the repository, and no other host needs the same path.

**Not verified here.** The `migrate`, `install` and `app-check` phases were **not**
run end to end in this session; `migrate` and `app-check` assert different
privilege shapes and remain unexercised. The `test` phase was run and passed; see
the pull request for its output, which this record deliberately does not duplicate.
Nothing here is a claim that any phase other than `test` passed.
