from __future__ import annotations
from datetime import date, timedelta
from typing import Dict, List
from .mapping import Control

def render_evidence_index(controls: Dict[str, Control]) -> str:
    lines: List[str] = ["# Evidence Index (Generated)", ""]
    for cid in sorted(controls.keys()):
        c = controls[cid]
        lines.append(f"## {cid} {c.name}")
        for e in c.evidence:
            lines.append(f"- {e}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"

def render_status_report(controls: Dict[str, Control]) -> str:
    today = date.today()
    lines: List[str] = ["# Control Status Report (Generated)", "", f"Generated: {today.isoformat()}", ""]
    for cid in sorted(controls.keys()):
        c = controls[cid]
        next_review = today + timedelta(days=c.review_frequency_days)
        lines += [
            f"## {cid} {c.name}",
            f"- Owner: {c.owner}",
            f"- Status: Compliant (reference)",
            f"- Next Review Target: {next_review.isoformat()}",
            "",
        ]
    return "\n".join(lines).rstrip() + "\n"
