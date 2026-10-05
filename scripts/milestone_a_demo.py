"""Milestone A end-to-end demonstration harness.

Drives the real DATARA chain against real PostgreSQL with real FIT bytes:

    SDK Encoder -> classify_bytes -> plan_import -> OriginalStore -> eligibility

No mocks, no stubs, no hand-assembled FIT bytes. Every FIT file here is written by
the pinned SDK's own encoder, so this exercises the input class the repository's
tests never covered.

Run with the pinned interpreter and DJANGO_SETTINGS_MODULE=datara.settings.
Prints a report; writes nothing to the repository.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.environ.get("DATARA_SRC", os.path.dirname(os.path.abspath(__file__))))

import django  # noqa: E402

django.setup()

from garmin_fit_sdk.encoder import Encoder  # noqa: E402

from datara import intake, storage  # noqa: E402
from datara.classification import classify_bytes, pinned_profile  # noqa: E402

PROFILE = pinned_profile()
MESG = PROFILE["mesg_num"]


def _by_name(mapping: dict[int, str]) -> dict[str, int]:
    """The pinned profile maps enum value -> name; the encoder needs name -> value."""

    return {name: value for value, name in mapping.items()}


FILE = _by_name(PROFILE["file"])
SPORT = _by_name(PROFILE["sport"])
SUBSPORT = _by_name(PROFILE["sub_sport"])

FILE_ID = MESG["FILE_ID"]
SESSION = MESG["SESSION"]
ACTIVITY = MESG["ACTIVITY"]

# A FIT-epoch timestamp comfortably above the pinned minimum 268435456.
BASE_TS = 1_700_000_000


def fit_bytes(
    *,
    sport: int,
    sub_sport: int,
    elapsed_ms: int,
    timer_ms: int,
    distance_cm: int,
    start_ts: int = BASE_TS,
    num_sessions: int | None = None,
    with_activity: bool = True,
) -> bytes:
    """Write one single-session FIT file with the pinned SDK's encoder."""

    enc = Encoder()
    enc.write_mesg(
        {
            "mesg_num": FILE_ID,
            "type": FILE["activity"],
            "manufacturer": 1,
            "product": 1,
            "serial_number": 1,
            "time_created": start_ts,
        }
    )
    if with_activity:
        activity = {
            "mesg_num": ACTIVITY,
            "timestamp": start_ts,
            "total_timer_time": timer_ms / 1000.0,
        }
        if num_sessions is not None:
            activity["num_sessions"] = num_sessions
        enc.write_mesg(activity)
    enc.write_mesg(
        {
            "mesg_num": SESSION,
            "sport": sport,
            "sub_sport": sub_sport,
            "start_time": start_ts,
            "total_elapsed_time": elapsed_ms / 1000.0,
            "total_timer_time": timer_ms / 1000.0,
            "total_distance": distance_cm / 100.0,
            "num_active_samples": 10,
        }
    )
    return enc.close()


RUNNING = SPORT["running"]
CYCLING = SPORT["cycling"]
ROAD = SUBSPORT["road"]
TRAIL = SUBSPORT["trail"]

CASES = [
    ("baseline: road running", dict(sport=RUNNING, sub_sport=ROAD,
     elapsed_ms=1_800_500, timer_ms=1_800_500, distance_cm=5_000_000)),
    ("baseline: trail running", dict(sport=RUNNING, sub_sport=TRAIL,
     elapsed_ms=1_200_000, timer_ms=1_150_000, distance_cm=3_000_000)),
    ("baseline: road cycling", dict(sport=CYCLING, sub_sport=ROAD,
     elapsed_ms=2_400_000, timer_ms=2_300_000, distance_cm=9_000_000)),
    ("C6: cross-sport running + road", dict(sport=RUNNING, sub_sport=ROAD,
     elapsed_ms=900_000, timer_ms=900_000, distance_cm=2_500_000)),
    ("C7 / D-A2: sub_sport = 254 all", dict(sport=RUNNING, sub_sport=254,
     elapsed_ms=900_000, timer_ms=900_000, distance_cm=2_500_000)),
    ("C10 / D-A4: no activity message", dict(sport=RUNNING, sub_sport=ROAD,
     elapsed_ms=900_000, timer_ms=900_000, distance_cm=2_500_000, with_activity=False)),
    ("D-A4: activity present, num_sessions absent", dict(sport=RUNNING, sub_sport=ROAD,
     elapsed_ms=900_000, timer_ms=900_000, distance_cm=2_500_000, with_activity=True)),
    ("D-A4: activity present, num_sessions = 1", dict(sport=RUNNING, sub_sport=ROAD,
     elapsed_ms=900_000, timer_ms=900_000, distance_cm=2_500_000, num_sessions=1)),
]


def rule(char: str = "-") -> None:
    print(char * 78)


def classify_all() -> dict[str, tuple]:
    rule("=")
    print("STAGE 1  classify_bytes  (pinned profile, no mocks)")
    rule("=")
    results = {}
    for name, kwargs in CASES:
        data = fit_bytes(**kwargs)
        out = classify_bytes(data)
        results[name] = (data, out)
        mark = "ACCEPT" if out.accepted else "REJECT"
        print(f"  [{mark}] {name}  ({len(data)} B)")
        if out.accepted:
            print(f"          sport={out.sport_name}  sub_sport={out.sub_sport_name}")
            print(f"          elapsed_ms={out.elapsed_duration_ms}  "
                  f"timer_s={out.timer_duration_seconds}  dist_m={out.total_distance_metres}")
            print(f"          start_utc={out.start_time_utc}")
            print(f"          warnings={list(out.warnings)}")
        else:
            print(f"          reason={out.reason_code}")
            print(f"          detail={out.reason_detail}")
    return results


def intake_all(results: dict[str, tuple]) -> None:
    rule("=")
    print("STAGE 2  plan_import  (deterministic intake, per owner)")
    rule("=")
    for name, (data, out) in results.items():
        if not out.accepted:
            print(f"  [skip]  {name}: not accepted, intake never reached")
            continue
        plan = intake.plan_import("demo-owner", [(f"{name}.fit", data)])
        print(f"  [plan]  {name}")
        print(f"          accepted={len(plan.accepted)}  rejected={len(plan.rejected)}  "
              f"duplicates={len(plan.duplicates)}  quarantined={len(plan.quarantined)}")
        print(f"          rule_version={plan.rule_version}")
        for item in plan.rejected:
            print(f"          reject: {item.reason_code}")
        for item in plan.quarantined:
            print(f"          quarantine: {getattr(item, 'reason_code', item)}")


def main() -> int:
    print()
    print("DATARA Milestone A - end-to-end demonstration")
    print("SDK-generated FIT bytes -> classify -> plan -> (store) -> eligibility")
    print()
    results = classify_all()
    intake_all(results)
    rule()
    accepted = sum(1 for _, (_, o) in results.items() if o.accepted)
    print(f"SUMMARY  {accepted}/{len(results)} cases accepted at classification")
    rule()
    return 0


if __name__ == "__main__":
    sys.exit(main())