#!/usr/bin/env python3
"""Build the ssq-update-v1 JSON file consumed by SSQ Assistant."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


def date_only(value: str) -> str:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()


def normalize(record: dict) -> dict:
    issue = str(record.get("issue", ""))
    if len(issue) != 7 or not issue.isdigit():
        raise ValueError(f"invalid issue: {issue!r}")
    reds = sorted(int(value) for value in record.get("reds", []))
    blue = int(record.get("blue", 0))
    if len(reds) != 6 or len(set(reds)) != 6 or any(value < 1 or value > 33 for value in reds):
        raise ValueError(f"invalid red balls for {issue}")
    if not 1 <= blue <= 16:
        raise ValueError(f"invalid blue ball for {issue}")
    normalized = {
        "issue": issue,
        "drawDate": date_only(str(record.get("drawDate", ""))),
        "reds": reds,
        "blue": blue,
    }
    for key in ("salesAmount", "jackpotAmount"):
        if record.get(key) is not None:
            normalized[key] = int(record[key])
    if record.get("claimDeadline"):
        normalized["claimDeadline"] = date_only(str(record["claimDeadline"]))
    if record.get("prizeTiers"):
        normalized["prizeTiers"] = [normalize_tier(tier) for tier in record["prizeTiers"]]
    return normalized


def normalize_tier(tier: dict) -> dict:
    if not isinstance(tier, dict):
        raise ValueError("invalid prize tier")
    name = next((tier.get(key) for key in ("name", "level", "prizeName", "type", "prizeType") if tier.get(key) is not None), "")
    if not str(name).strip():
        raise ValueError("prize tier has no name")
    normalized = {"name": str(name)}
    for output, keys in (
        ("winningCount", ("winningCount", "count", "number", "num")),
        ("unitPrize", ("unitPrize", "singleBonus", "money", "bonus", "singleMoney")),
    ):
        value = next((tier.get(key) for key in keys if tier.get(key) is not None), None)
        if value is not None:
            value = int(value)
            if value < 0:
                raise ValueError("negative prize tier value")
            normalized[output] = value
    condition = tier.get("condition", tier.get("require"))
    if condition is not None:
        normalized["condition"] = str(condition)
    return normalized


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--version", default=dt.date.today().isoformat())
    parser.add_argument("--primary-source", required=True)
    parser.add_argument("--verification-source", required=True)
    args = parser.parse_args()

    raw = json.loads(args.input.read_text(encoding="utf-8"))
    records_input = raw["records"] if isinstance(raw, dict) else raw
    if not isinstance(records_input, list) or not records_input:
        raise ValueError("input must contain a non-empty records list")
    records = sorted((normalize(record) for record in records_input), key=lambda item: item["issue"])
    if len({record["issue"] for record in records}) != len(records):
        raise ValueError("duplicate issue")
    canonical = json.dumps(records, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    package = {
        "format": "ssq-update-v1",
        "version": args.version,
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "primarySource": args.primary_source,
        "verificationSource": args.verification_source,
        "expectedDraws": len(records),
        "latestIssue": records[-1]["issue"],
        "recordsSha256": hashlib.sha256(canonical).hexdigest(),
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(package, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
