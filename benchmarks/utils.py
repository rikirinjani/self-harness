"""BENCH-C-01: Bounded Implementation - compute_aggregate_stats

Spec:
    Function: compute_aggregate_stats(results_dir)
    Input: pathlib.Path to directory with BENCH-*.json files
    Output: dict with:
        - total_benchmarks (int)
        - avg_score (float)
        - highest (dict with id, score, title)
        - lowest (dict with id, score, title)
        - pass_rate (float)
        - category_breakdown (list of {category, count, avg_score, avg_duration})
    Constraints:
        - stdlib only
        - handle malformed JSON gracefully (skip corrupt files)
        - follow project style (snake_case, type hints)
"""

import json
from pathlib import Path
from collections import defaultdict


def compute_aggregate_stats(results_dir: Path) -> dict:
    """Compute aggregate statistics from benchmark result files.

    Args:
        results_dir: Path to directory containing BENCH-*.json result files.

    Returns:
        dict with total_benchmarks, avg_score, highest (id+score+title),
        lowest (id+score+title), pass_rate, category_breakdown.

    Assumes result files follow the schema produced by benchmarks/score.py.
    Malformed files are silently skipped.
    """
    results_dir = Path(results_dir)
    result_files = sorted(results_dir.glob("BENCH-*.json"))

    scores = []
    passes = 0
    category_data = defaultdict(list)
    total = 0
    highest = None
    lowest = None

    for rf in result_files:
        try:
            with open(rf, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        bid = data.get("benchmark_id", "unknown")
        title = data.get("task", "")
        avg = data.get("scores", {}).get("average")
        outcome = data.get("execution", {}).get("outcome", "")
        duration = data.get("execution", {}).get("duration_s", 0)

        if avg is None:
            continue

        cat_letter = bid.split("-")[1].lower() if "-" in bid else "?"
        cat_map = {"r": "research", "c": "coding", "p": "planning", "o": "operational"}
        category = cat_map.get(cat_letter, "unknown")

        score_entry = {"id": bid, "score": avg, "title": title, "duration": duration}
        scores.append(score_entry)
        category_data[category].append(score_entry)
        total += 1

        if outcome == "pass":
            passes += 1

        entry = {"id": bid, "score": avg, "title": title}
        if highest is None or avg > highest["score"]:
            highest = dict(entry)
        if lowest is None or avg < lowest["score"]:
            lowest = dict(entry)

    if not scores:
        return {
            "total_benchmarks": 0,
            "avg_score": 0.0,
            "highest": {"id": "", "score": 0.0, "title": ""},
            "lowest": {"id": "", "score": 0.0, "title": ""},
            "pass_rate": 0.0,
            "category_breakdown": [
                {"category": c, "count": 0, "avg_score": 0.0, "avg_duration": 0.0}
                for c in ["research", "coding", "planning", "operational"]
            ],
        }

    avg_score = round(sum(s["score"] for s in scores) / len(scores), 2)
    pass_rate = round(passes / total * 100, 1) if total > 0 else 0.0

    category_breakdown = []
    for cat in ["research", "coding", "planning", "operational"]:
        entries = category_data.get(cat, [])
        if entries:
            cat_avg = round(sum(e["score"] for e in entries) / len(entries), 2)
            cat_dur = sum(e["duration"] for e in entries)
            category_breakdown.append({
                "category": cat,
                "count": len(entries),
                "avg_score": cat_avg,
                "avg_duration": round(cat_dur / len(entries), 1),
            })
        else:
            category_breakdown.append({
                "category": cat, "count": 0, "avg_score": 0.0, "avg_duration": 0.0,
            })

    return {
        "total_benchmarks": total,
        "avg_score": avg_score,
        "highest": highest,
        "lowest": lowest,
        "pass_rate": pass_rate,
        "category_breakdown": category_breakdown,
    }


# Self-test (runs only when executed directly)
if __name__ == "__main__":
    test_dir = Path(__file__).resolve().parent / "results"
    stats = compute_aggregate_stats(test_dir)
    print(f"Results from: {test_dir}")
    print(f"Total:        {stats['total_benchmarks']}")
    print(f"Avg score:    {stats['avg_score']}")
    print(f"Highest:      {stats['highest']['id']} ({stats['highest']['score']})")
    print(f"Lowest:       {stats['lowest']['id']} ({stats['lowest']['score']})")
    print(f"Pass rate:    {stats['pass_rate']}%")
    print(f"\nCategory breakdown:")
    for cat in stats["category_breakdown"]:
        print(f"  {cat['category']:12s} {cat['count']:2d} benchmarks, "
              f"avg score {cat['avg_score']:.2f}, avg dur {cat['avg_duration']:.0f}s")
    assert isinstance(stats["total_benchmarks"], int), "total must be int"
    assert isinstance(stats["avg_score"], float), "avg must be float"
    assert stats["highest"]["score"] >= stats["lowest"]["score"], "highest >= lowest"
    assert 0 <= stats["pass_rate"] <= 100, "pass_rate in range"
    assert len(stats["category_breakdown"]) == 4, "4 categories"
    print("\n[PASS] All assertions passed")
