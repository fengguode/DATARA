# FIT profile enum derivation — method and verified inputs (2 October 2026)

Status: **source evidence and derivation method** for the allowlists frozen by the 2 October
2026 decisions in [`fit-support-matrix.md`](../../p0-design/fit-support-matrix.md) §12. This is
not a conformance result, not a verified requirement, not an acceptance and not a release.
`TC01`, `TC19`, `TC25` remain **Not run / unverified**.

Trace: WP01, TK10 (#116), STK003 (#175), STK004 (#176), TK11 (#117), TK15 (#121); CUS01,
FEAT01, SR01, SR02, SR27, SR32, D01. System Architect — Feng Guo.

## 1. Which artifact the allowlists are derived from, and how that was confirmed

The 1 October matrix recorded MAP01 as the pinned `profile.py` at commit
`6db34d7958dce3cef89194e82d6bdc9437c810de`, SHA-256
`cfc2737638285d1ec09d2972e4bc88b30b4b5a5bc07bfcd843669e7c92cb865c`, 967399 bytes
(`fit-support-matrix.md:13`, `fit-source-inventory.md:16` / SRC02).

**Verified on 2 October 2026.** A copy of `garmin_fit_sdk/profile.py` present in a local
virtual environment was hashed and the digest compared to the recorded MAP01 value:

| Check | Recorded (MAP01 / SRC02) | Computed locally on 2 October 2026 | Match |
| --- | --- | --- | --- |
| SHA-256 | `cfc2737638285d1ec09d2972e4bc88b30b4b5a5bc07bfcd843669e7c92cb865c` | `cfc2737638285d1ec09d2972e4bc88b30b4b5a5bc07bfcd843669e7c92cb865c` | **Yes** |
| Byte length | 967399 | 967399 | **Yes** |

Two further independent copies in separate local environments produced the same digest, so
the allowlists below are derived from the *pinned* profile bytes and not from a
same-version-but-different artifact. This closes the "which bytes" question for this
increment only. It does **not** close package-byte verification for the published wheel
(`fit-source-inventory.md:25`), and the SDK was not imported, executed or vendored into
DATARA to produce these values.

Literal metadata also re-confirmed from those bytes: `Profile.version` = 21.217.0 `Release`
(`profile.py:13-19`), generation tag `production/release/21.217.0-0-g248b1c46`
(`profile.py:8-9`).

## 2. Derivation method, stated so it can be audited and repeated

1. **Parse, do not import.** `profile.py` is a literal dict assignment named `Profile`
   (`profile.py:13`). Values were extracted with Python's `ast` module, so the file was read
   and never imported. The SDK's own code paths were not exercised.
2. **Enum membership from the AST**; the *sport tag* on a sub-sport is **not** in the AST,
   because the publisher writes it as a trailing `#` comment. Sport tags were therefore read
   from the literal line text, and each value's source line number is recorded below so any
   row can be checked by opening one line.
3. **Enumerated counts as a completeness check.** `sub_sport` has **112** values,
   `sport` **82**, `file` **20**, `activity` **2**. The 112 sub-sport values partition as
   9 running + 19 cycling − 1 shared + 84 assigned to neither + 1 (`254`) = 112. The
   partition is exhaustive, so no sub-sport value is unaccounted for.
4. **A name is not a location.** The profile declares no indoor/outdoor flag on
   `sub_sport` or on `session` (18); the full `session` field list was enumerated and
   contains no such field. The enum *name* is therefore the only available evidence, which is
   why the classification rule in matrix §12.3 is stated as a strict, positive-evidence rule
   rather than a best guess.

## 3. The `254` ("all") values — verified, and the two are not equally evidenced

| Value | Line | Literal profile entry | Evidenced as goals-only? |
| --- | --- | --- | --- |
| `sport` `254` | `profile.py:27269` | `254: 'all', # All is for goals only to include all sports.` | **Yes — publisher comment, verbatim.** |
| `sub_sport` `254` | `profile.py:27446` | `254: 'all',` | **No — the entry carries no comment.** |

This asymmetry is load-bearing and is recorded rather than smoothed over. The goals-only
reading is **verified** for `sport` and is **inferred by analogy** for `sub_sport`. The
inference is nevertheless sound on independent grounds: the profile's `file` enum contains
`11: 'goals'` (a goals file is its own file category), and a value that asserts "all sports"
is a multi-sport aggregate, which cannot be a single running or cycling session. Matrix
§12.4 records the disposition for each and labels the reasoning separately.

## 4. The `file` enum — verified, and it contradicts a naming assumption

`profile.py` `types.file`, 20 values, extracted in full: `1 device`, `2 settings`,
`3 sport`, `4 activity`, `5 workout`, `6 course`, `7 schedules`, `9 weight`, `10 totals`,
`11 goals`, `14 blood_pressure`, `15 monitoring_a`, `20 activity_summary`,
`28 monitoring_daily`, `32 monitoring_b`, `34 segment`, `35 segment_list`,
`40 exd_configuration`, `247 mfg_range_min`, `254 mfg_range_max`.

**There is no `wellness` value.** This confirms the observation behind the correction in
matrix §12.6: wellness and monitoring data are carried under *five* separate file
categories, not one. The correction concerns completeness, not the premise.

## 5. Licence observation — recorded, and it does not resolve #319/#320

`profile.py:2-3` carries the publisher's own header notice: *"Licensed under the Flexible
and Interoperable Data Transfer (FIT) Protocol License."* `fit-source-inventory.md:16`
(SRC02) already recorded "Header names FIT Protocol License", and SRC03 records that
`pyproject.toml` "Refers to LICENSE, which was absent at this commit", with SRC06 recording
that `LICENSE.txt` and `LICENSE` both return 404 at the selected commit.

A copyright header in a generated source file is **not** the artifact's licence text and
establishes no permitted use, no redistribution right and no obligation set. It is recorded
here only because it is the strongest licence-bearing text that exists *inside* the pinned
bytes, and because it should not be silently promoted to a rights conclusion. Applicable
terms remain for the authorized owner under #319/#320. No terms were accepted and no legal
conclusion is drawn here.

## 6. What this note does not establish

- No protocol conformance. The FIT protocol prose was never substantively captured
  (`fit-source-inventory.md:19`, SRC05), so header-flag semantics, reserved values and
  integrity exceptions remain unevidenced.
- No fixture oracle and no lawful fixture exists (`fit-source-inventory.md:36`).
- No coverage claim. Enumerating the enum says what the profile *can* express; it says
  nothing about what files in the supported population actually contain.
- Nothing is Done, Verified, Accepted or released.
