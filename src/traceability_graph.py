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

"""Traceability graph generator: produces Mermaid flowchart text from a
:class:`~src.models.TraceMatrix`.

The resulting Mermaid diagram can be embedded in Markdown documentation,
rendered by GitHub's native Mermaid support, or piped through the Mermaid
CLI (``mmdc``) to produce PNG/SVG artefacts.

Graph layout (left to right)::

    [Component] --> [Control] --> [Evidence Artifact]

Node IDs in Mermaid are sanitised (spaces and special chars replaced with
underscores) so the diagram renders without quoting issues.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Union

from .models import TraceMatrix


def _node_id(raw: str) -> str:
    """Return a Mermaid-safe node identifier derived from *raw*."""
    return re.sub(r"[^A-Za-z0-9_]", "_", raw)


def _truncate(text: str, max_len: int = 30) -> str:
    """Truncate *text* to *max_len* chars for readable node labels."""
    return text if len(text) <= max_len else text[: max_len - 1] + "…"


def build_mermaid_graph(matrix: TraceMatrix, max_evidence_nodes: Optional[int] = 20) -> str:
    """Build a Mermaid ``flowchart LR`` diagram from *matrix*.

    Parameters
    ----------
    matrix:
        The :class:`~src.models.TraceMatrix` to visualise.
    max_evidence_nodes:
        Maximum number of evidence nodes to include.  Very large evidence sets
        produce noisy graphs; set to ``None`` to include all artifacts.

    Returns
    -------
    str
        The complete Mermaid diagram source as a string.
    """
    lines = [
        "%%{ init: { 'theme': 'base', 'themeVariables': { 'fontSize': '14px' } } }%%",
        "flowchart LR",
        "",
        "    %% ── Subgraph: Components ─────────────────────────────────────",
        "    subgraph Components",
    ]

    # Component nodes
    comp_by_id = {c.id: c for c in matrix.components}
    for comp in matrix.components:
        nid = _node_id(comp.id)
        label = _truncate(f"{comp.id}\\n{comp.name}")
        lines.append(f"        {nid}[{label!r}]")

    lines += ["    end", ""]

    # Control nodes
    lines += [
        "    %% ── Subgraph: Controls ──────────────────────────────────────",
        "    subgraph Controls",
    ]
    ctrl_by_id = {c.id: c for c in matrix.controls}
    for ctrl in matrix.controls:
        nid = _node_id(ctrl.id)
        label = _truncate(f"{ctrl.id}\\n{ctrl.title}")
        lines.append(f"        {nid}([{label!r}])")

    lines += ["    end", ""]

    # Evidence nodes (capped)
    evidence_list = list(matrix.evidence)
    if max_evidence_nodes is not None:
        evidence_list = evidence_list[:max_evidence_nodes]

    if evidence_list:
        lines += [
            "    %% ── Subgraph: Evidence ──────────────────────────────────────",
            "    subgraph Evidence",
        ]
        ev_ids_included = {a.id for a in evidence_list}
        for artifact in evidence_list:
            nid = _node_id(artifact.id)
            label = _truncate(f"{artifact.type}\\n{artifact.title}")
            lines.append(f"        {nid}{{'{label}'}}")
        lines += ["    end", ""]

    # Edges: Component → Control
    lines.append("    %% ── Edges: Component → Control ──────────────────────────")
    seen_links: set = set()
    for link in matrix.links:
        edge_key = (link.component_id, link.control_id)
        if edge_key in seen_links:
            continue
        seen_links.add(edge_key)
        if link.component_id in comp_by_id and link.control_id in ctrl_by_id:
            c_nid = _node_id(link.component_id)
            ctrl_nid = _node_id(link.control_id)
            lines.append(f"    {c_nid} --> {ctrl_nid}")

    # Edges: Control → Evidence
    if evidence_list:
        lines.append("")
        lines.append("    %% ── Edges: Control → Evidence ──────────────────────────")
        ev_ids_included = {a.id for a in evidence_list}
        seen_ctrl_ev_edges: set = set()
        for link in matrix.links:
            ctrl_nid = _node_id(link.control_id)
            for ev_id in link.evidence_ids:
                if ev_id in ev_ids_included:
                    edge_key = (link.control_id, ev_id)
                    if edge_key in seen_ctrl_ev_edges:
                        continue
                    seen_ctrl_ev_edges.add(edge_key)
                    ev_nid = _node_id(ev_id)
                    lines.append(f"    {ctrl_nid} --> {ev_nid}")

    # Style definitions
    lines += [
        "",
        "    %% ── Styles ──────────────────────────────────────────────────",
        "    classDef component fill:#4A90D9,stroke:#2C5F8A,color:#fff",
        "    classDef control  fill:#27AE60,stroke:#1A7A42,color:#fff",
        "    classDef evidence fill:#E67E22,stroke:#B85C0A,color:#fff",
    ]
    for comp in matrix.components:
        lines.append(f"    class {_node_id(comp.id)} component")
    for ctrl in matrix.controls:
        lines.append(f"    class {_node_id(ctrl.id)} control")
    for artifact in evidence_list:
        lines.append(f"    class {_node_id(artifact.id)} evidence")

    return "\n".join(lines) + "\n"


def save_graph(graph_text: str, output_path: Union[str, Path]) -> None:
    """Write *graph_text* to *output_path* (``*.mmd`` or ``*.md``)."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(graph_text, encoding="utf-8")
