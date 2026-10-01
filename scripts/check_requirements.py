"""Check requirement links and planned coverage; this does not validate the product."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
r = json.loads(
    (ROOT / "docs/management/requirements-registry.json").read_text(encoding="utf-8")
)
errors = []
if r.get("schema_version") != "2.0":
    errors.append("Expected CUS/SR registry schema version 2.0")
def index(name):
    rows = r[name]
    ids = [x["id"] for x in rows]
    if len(ids) != len(set(ids)):
        errors.append(f"Duplicate IDs in {name}")
    return {x["id"]: x for x in rows}
c = index("customer_user_stories")
s = index("system_requirements")
t = index("verification_cases")
w = index("work_packages")
k = index("tasks")
for cid, x in c.items():
    if not re.fullmatch(r"CUS\d{2}", cid):
        errors.append(f"{cid}: invalid CUS identifier")
    if not x.get("story", "").strip():
        errors.append(f"{cid}: missing customer or user story")
for sid, x in s.items():
    if not re.fullmatch(r"SR\d{2}", sid):
        errors.append(f"{sid}: invalid SR identifier")
    parents = x.get("cus_ids", [])
    if (not isinstance(parents, list) or not parents or
            any(not isinstance(cid, str) for cid in parents) or
            len(parents) != len(set(parents))):
        errors.append(f"{sid}: missing or duplicate CUS parents")
        parents = []
    for cid in parents:
        if cid not in c:
            errors.append(f"{sid}: unknown CUS parent {cid}")
    known_parents = [c[cid] for cid in parents if cid in c]
    if known_parents and x["priority"] != ("P0" if any(parent["priority"] == "P0" for parent in known_parents) else "P1"):
        errors.append(f"{sid}: priority differs from highest-priority CUS parent")
    if x["work_package"] not in w:
        errors.append(f"{sid}: unknown work package")
    if not x["verification_ids"]:
        errors.append(f"{sid}: no planned verification")
    for tid in x["verification_ids"]:
        if tid not in t:
            errors.append(f"{sid}: unknown verification {tid}")
for cid in c:
    if not any(cid in x.get("cus_ids", []) for x in s.values()):
        errors.append(f"{cid}: no derived system requirements")
for wid, x in w.items():
    for dep in x["dependencies"]:
        if dep not in w:
            errors.append(f"{wid}: unknown dependency {dep}")
for kid, x in k.items():
    if x["work_package"] not in w:
        errors.append(f"{kid}: unknown work package")
    if not x["requirement_ids"]:
        errors.append(f"{kid}: no linked requirements")
    for rid in x["requirement_ids"]:
        if rid not in c and rid not in s:
            errors.append(f"{kid}: unknown requirement {rid}")
    if not x["verification_ids"]:
        errors.append(f"{kid}: no planned verification")
    for tid in x["verification_ids"]:
        if tid not in t:
            errors.append(f"{kid}: unknown verification {tid}")
    for dep in x["dependencies"]:
        if dep not in k:
            errors.append(f"{kid}: unknown task dependency {dep}")
# Detect cyclic task dependencies.
task_visiting, task_done = set(), set()
def visit_task(kid):
    if kid in task_visiting:
        errors.append(f"Task dependency cycle at {kid}")
        return
    if kid in task_done: return
    task_visiting.add(kid)
    for dep in k[kid]["dependencies"]:
        if dep in k: visit_task(dep)
    task_visiting.remove(kid)
    task_done.add(kid)
for kid in k: visit_task(kid)
linked_requirements = {rid for x in k.values() for rid in x["requirement_ids"]}
for rid in set(c) | set(s):
    if rid not in linked_requirements:
        errors.append(f"{rid}: no linked task")
linked_verification = {tid for x in k.values() for tid in x["verification_ids"]}
for tid in t:
    if tid not in linked_verification:
        errors.append(f"{tid}: no linked task")
# Detect cyclic task dependencies.
visiting, done = set(), set()
def visit(wid):
    if wid in visiting:
        errors.append(f"Dependency cycle at {wid}")
        return
    if wid in done: return
    visiting.add(wid)
    for dep in w[wid]["dependencies"]:
        if dep in w: visit(dep)
    visiting.remove(wid)
    done.add(wid)
for wid in w: visit(wid)
for tid, x in t.items():
    if x["status"] not in {"Not run", "Passed", "Failed", "Blocked"}:
        errors.append(f"{tid}: unknown verification status")
    if x["status"] == "Passed" and not x["evidence"]:
        errors.append(f"{tid}: passed without evidence")
v = r["release_validation"]
if v["verification_id"] not in t:
    errors.append("Unknown release validation case")
if set(v["cus_ids"]) != {cid for cid,x in c.items() if x["priority"] == "P0"}:
    errors.append("Release validation must cover exactly all P0 requirements")
if v["status"] == "Passed" and (not v["candidate_commit"] or not v["evidence"]):
    errors.append("Release validation passed without candidate and evidence")
if errors:
    raise SystemExit("\\n".join(errors))
print(f"Traceability valid: {len(c)} customer-user-stories, {len(s)} system requirements, {len(k)} tasks, {len(t)} planned cases")
print("This check validates registry integrity only, not product behavior or user acceptance.")
