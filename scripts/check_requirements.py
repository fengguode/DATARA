"""Check requirement links and planned coverage; this does not validate the product."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
r = json.loads((ROOT / "docs/management/requirements-registry.json").read_text())
errors = []
def index(name):
    rows = r[name]
    ids = [x["id"] for x in rows]
    if len(ids) != len(set(ids)):
        errors.append(f"Duplicate IDs in {name}")
    return {x["id"]: x for x in rows}
p = index("product_requirements")
s = index("system_requirements")
t = index("verification_cases")
w = index("work_packages")
for sid, x in s.items():
    if x["product_id"] not in p:
        errors.append(f"{sid}: unknown product parent")
    elif x["priority"] != p[x["product_id"]]["priority"]:
        errors.append(f"{sid}: priority differs from parent")
    if x["work_package"] not in w:
        errors.append(f"{sid}: unknown work package")
    if not x["verification_ids"]:
        errors.append(f"{sid}: no planned verification")
    for tid in x["verification_ids"]:
        if tid not in t:
            errors.append(f"{sid}: unknown verification {tid}")
for pid in p:
    if not any(x["product_id"] == pid for x in s.values()):
        errors.append(f"{pid}: no derived system requirements")
for wid, x in w.items():
    for dep in x["dependencies"]:
        if dep not in w:
            errors.append(f"{wid}: unknown dependency {dep}")
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
if set(v["product_ids"]) != {pid for pid,x in p.items() if x["priority"] == "P0"}:
    errors.append("Release validation must cover exactly all P0 requirements")
if v["status"] == "Passed" and (not v["candidate_commit"] or not v["evidence"]):
    errors.append("Release validation passed without candidate and evidence")
if errors:
    raise SystemExit("\\n".join(errors))
print(f"Traceability valid: {len(p)} product requirements, {len(s)} system requirements, {len(t)} planned cases")
print("This check validates registry integrity only, not product behavior or user acceptance.")
