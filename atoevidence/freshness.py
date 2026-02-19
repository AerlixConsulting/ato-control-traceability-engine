from __future__ import annotations
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

from .mapping import Control

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")

@dataclass
class FreshnessResult:
    control_id: str
    last_date: Optional[date]
    age_days: Optional[int]
    frequency_days: int
    score_0_100: int
    status: str

def _extract_latest_date_from_file(path: Path) -> Optional[date]:
    if not path.exists() or not path.is_file():
        return None
    text = path.read_text(encoding="utf-8", errors="ignore")
    matches = DATE_RE.findall(text)
    if not matches:
        return None
    # choose the max ISO date
    try:
        latest = max(datetime.strptime(m, "%Y-%m-%d").date() for m in matches)
        return latest
    except Exception:
        return None

def _score(age: Optional[int], freq: int) -> Tuple[int, str]:
    if age is None:
        return 0, "Unknown"
    # 100 if age <= freq, then linearly drop to 0 at 2*freq
    if age <= freq:
        return 100, "Fresh"
    if age >= 2 * freq:
        return 0, "Stale"
    # linear between
    remaining = (2 * freq) - age
    score = int(round((remaining / freq) * 100))
    return max(1, min(99, score)), "Aging"

def compute_freshness(repo_root: Path, controls: Dict[str, Control]) -> Dict[str, FreshnessResult]:
    today = date.today()
    results: Dict[str, FreshnessResult] = {}

    for cid, c in controls.items():
        # Heuristic: freshness is determined from the newest date in monitoring artifacts
        # (review records, status reports, drift logs). This is portfolio-safe and deterministic.
        latest: Optional[date] = None
        for rel in c.monitoring:
            d = _extract_latest_date_from_file(repo_root / rel)
            if d and (latest is None or d > latest):
                latest = d

        age = (today - latest).days if latest else None
        score, status = _score(age, c.review_frequency_days)
        results[cid] = FreshnessResult(
            control_id=cid,
            last_date=latest,
            age_days=age,
            frequency_days=c.review_frequency_days,
            score_0_100=score,
            status=status,
        )
    return results

def render_freshness_report(results: Dict[str, FreshnessResult]) -> str:
    lines = ["# Evidence Freshness Score (Generated)", ""]
    lines.append("| Control | Last Evidence Date | Age (days) | Frequency (days) | Score | Status |")
    lines.append("|---|---:|---:|---:|---:|---|")
    for cid in sorted(results.keys()):
        r = results[cid]
        last = r.last_date.isoformat() if r.last_date else "N/A"
        age = str(r.age_days) if r.age_days is not None else "N/A"
        lines.append(f"| {cid} | {last} | {age} | {r.frequency_days} | {r.score_0_100} | {r.status} |")
    lines.append("")
    lines.append("Scoring model (reference):")
    lines.append("- 100 if evidence is within required cadence")
    lines.append("- linearly decreases to 0 at 2× cadence")
    lines.append("- 0 if no dates found in monitoring artifacts")
    return "\n".join(lines) + "\n"
