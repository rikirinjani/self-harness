#!/usr/bin/env python3
"""Descriptive overhead reporting for overhead.v1 records; Python 3.10+."""

import argparse
from collections import defaultdict
from datetime import datetime
import json
import math
import os
from pathlib import Path
import sys

CATEGORIES = {
    "dispatch", "briefing", "implementation", "synthesis", "retry",
    "verification", "evidence", "reporting", "context_management",
    "human_intervention", "other",
}
NUMERIC = (
    "cost_usd", "human_seconds", "duration_seconds",
    "input_tokens", "output_tokens", "context_tokens",
)
TOKEN_FIELDS = {"input_tokens", "output_tokens", "context_tokens"}
TYPES = {"task", "activity", "acceptance", "failure", "skill", "compression"}


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError("timestamp must be a string")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("timestamp must include timezone")
    return result


def text(record, *fields):
    for field in fields:
        if not isinstance(record.get(field), str) or not record[field].strip():
            raise ValueError(f"{field} must be a nonempty string")


def boolean(record, *fields):
    for field in fields:
        if type(record.get(field)) is not bool:
            raise ValueError(f"{field} must be boolean")


def number(value, name, integer=False):
    allowed = (int,) if integer else (int, float)
    if type(value) not in allowed:
        raise ValueError(f"{name} must be a nonnegative finite number")
    try:
        valid = value >= 0 and math.isfinite(value)
    except (OverflowError, ValueError):
        valid = False
    if not valid:
        raise ValueError(f"{name} must be a nonnegative finite number")


def validate(record):
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    if record.get("schema") != "overhead.v1":
        raise ValueError("unsupported or missing schema")
    text(record, "record_id", "task_id", "type")
    kind = record["type"]
    if kind not in TYPES:
        raise ValueError(f"unknown record type: {kind}")
    if kind == "task":
        text(record, "pair_id", "task_class", "revision", "suite_id",
             "implementer_id")
        if record.get("mode") not in ("direct", "delegated"):
            raise ValueError("invalid mode")
        if record.get("status") not in ("completed", "failed", "abandoned", "running"):
            raise ValueError("invalid status")
        boolean(record, "accounting_complete")
        start = timestamp(record.get("started_at"))
        if "ended_at" not in record:
            raise ValueError("ended_at is required")
        if record["status"] == "running":
            if record["ended_at"] is not None:
                raise ValueError("running task must have null ended_at")
        elif timestamp(record["ended_at"]) < start:
            raise ValueError("ended_at precedes started_at")
    elif kind == "activity":
        if record.get("category") not in CATEGORIES:
            raise ValueError("invalid activity category")
        for field in NUMERIC:
            if field not in record:
                raise ValueError(f"missing {field}; use null for unknown")
            if record[field] is not None:
                number(record[field], field, field in TOKEN_FIELDS)
        if (record["context_tokens"] is not None
                and record["input_tokens"] is not None
                and record["context_tokens"] > record["input_tokens"]):
            raise ValueError("context_tokens exceeds input_tokens")
    elif kind == "acceptance":
        if record.get("decision") not in ("APPROVE", "REJECT"):
            raise ValueError("invalid acceptance decision")
        text(record, "revision", "suite_id", "reviewer_id", "rationale",
             "evidence_uri")
        boolean(record, "independent", "tests_passed", "correct",
                "observation_complete")
    elif kind == "failure":
        text(record, "reason")
        timestamp(record.get("at"))
    elif kind == "skill":
        text(record, "skill_id")
        boolean(record, "success")
    elif kind == "compression":
        text(record, "tokenizer_id", "tokenizer_version",
             "tokenizer_config_hash", "corpus_id", "evidence_uri")
        number(record.get("original_tokens"), "original_tokens", True)
        number(record.get("compressed_tokens"), "compressed_tokens", True)
        if record["original_tokens"] == 0:
            raise ValueError("original_tokens must be positive")
        boolean(record, "decode_included", "round_trip_ok", "semantic_ok")


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def bad_constant(value):
    raise ValueError(f"invalid JSON constant: {value}")


