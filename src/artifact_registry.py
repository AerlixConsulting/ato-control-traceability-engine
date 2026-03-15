# Copyright 2024 Aerlix Consulting
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Artifact registry: discovers and loads evidence artifact metadata.

Each evidence artifact is described by a small YAML file (conventionally
stored in ``examples/evidence/`` or ``evidence/`` in a real deployment).

Artifact YAML schema::

    id: ac-2-account-audit-2025
    title: Account Management Audit Report — Q1 2025
    type: test_result          # test_result | policy | log_sample | procedure | configuration
    path: evidence/ac-2-account-audit-2025.pdf
    description: Quarterly account management review
    control_ids: [AC-2, AC-3]
    component_ids: [auth-service, api-gateway]
    date_collected: "2025-03-15"

The :func:`load_artifact_registry` function scans a directory for ``*.yaml``
files that contain an ``id`` field and returns a ``{artifact_id: EvidenceArtifact}``
dictionary.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Union

import yaml

from .models import EvidenceArtifact


def load_artifact_registry(evidence_dir: Union[str, Path]) -> Dict[str, EvidenceArtifact]:
    """Scan *evidence_dir* for ``*.yaml`` evidence metadata files.

    Returns a ``{artifact_id: EvidenceArtifact}`` mapping.  Files that do not
    contain an ``id`` field are skipped with a warning rather than raising an
    exception so a single bad file does not break the whole registry load.
    """
    d = Path(evidence_dir)
    if not d.is_dir():
        raise FileNotFoundError(f"Evidence directory not found: {evidence_dir!r}")

    registry: Dict[str, EvidenceArtifact] = {}
    for yaml_file in sorted(d.glob("*.yaml")):
        try:
            data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            # Skip malformed files and continue
            print(f"[artifact_registry] Warning: could not parse {yaml_file}: {exc}")
            continue

        if not isinstance(data, dict):
            continue

        artifact_id = str(data.get("id", "")).strip()
        if not artifact_id:
            continue  # not an artifact metadata file

        artifact = EvidenceArtifact(
            id=artifact_id,
            title=str(data.get("title", artifact_id)).strip(),
            type=str(data.get("type", "unknown")).strip(),
            path=str(data.get("path", "")).strip(),
            description=str(data.get("description", "")).strip(),
            control_ids=list(data.get("control_ids", []) or []),
            component_ids=list(data.get("component_ids", []) or []),
            date_collected=str(data.get("date_collected", "")).strip() or None,
        )
        registry[artifact_id] = artifact

    return registry


def find_artifacts_for_control(
    registry: Dict[str, EvidenceArtifact],
    control_id: str,
) -> List[EvidenceArtifact]:
    """Return all artifacts in *registry* that reference *control_id*."""
    return [a for a in registry.values() if control_id in a.control_ids]


def find_artifacts_for_component(
    registry: Dict[str, EvidenceArtifact],
    component_id: str,
) -> List[EvidenceArtifact]:
    """Return all artifacts in *registry* that reference *component_id*."""
    return [a for a in registry.values() if component_id in a.component_ids]
