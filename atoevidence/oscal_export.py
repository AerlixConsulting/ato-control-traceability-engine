from __future__ import annotations
from datetime import date
from pathlib import Path
from typing import Dict, Any
import json

from .mapping import Control

def export_oscal_stubs(repo_root: Path, controls: Dict[str, Control]) -> Dict[str, Path]:
    """
    Creates OSCAL-ish stub files suitable for auditor conversations:
    - catalog stub (controls list)
    - assessment results stub (simple findings/observations placeholder)
    This is intentionally a "stub" and not a full OSCAL implementation.
    """
    out_dir = repo_root / "generated" / "oscal"
    out_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()

    catalog: Dict[str, Any] = {
        "oscal_version": "1.1.2-stub",
        "generated": today,
        "type": "catalog-stub",
        "controls": [
            {
                "id": cid,
                "title": c.name,
                "owner": c.owner,
                "implementation_ref": c.implementation,
                "evidence_refs": c.evidence,
                "monitoring_refs": c.monitoring,
            }
            for cid, c in sorted(controls.items())
        ],
        "notes": "Synthetic OSCAL-style catalog stub for portfolio demonstration.",
    }

    assessment_results: Dict[str, Any] = {
        "oscal_version": "1.1.2-stub",
        "generated": today,
        "type": "assessment-results-stub",
        "observations": [
            {
                "control_id": cid,
                "statement": "Control appears implemented with evidence and monitoring artifacts available (reference).",
                "evidence": c.evidence,
                "monitoring": c.monitoring,
            }
            for cid, c in sorted(controls.items())
        ],
        "notes": "Synthetic OSCAL-style assessment results stub for portfolio demonstration.",
    }

    cat_path = out_dir / f"catalog-stub-{today}.json"
    ar_path = out_dir / f"assessment-results-stub-{today}.json"
    cat_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    ar_path.write_text(json.dumps(assessment_results, indent=2) + "\n", encoding="utf-8")

    return {"catalog": cat_path, "assessment_results": ar_path}
