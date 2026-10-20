#!/usr/bin/env python3
"""Validate the dataset: JSON parses, matches the JSON Schema, CSV matches JSON
row for row, percent bands are sane, and docs/ copies are in sync.
Requires: pip install jsonschema"""
import csv, json, pathlib, sys
from jsonschema import Draft202012Validator, FormatChecker

ROOT = pathlib.Path(__file__).resolve().parent.parent
errors = []

rows = json.loads((ROOT / "data/grading-scales.json").read_text(encoding="utf-8"))
schema = json.loads((ROOT / "schema/grading-scales.schema.json").read_text(encoding="utf-8"))
Draft202012Validator.check_schema(schema)
for e in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(rows):
    errors.append(f"schema: {list(e.path)}: {e.message}")

fields = list(schema["items"]["properties"].keys())
with open(ROOT / "data/grading-scales.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    if reader.fieldnames != fields:
        errors.append(f"csv header {reader.fieldnames} != {fields}")
    csv_rows = list(reader)
if len(csv_rows) != len(rows):
    errors.append(f"row count: csv {len(csv_rows)} vs json {len(rows)}")


def norm(v):
    return None if v == "" else v


for i, (j, c) in enumerate(zip(rows, csv_rows)):
    for k in fields:
        jv, cv = j[k], norm(c[k])
        if isinstance(jv, (int, float)) and not isinstance(jv, bool):
            ok = cv is not None and float(cv) == float(jv)
        else:
            ok = jv == cv
        if not ok:
            errors.append(f"row {i} field {k}: json={jv!r} csv={cv!r}")

seen = set()
for i, r in enumerate(rows):
    key = (r["country"], r["system"], r["grade"])
    if key in seen:
        errors.append(f"row {i}: duplicate {key}")
    seen.add(key)
    lo, hi = r["min_percent"], r["max_percent"]
    if (lo is None) != (hi is None):
        errors.append(f"row {i}: min/max_percent must both be null or both set")
    if lo is not None and lo > hi:
        errors.append(f"row {i}: min_percent > max_percent")

# percent bands within a system must not overlap
by_sys = {}
for r in rows:
    if r["min_percent"] is not None:
        by_sys.setdefault((r["country"], r["system"]), []).append(r)
for key, bands in by_sys.items():
    bands = sorted(bands, key=lambda b: b["min_percent"])
    for a, b in zip(bands, bands[1:]):
        if b["min_percent"] <= a["max_percent"]:
            errors.append(f"{key}: overlap {a['grade']} / {b['grade']}")

for name in ["data/grading-scales.json", "data/grading-scales.csv"]:
    if (ROOT / name).read_bytes() != (ROOT / "docs" / name).read_bytes():
        errors.append(f"docs/{name} is out of sync; run scripts/build.py")

if errors:
    print("\n".join(errors))
    sys.exit(1)
systems = {(r["country"], r["system"]) for r in rows}
countries = {r["country"] for r in rows}
print(f"OK: {len(rows)} rows, {len(systems)} systems, {len(countries)} countries; schema valid; CSV matches JSON")