def parse_json(source):
    return json.loads(source, object_pairs_hook=unique_keys,
                      parse_constant=bad_constant)


def load_records(directories, warnings):
    records = {}
    conflicts = set()
    seen_paths = set()
    duplicates = 0

    def ingest(value, origin):
        nonlocal duplicates
        try:
            validate(value)
        except (ValueError, TypeError, OverflowError, RecursionError) as exc:
            warnings.append(f"{origin}: {exc}")
            # A malformed version of an existing ID must not leave that ID trusted.
            if isinstance(value, dict):
                rid = value.get("record_id")
                if isinstance(rid, str):
                    conflicts.add(rid)
                    records.pop(rid, None)
            return
        rid = value["record_id"]
        if rid in conflicts:
            return
        if rid in records:
            if records[rid] == value:
                duplicates += 1
            else:
                warnings.append(f"{origin}: conflicting record_id {rid}")
                conflicts.add(rid)
                del records[rid]
        else:
            records[rid] = value

    for directory in directories:
        root = Path(directory)
        if root.is_symlink() or not root.is_dir():
            warnings.append(f"missing, unreadable, or symlink directory: {root}")
            continue

        def walk_error(exc):
            warnings.append(f"directory scan: {exc}")

        for parent, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
            for name in list(dirs):
                candidate = Path(parent) / name
                if candidate.is_symlink():
                    warnings.append(f"skipped symlink directory: {candidate}")
                    dirs.remove(name)
            dirs.sort()
            for name in sorted(files):
                path = Path(parent) / name
                if path.suffix.lower() not in (".json", ".jsonl", ".pm1"):
                    continue
                try:
                    if path.is_symlink():
                        warnings.append(f"skipped symlink file: {path}")
                        continue
                    resolved = path.resolve()
                    if resolved in seen_paths:
                        continue
                    seen_paths.add(resolved)
                    source = path.read_text(encoding="utf-8-sig")
                    if not source.strip():
                        raise ValueError("empty record file")
                    if path.suffix.lower() == ".jsonl":
                        for line_no, line in enumerate(source.splitlines(), 1):
                            if not line.strip():
                                continue
                            origin = f"{path}:{line_no}"
                            try:
                                ingest(parse_json(line), origin)
                            except (ValueError, RecursionError) as exc:
                                warnings.append(f"{origin}: {exc}")
                    else:
                        value = parse_json(source)
                        if isinstance(value, list):
                            for index, record in enumerate(value):
                                ingest(record, f"{path}[{index}]")
                        else:
                            ingest(value, str(path))
                except (OSError, UnicodeError, ValueError, RecursionError) as exc:
                    warnings.append(f"{path}: {exc}")
    return list(records.values()), duplicates


def total(values):
    values = list(values)
    if any(value is None for value in values):
        return None
    try:
        result = math.fsum(values)
        return result if math.isfinite(result) else None
    except (OverflowError, ValueError):
        return None


def percentile(values, fraction):
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def ratio(numerator, denominator):
    if numerator is None or not denominator:
        return None
    return numerator / denominator


def fmt(value, digits=2):
    return "unknown" if value is None else f"{value:.{digits}f}"


def cell(value):
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace(
        "\r", " "
    ).replace("\n", " ").replace("<", "&lt;").replace(">", "&gt;")


