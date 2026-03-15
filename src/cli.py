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

"""CLI entrypoint for the ATO Control Traceability Engine (``atotrace``).

Commands
--------
trace
    Full pipeline: load inventory + catalog + evidence, output trace matrix
    JSON and an optional Mermaid graph.

graph
    Re-generate a Mermaid graph from an existing trace matrix JSON file.

Usage examples::

    # Full pipeline
    atotrace trace \\
        --inventory examples/system_inventory.yaml \\
        --catalog   examples/control_catalog.yaml \\
        --evidence  examples/evidence \\
        --matrix    examples/control_trace_matrix.json \\
        --graph     examples/traceability_graph.mmd

    # Graph only from existing matrix
    atotrace graph \\
        --matrix examples/control_trace_matrix.json \\
        --graph  examples/traceability_graph.mmd
"""

from __future__ import annotations

import json
from pathlib import Path

import click

from .artifact_registry import load_artifact_registry
from .control_mapper import build_trace_links, load_control_catalog, load_system_inventory
from .evidence_linker import build_trace_matrix, enrich_links_with_evidence, export_matrix_json
from .models import Component, Control, EvidenceArtifact, TraceLink, TraceMatrix
from .traceability_graph import build_mermaid_graph, save_graph


@click.group()
@click.version_option(package_name="atoevidence")
def main() -> None:
    """ATO Control Traceability Engine — trace components to controls to evidence."""


@main.command()
@click.option(
    "--inventory",
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    help="Path to system component inventory YAML/JSON.",
)
@click.option(
    "--catalog",
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    help="Path to control catalog YAML.",
)
@click.option(
    "--evidence",
    "evidence_dir",
    default=None,
    type=click.Path(exists=True, file_okay=False),
    help="Path to directory containing evidence artifact YAML metadata files.",
)
@click.option(
    "--matrix",
    "matrix_out",
    default="control_trace_matrix.json",
    show_default=True,
    help="Output path for the compliance trace matrix JSON.",
)
@click.option(
    "--graph",
    "graph_out",
    default=None,
    help="Output path for the Mermaid traceability graph (.mmd). Omit to skip.",
)
def trace(
    inventory: str,
    catalog: str,
    evidence_dir: str | None,
    matrix_out: str,
    graph_out: str | None,
) -> None:
    """Run the full traceability pipeline and produce the compliance matrix."""
    click.echo(f"[atotrace] Loading inventory: {inventory}")
    system_id, system_name, components = load_system_inventory(inventory)
    click.echo(f"[atotrace] System: {system_name!r} ({len(components)} components)")

    click.echo(f"[atotrace] Loading control catalog: {catalog}")
    controls = load_control_catalog(catalog)
    click.echo(f"[atotrace] Loaded {len(controls)} controls")

    links = build_trace_links(components, controls)
    click.echo(f"[atotrace] Built {len(links)} component-control trace links")

    registry: dict = {}
    if evidence_dir:
        click.echo(f"[atotrace] Loading evidence artifacts from: {evidence_dir}")
        registry = load_artifact_registry(evidence_dir)
        click.echo(f"[atotrace] Loaded {len(registry)} evidence artifacts")
        links = enrich_links_with_evidence(links, registry)
        click.echo("[atotrace] Enriched links with evidence")

    matrix = build_trace_matrix(system_id, system_name, components, controls, links, registry)
    export_matrix_json(matrix, matrix_out)
    click.echo(f"[atotrace] Wrote trace matrix → {matrix_out}")

    if graph_out:
        graph_text = build_mermaid_graph(matrix)
        save_graph(graph_text, graph_out)
        click.echo(f"[atotrace] Wrote Mermaid graph → {graph_out}")

    # Print summary
    impl = sum(1 for lnk in links if lnk.status == "implemented")
    partial = sum(1 for lnk in links if lnk.status == "partial")
    click.echo(
        f"\n[atotrace] Summary: {len(components)} components | "
        f"{len(controls)} controls | {len(links)} links "
        f"({impl} implemented, {partial} partial)"
    )


@main.command()
@click.option(
    "--matrix",
    "matrix_in",
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    help="Path to existing trace matrix JSON.",
)
@click.option(
    "--graph",
    "graph_out",
    default="traceability_graph.mmd",
    show_default=True,
    help="Output path for the Mermaid graph file.",
)
def graph(matrix_in: str, graph_out: str) -> None:
    """Re-generate a Mermaid traceability graph from an existing matrix JSON."""
    click.echo(f"[atotrace] Loading matrix: {matrix_in}")
    raw = json.loads(Path(matrix_in).read_text(encoding="utf-8"))

    # Reconstruct lightweight TraceMatrix from JSON
    matrix = TraceMatrix(
        system_id=raw.get("system_id", ""),
        system_name=raw.get("system_name", ""),
        generated=raw.get("generated", ""),
        components=[
            Component(**{k: v for k, v in c.items()}) for c in raw.get("components", [])
        ],
        controls=[
            Control(**{k: v for k, v in c.items()}) for c in raw.get("controls", [])
        ],
        evidence=[
            EvidenceArtifact(**{k: v for k, v in e.items()})
            for e in raw.get("evidence_artifacts", [])
        ],
    )

    matrix.links = [
        TraceLink(**{k: v for k, v in lnk.items()}) for lnk in raw.get("trace_links", [])
    ]

    graph_text = build_mermaid_graph(matrix)
    save_graph(graph_text, graph_out)
    click.echo(f"[atotrace] Wrote Mermaid graph → {graph_out}")


if __name__ == "__main__":
    main()
