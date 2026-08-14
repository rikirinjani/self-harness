#!/usr/bin/env python3
"""
detect_overrides.py — Automated detection of the OVERRIDES failure pattern.

OVERRIDES (DEC-2026-0001, 6th failure category):
    Oracle read-only constraint causing payload loss. The oracle lane is
    read-only (read_files only) and cannot persist JSON to disk; a required
    payload is lost when the lane closes or is omitted from the final task
    result, forcing regeneration / re-dispatch.

Reference records (ground truth):
    - 20260731-process-ora1-payload-loss.json
    - 20260731-process-ora9-payload-loss.json

Usage:
    python detect_overrides.py [--failures-dir DIR] [--threshold 0.5] [--json]

Output:
    - List of detected records with confidence score (0-1)
    - Summary: total scanned, total detected, confidence distribution
"""

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Signal definitions
# ---------------------------------------------------------------------------

# Fields whose text is scanned for signals.
TEXT_FIELDS = (
    "summary",
    "root_cause",
    "lesson",
    "recovery",
    "remediation",
    "corrective_action",
    "what_was_done_wrong",
)

# (name, weight, regex-or-callable) — each signal contributes to the score.
# Weights chosen so that the two ground-truth records score >= 1.0 while
# near-miss records (read-only mention without payload loss, oracle mention
# without payload) stay well below the default 0.5 threshold.
SIGNALS = [
    # Agent field is exactly "oracle" — strongest single indicator.
    ("agent_oracle", 0.35, lambda rec: str(rec.get("agent", "")).strip().lower() == "oracle"),
    # "oracle" mentioned anywhere in the record text (weaker than agent field).
    ("text_oracle", 0.15, lambda text: re.search(r"\boracle\b", text, re.I) is not None),
    # Payload + loss/omission language — the core of the pattern.
    (
        "payload_loss",
        0.35,
        lambda text: (
            re.search(r"\bpayload\b", text, re.I) is not None
            and re.search(
                r"\b(lost|omitted|not included|missing|no payload|did not include|"
                r"without the payload|payload not included|failed to include)\b",
                text,
                re.I,
            )
            is not None
        ),
    ),
    # Read-only lane constraint.
    (
        "read_only",
        0.20,
        lambda text: re.search(r"\bread[- ]?only\b|\bread_files\b", text, re.I) is not None,
    ),
    # Lane + ephemeral/closed/buffer/omitted — the delivery-channel failure.
    (
        "lane_ephemeral",
        0.20,
        lambda text: (
            re.search(r"\blane\b", text, re.I) is not None
            and re.search(
                r"\b(closed|close|closing|ephemeral|buffer|omitted)\b", text, re.I
            )
            is not None
        ),
    ),
    # Persistence language (persist / Persistence Rule / write to disk).
    (
        "persist",
        0.10,
        lambda text: re.search(r"\bpersist", text, re.I) is not None,
    ),
    # Recovery pattern: regeneration or re-dispatch.
    (
        "regeneration",
        0.10,
        lambda text: re.search(r"\bregenerat|\bre-?dispatch", text, re.I) is not None,
    ),
]

MAX_SCORE = sum(w for _, w, _ in SIGNALS)


def record_text(record: dict) -> str:
    """Concatenate all free-text fields of a failure record."""
    parts = []
    for field in TEXT_FIELDS:
        value = record.get(field)
        if isinstance(value, str):
            parts.append(value)
    return "\n".join(parts)


def score_record(record: dict) -> tuple[float, list[str]]:
    """Return (raw_score, list of matched signal names) for a record."""
    text = record_text(record)
    matched = []
    score = 0.0
    for name, weight, matcher in SIGNALS:
        if matcher(record) if name == "agent_oracle" else matcher(text):
            score += weight
            matched.append(name)
    return score, matched


def confidence(raw_score: float) -> float:
    """Normalize raw score to a 0-1 confidence, capped at 1.0."""
    return min(1.0, raw_score / MAX_SCORE)


def is_failure_record(record: dict) -> bool:
    """A failure record must carry an outcome of fail/partial.

    Some records in the failures directory predate the outcome field (they
    only carry category + severity / root_cause). Treat those as failure
    records too. Files that are neither (e.g. the taxonomy-classification
    output, which has no category/severity) are skipped.
    """
    outcome = str(record.get("outcome", "")).strip().lower()
    if outcome in ("fail", "partial"):
        return True
    has_category = "category" in record
    has_failure_shape = "severity" in record or "root_cause" in record
    return has_category and has_failure_shape


