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

"""Evidence linker: enriches trace links with supporting evidence artifacts
and assembles the complete :class:`~src.models.TraceMatrix`.

Pipeline::

    components + controls  →  build_trace_links()  →  [TraceLink (no evidence)]
    [TraceLink] + registry →  enrich_links_with_evidence()  →  [TraceLink (with evidence)]
    everything             →  build_trace_matrix()  →  TraceMatrix
    TraceMatrix            →  export_matrix_json()  →  JSON file
"""

from __future__ import annotations

import dataclasses
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Union

from .models import Component, Control, EvidenceArtifact, TraceLink, TraceMatrix


def enrich_links_with_evidence(
    links: List[TraceLink],
    registry: Dict[str, EvidenceArtifact],
) -> List[TraceLink]:
    """Attach relevant evidence artifact IDs to each :class:`~src.models.TraceLink`.

    An artifact is considered relevant to a link if it references **both** the
    link's ``component_id`` and the link's ``control_id``.  If an artifact
    references the control but not a specific component the artifact is
    attached to all links for that control.
    """
    enriched: List[TraceLink] = []
    for link in links:
        evidence_ids: List[str] = []
        for artifact in registry.values():
            control_match = link.control_id in artifact.control_ids
            component_match = (
                link.component_id in artifact.component_ids
                or not artifact.component_ids  # control-level evidence applies to all
            )
            if control_match and component_match:
                evidence_ids.append(artifact.id)
        enriched.append(
            TraceLink(
                component_id=link.component_id,
                control_id=link.control_id,
                evidence_ids=sorted(set(evidence_ids)),
                # Downgrade to "partial" when the link has no supporting evidence
                status="implemented" if evidence_ids else "partial",
            )
        )
    return enriched


def build_trace_matrix(
    system_id: str,
    system_name: str,
    components: List[Component],
    controls: Dict[str, Control],
    links: List[TraceLink],
    evidence: Dict[str, EvidenceArtifact],
) -> TraceMatrix:
    """Assemble a :class:`~src.models.TraceMatrix` from all pipeline artifacts."""
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return TraceMatrix(
        system_id=system_id,
        system_name=system_name,
        generated=generated,
        components=list(components),
        controls=list(controls.values()),
        links=links,
        evidence=list(evidence.values()),
    )


def export_matrix_json(matrix: TraceMatrix, output_path: Union[str, Path]) -> None:
    """Serialise *matrix* to a JSON file at *output_path*.

    The output is a structured JSON document that is both human-readable and
    machine-parseable.  It can be consumed by dashboards, OSCAL processors, or
    downstream tooling.
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "system_id": matrix.system_id,
        "system_name": matrix.system_name,
        "generated": matrix.generated,
        "summary": {
            "total_components": len(matrix.components),
            "total_controls": len(matrix.controls),
            "total_links": len(matrix.links),
            "total_evidence_artifacts": len(matrix.evidence),
            "implemented": sum(1 for lnk in matrix.links if lnk.status == "implemented"),
            "partial": sum(1 for lnk in matrix.links if lnk.status == "partial"),
            "not_implemented": sum(1 for lnk in matrix.links if lnk.status == "not_implemented"),
        },
        "components": [dataclasses.asdict(c) for c in matrix.components],
        "controls": [dataclasses.asdict(c) for c in matrix.controls],
        "trace_links": [dataclasses.asdict(lnk) for lnk in matrix.links],
        "evidence_artifacts": [dataclasses.asdict(e) for e in matrix.evidence],
    }

    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
