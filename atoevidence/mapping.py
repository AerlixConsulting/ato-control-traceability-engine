from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import yaml

@dataclass
class Control:
    control_id: str
    name: str
    owner: str
    review_frequency_days: int
    implementation: str
    evidence: List[str]
    monitoring: List[str]

def load_mapping(mapping_path: str) -> Dict[str, Control]:
    p = Path(mapping_path)
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "controls" not in data:
        raise ValueError("Mapping must be a YAML dict with top-level key 'controls'.")
    controls = data["controls"]
    if not isinstance(controls, dict):
        raise ValueError("'controls' must be a mapping of control_id -> fields.")

    out: Dict[str, Control] = {}
    for cid, fields in controls.items():
        if not isinstance(fields, dict):
            raise ValueError(f"{cid} fields must be a dict.")
        out[cid] = Control(
            control_id=cid,
            name=str(fields.get("name", "")).strip() or cid,
            owner=str(fields.get("owner", "Unassigned")).strip(),
            review_frequency_days=int(fields.get("review_frequency_days", 90)),
            implementation=str(fields.get("implementation", "")).strip(),
            evidence=list(fields.get("evidence", []) or []),
            monitoring=list(fields.get("monitoring", []) or []),
        )
    return out