def scan_failures(failures_dir: Path, threshold: float):
    """Scan all *.json files in failures_dir and detect OVERRIDES records."""
    scanned = 0
    skipped = 0
    parse_errors = []
    detected = []

    for path in sorted(failures_dir.glob("*.json")):
        try:
            with open(path, "r", encoding="utf-8-sig") as fh:
                record = json.load(fh)
        except UnicodeDecodeError:
            # Some records contain non-UTF-8 bytes (e.g. a stray 0x97); fall
            # back to a lossy decode so the record is still scanned.
            try:
                with open(path, "r", encoding="utf-8-sig", errors="replace") as fh:
                    record = json.load(fh)
            except (json.JSONDecodeError, OSError) as exc:
                parse_errors.append((path.name, str(exc)))
                continue
        except (json.JSONDecodeError, OSError) as exc:
            parse_errors.append((path.name, str(exc)))
            continue

        if not isinstance(record, dict) or not is_failure_record(record):
            skipped += 1
            continue

        scanned += 1
        raw, matched = score_record(record)
        conf = confidence(raw)
        if conf >= threshold:
            detected.append(
                {
                    "file": path.name,
                    "agent": record.get("agent", ""),
                    "category": record.get("category", ""),
                    "severity": record.get("severity", ""),
                    "trace_id": record.get("trace_id", ""),
                    "confidence": round(conf, 3),
                    "raw_score": round(raw, 3),
                    "signals": matched,
                    "summary": (record.get("summary", "") or "")[:160],
                }
            )

    return scanned, skipped, parse_errors, detected


def print_report(scanned, skipped, parse_errors, detected, threshold):
    print("=" * 72)
    print("OVERRIDES PATTERN DETECTION")
    print("=" * 72)
    print(f"Threshold: {threshold}  |  Max score: {MAX_SCORE:.2f}")
    print()

    if detected:
        print(f"Detected OVERRIDES-pattern records ({len(detected)}):")
        print("-" * 72)
        for d in detected:
            print(f"  [{d['confidence']:.2f}] {d['file']}")
            print(f"        agent={d['agent']!r}  category={d['category']!r}  "
                  f"severity={d['severity']!r}")
            print(f"        signals={', '.join(d['signals'])}")
            if d["summary"]:
                print(f"        summary: {d['summary']}")
            print()
    else:
        print("No OVERRIDES-pattern records detected.")
        print()

    print("-" * 72)
    print("SUMMARY")
    print(f"  Total JSON files scanned : {scanned}")
    print(f"  Skipped (non-failure)    : {skipped}")
    print(f"  Parse errors             : {len(parse_errors)}")
    print(f"  Detected (OVERRIDES)     : {len(detected)}")

    if detected:
        confs = sorted(d["confidence"] for d in detected)
        print("\n  Confidence distribution:")
        print(f"    min    : {confs[0]:.3f}")
        print(f"    median : {confs[len(confs) // 2]:.3f}")
        print(f"    max    : {confs[-1]:.3f}")
        buckets = {
            "0.90-1.00": sum(1 for c in confs if c >= 0.90),
            "0.70-0.89": sum(1 for c in confs if 0.70 <= c < 0.90),
            "0.50-0.69": sum(1 for c in confs if 0.50 <= c < 0.70),
            "< 0.50    ": sum(1 for c in confs if c < 0.50),
        }
        for label, count in buckets.items():
            if count:
                print(f"    {label}: {count}")

    if parse_errors:
        print("\n  Parse errors:")
        for name, err in parse_errors:
            print(f"    {name}: {err}")

    print("=" * 72)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Detect OVERRIDES-pattern failures.")
    parser.add_argument(
        "--failures-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "failures",
        help="Directory containing failure JSON records (default: ../failures).",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Confidence threshold for detection (default: 0.5).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of the human report.",
    )
    args = parser.parse_args(argv)

    if not args.failures_dir.is_dir():
        print(f"ERROR: failures directory not found: {args.failures_dir}", file=sys.stderr)
        return 2

    scanned, skipped, parse_errors, detected = scan_failures(
        args.failures_dir, args.threshold
    )

    if args.json:
        print(
            json.dumps(
                {
                    "scanned": scanned,
                    "skipped": skipped,
                    "parse_errors": parse_errors,
                    "detected": detected,
                    "threshold": args.threshold,
                },
                indent=2,
            )
        )
    else:
        print_report(scanned, skipped, parse_errors, detected, args.threshold)

    return 0


if __name__ == "__main__":
    sys.exit(main())