def table(headers, rows):
    print("| " + " | ".join(cell(h) for h in headers) + " |")
    print("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        print("| " + " | ".join(cell(value) for value in row) + " |")
    print()


def summarize_tasks(records, hourly_rate, warnings):
    grouped = defaultdict(list)
    for record in records:
        grouped[record["task_id"]].append(record)
    results = []
    for task_id, items in sorted(grouped.items()):
        envelopes = [r for r in items if r["type"] == "task"]
        if len(envelopes) != 1:
            warnings.append(
                f"{task_id}: expected one task envelope, found {len(envelopes)}; "
                "orphan/conflicting task excluded"
            )
            continue
        task = envelopes[0]
        activities = [r for r in items if r["type"] == "activity"]
        acceptances = [r for r in items if r["type"] == "acceptance"]
        issues = []
        if not activities:
            issues.append("no activity ledger")
        if not task["accounting_complete"]:
            issues.append("accounting not attested complete")
        if any(r[field] is None for r in activities for field in NUMERIC):
            issues.append("unknown activity measurements")

        sums = {field: total(r[field] for r in activities) for field in NUMERIC}
        if any(value is None for value in sums.values()):
            issues.append("unknown or overflowing totals")
        human = sums["human_seconds"]
        labor = (0.0 if human == 0 else
                 None if human is None or hourly_rate is None else
                 total([human / 3600 * hourly_rate]))
        ledger_complete = (
            bool(activities) and task["accounting_complete"]
            and not any(r[field] is None for r in activities for field in NUMERIC)
            and all(value is not None for value in sums.values())
        )
        cost = total([sums["cost_usd"], labor]) if ledger_complete else None
        if cost is None:
            issues.append("labor-inclusive total cost unknown")
        terminal = task["status"] != "running"
        elapsed = (
            (timestamp(task["ended_at"]) - timestamp(task["started_at"])).total_seconds()
            if terminal else None
        )
        if not terminal:
            issues.append("running/censored")

        accepted = False
        quality_resolved = task["status"] in ("failed", "abandoned")
        if len(acceptances) > 1:
            issues.append("conflicting acceptance records")
            quality_resolved = False
        elif len(acceptances) == 1:
            acceptance = acceptances[0]
            bound = (
                acceptance["revision"] == task["revision"]
                and acceptance["suite_id"] == task["suite_id"]
                and acceptance["reviewer_id"] != task["implementer_id"]
                and acceptance["independent"]
            )
            if not bound:
                issues.append("acceptance binding/independence invalid")
                quality_resolved = False
            elif not acceptance["observation_complete"]:
                issues.append("quality observation window incomplete")
                quality_resolved = False
            else:
                quality_resolved = terminal
                accepted = (
                    task["status"] == "completed"
                    and acceptance["decision"] == "APPROVE"
                    and acceptance["tests_passed"] and acceptance["correct"]
                )
                if task["status"] != "completed" and acceptance["decision"] == "APPROVE":
                    issues.append("approval contradicts task status")
                    quality_resolved = False
        elif task["status"] == "completed":
            issues.append("missing independent acceptance")
            quality_resolved = False

        results.append({
            "task": task, "items": items, "activities": activities, "sums": sums,
            "cost": cost, "elapsed": elapsed, "accepted": accepted,
            "resolved": quality_resolved, "issues": issues,
            "failures": sum(r["type"] == "failure" for r in items),
            "retries": sum(r["category"] == "retry" for r in activities),
        })
    return results


def load_inventory(path, warnings):
    if path is None:
        return None
    try:
        value = parse_json(Path(path).read_text(encoding="utf-8-sig"))
        if (not isinstance(value, list)
                or any(not isinstance(s, str) or not s.strip() for s in value)
                or len(set(value)) != len(value)):
            raise ValueError("inventory must be an array of unique nonempty strings")
        return set(value)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        warnings.append(f"skill inventory: {exc}")
        return None


def report(tasks, records, inventory, warnings, duplicates, hourly_rate):
    provisional = bool(warnings) or not tasks or any(t["issues"] for t in tasks)
    print("# Orchestration overhead report\n")
    print(f"Status: **{'PROVISIONAL' if provisional else 'DESCRIPTIVE / COMPLETE'}**\n")
    print(f"Valid records: {len(records)}; identical duplicates ignored: {duplicates}.")
    print(f"Human loaded hourly rate (USD): {fmt(hourly_rate)}.\n")
    print("Unknown is not zero. Acceptance is a recorded attestation, not "
          "authenticated by this reader. No causal multiplier is established.\n")

    print("## Per-task measurements\n")
    table(
        ["Task", "Arm", "Pair", "Class", "Status", "Accepted/correct",
         "Cost USD", "Elapsed min", "Human min", "Input/output/context tokens",
         "Failures/retry items", "Issues"],
        [
            [
                t["task"]["task_id"], t["task"]["mode"], t["task"]["pair_id"],
                t["task"]["task_class"], t["task"]["status"],
                "yes" if t["accepted"] else "no" if t["resolved"] else "unresolved",
                fmt(t["cost"]), fmt(ratio(t["elapsed"], 60)),
                fmt(ratio(t["sums"]["human_seconds"], 60)),
                "/".join(fmt(t["sums"][f], 0) for f in
                         ("input_tokens", "output_tokens", "context_tokens")),
                f'{t["failures"]}/{t["retries"]}',
                "; ".join(t["issues"]) or "none",
            ] for t in tasks
        ],
    )

    print("## Arm summaries — all assigned tasks remain in the cost pool\n")
    rows = []
    for mode in ("direct", "delegated"):
        subset = [t for t in tasks if t["task"]["mode"] == mode]
        if not subset:
            continue
        accepted = [t for t in subset if t["accepted"]]
        failed = sum(t["task"]["status"] in ("failed", "abandoned") for t in subset)
        running = sum(t["task"]["status"] == "running" for t in subset)
        # Any invalid record can hide cost or an assignment: suppress primary ratios.
        ready = not warnings and all(
            t["cost"] is not None and t["elapsed"] is not None
            and t["resolved"] and not t["issues"] for t in subset
        )
        costs = total(t["cost"] for t in subset) if ready else None
        elapsed = total(t["elapsed"] for t in subset) if ready else None
        human = total(t["sums"]["human_seconds"] for t in subset) if ready else None
        latency = [t["elapsed"] / 60 for t in accepted]
        rows.append([
            mode, len(subset), len(accepted), running,
            fmt(100 * failed / len(subset)) + "%",
            fmt(100 * len(accepted) / len(subset)) + "%",
            fmt(costs), fmt(ratio(costs, len(accepted))),
            fmt(ratio(elapsed, 60 * len(accepted))),
            "/".join(fmt(percentile(latency, p)) for p in (.5, .9, .95)),
            fmt(ratio(human, 60 * len(subset))),
            fmt(ratio(human, 60 * len(accepted))),
        ])
    table(
        ["Arm", "Assigned", "Accepted", "Running", "Failed/abandoned",
         "Acceptance yield", "Total USD", "USD/accepted", "Elapsed min/accepted",
         "Accepted latency p50/p90/p95 min", "Human min/task", "Human min/accepted"],
        rows,
    )
    print("Primary ratios require a complete, closed, quality-resolved arm and "
          "no ingestion diagnostics. Latency quantiles describe only observed "
          "accepted tasks; they exclude unresolved observations.\n")

    print("## Recorded activity categories\n")
    stages = defaultdict(list)
    for record in records:
        if record["type"] == "activity":
            stages[record["category"]].append(record)
    table(
        ["Category", "Items", "Nonhuman USD", "Human min", "Activity duration min"],
        [
            [category, len(items),
             fmt(total(r["cost_usd"] for r in items)),
             fmt(ratio(total(r["human_seconds"] for r in items), 60)),
             fmt(ratio(total(r["duration_seconds"] for r in items), 60))]
            for category, items in sorted(stages.items())
        ],
    )
    print("Category totals include valid orphan activities and may overlap in "
          "wall time. They are not end-to-end latency or certified ledger totals.\n")

    print("## Skill utilization\n")
    skills = defaultdict(list)
    for record in records:
        if record["type"] == "skill":
            skills[record["skill_id"]].append(record)
    accepted_ids = {t["task"]["task_id"] for t in tasks if t["accepted"]}
    names = set(skills) | (inventory or set())
    table(
        ["Skill", "Invocations", "Distinct tasks", "Failed invocations",
         "Accepted-task associations", "Inventory"],
        [
            [
                name, len(skills[name]), len({r["task_id"] for r in skills[name]}),
                sum(not r["success"] for r in skills[name]),
                len({r["task_id"] for r in skills[name]} & accepted_ids),
                "unavailable" if inventory is None else
                "listed" if name in inventory else "unlisted",
            ] for name in sorted(names)
        ],
    )
    print("Associations are not causal benefits. Zero-use skills are visible "
          "only when an inventory is supplied.\n")

    print("## Compression observations\n")
    groups = defaultdict(list)
    for record in records:
        if record["type"] == "compression":
            key = tuple(record[k] for k in (
                "corpus_id", "tokenizer_id", "tokenizer_version",
                "tokenizer_config_hash",
            ))
            groups[key].append(record)
    compression_rows = []
    for key, items in sorted(groups.items()):
        valid = [
            r for r in items if r["decode_included"]
            and r["round_trip_ok"] and r["semantic_ok"]
        ]
        original = total(r["original_tokens"] for r in valid)
        compressed = total(r["compressed_tokens"] for r in valid)
        fraction = ratio(compressed, original)
        savings = None if fraction is None else 100 * (1 - fraction)
        compression_rows.append([
            *key, len(items), len(valid), len(items) - len(valid),
            fmt(original, 0), fmt(compressed, 0),
            "unknown" if savings is None else fmt(savings) + "%",
        ])
    table(
        ["Corpus", "Tokenizer", "Version", "Config hash", "Observed", "Verified",
         "Unverified/failed", "Original tokens", "Effective compressed tokens",
         "Verified-subset savings"],
        compression_rows,
    )
    print("Compression inputs are externally measured attestations. Failed or "
          "unverified observations are exposed, not counted as zero. A subset "
          "saving cannot substantiate a whole-corpus claim when failures exist.\n")

    print("## Diagnostics\n")
    if not tasks:
        print("- No usable tasks; no delivery metric is established.")
    for warning in warnings:
        print("- " + cell(warning))
    if not warnings and tasks:
        print("- No ingestion diagnostics. Per-task issues, if any, remain above.")
    print("\n## Claim status\n")
    print("- **2x:** not tested here; requires preregistered paired/stratified "
          "analysis, confidence intervals, and quality constraints.")
    print("- **5x:** not tested here; requires independently adjudicated decision "
          "opportunities and an explicitly defined ratio.")
    print("- **67–84%:** descriptive tokenizer observations only; requires "
          "representative corpus validation and confidence intervals.")
    return provisional


def nonnegative_rate(value):
    try:
        result = float(value)
        number(result, "human-hourly-usd")
        return result
    except (ValueError, OverflowError) as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--traces-dir", action="append", required=True, type=Path)
    parser.add_argument("--failures-dir", action="append", required=True, type=Path)
    parser.add_argument("--qms-dir", action="append", required=True, type=Path)
    parser.add_argument("--human-hourly-usd", type=nonnegative_rate)
    parser.add_argument("--skills-file", type=Path)
    parser.add_argument("--strict", action="store_true",
                        help="exit 2 for provisional/incomplete measurement")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    warnings = []
    records, duplicates = load_records(
        args.traces_dir + args.failures_dir + args.qms_dir, warnings
    )
    inventory = load_inventory(args.skills_file, warnings)
    tasks = summarize_tasks(records, args.human_hourly_usd, warnings)
    provisional = report(
        tasks, records, inventory, warnings, duplicates, args.human_hourly_usd
    )
    return 2 if args.strict and provisional else 0


if __name__ == "__main__":
    raise SystemExit(main())
