# Copyright 2024 Aerlix Consulting
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Tests for src/evidence_linker.py — enrichment, matrix assembly, JSON export shape."""

from __future__ import annotations

import json
from pathlib import Path

from src.evidence_linker import (
    build_trace_matrix,
    enrich_links_with_evidence,
    export_matrix_json,
)
from src.models import Component, Control, EvidenceArtifact, TraceLink

# ── Fixtures ─────────────────────────────────────────────────────────────────

def _components():
    return [
        Component(id="web-app", name="Web App", type="web_application", owner="Team"),
        Component(id="auth-svc", name="Auth Service", type="microservice", owner="SecTeam"),
    ]


def _controls():
    return {
        "IA-2": Control(id="IA-2", title="Auth", family="IA", component_mapping=["auth-svc"]),
        "SC-8": Control(id="SC-8", title="TLS", family="SC", component_mapping=["web-app"]),
    }


def _registry():
    return {
        "ev-mfa": EvidenceArtifact(
            id="ev-mfa",
            title="MFA Test",
            type="test_result",
            path="evidence/mfa.pdf",
            control_ids=["IA-2"],
            component_ids=["auth-svc"],
            date_collected="2025-03-01",
        ),
        "ev-tls": EvidenceArtifact(
            id="ev-tls",
            title="TLS Scan",
            type="configuration",
            path="evidence/tls.json",
            control_ids=["SC-8"],
            component_ids=["web-app"],
        ),
        "ev-policy": EvidenceArtifact(
            id="ev-policy",
            title="Access Control Policy",
            type="policy",
            path="evidence/policy.pdf",
            control_ids=["IA-2"],
            component_ids=[],  # control-level evidence — applies to all components
        ),
    }


# ── enrich_links_with_evidence ────────────────────────────────────────────────

class TestEnrichLinksWithEvidence:
    def test_exact_match_attached(self) -> None:
        links = [TraceLink(component_id="auth-svc", control_id="IA-2")]
        registry = _registry()
        enriched = enrich_links_with_evidence(links, registry)
        assert len(enriched) == 1
        # ev-mfa (exact) + ev-policy (control-level) both apply
        assert "ev-mfa" in enriched[0].evidence_ids
        assert "ev-policy" in enriched[0].evidence_ids
        assert enriched[0].status == "implemented"

    def test_control_level_evidence_no_component_ids(self) -> None:
        """Artifact with empty component_ids should attach to all links for its control."""
        links = [
            TraceLink(component_id="auth-svc", control_id="IA-2"),
            TraceLink(component_id="web-app", control_id="IA-2"),
        ]
        # Only control-level evidence for IA-2
        registry = {
            "ev-policy": EvidenceArtifact(
                id="ev-policy",
                title="Policy",
                type="policy",
                path="p.pdf",
                control_ids=["IA-2"],
                component_ids=[],
            )
        }
        enriched = enrich_links_with_evidence(links, registry)
        for link in enriched:
            assert "ev-policy" in link.evidence_ids
            assert link.status == "implemented"

    def test_no_evidence_yields_partial(self) -> None:
        links = [TraceLink(component_id="auth-svc", control_id="CM-2")]
        enriched = enrich_links_with_evidence(links, _registry())
        assert enriched[0].status == "partial"
        assert enriched[0].evidence_ids == []

    def test_wrong_component_not_attached(self) -> None:
        links = [TraceLink(component_id="web-app", control_id="IA-2")]
        registry = {
            "ev-mfa": EvidenceArtifact(
                id="ev-mfa",
                title="MFA",
                type="test_result",
                path="p",
                control_ids=["IA-2"],
                component_ids=["auth-svc"],  # wrong component
            )
        }
        enriched = enrich_links_with_evidence(links, registry)
        assert "ev-mfa" not in enriched[0].evidence_ids

    def test_evidence_ids_deduplicated(self) -> None:
        links = [TraceLink(component_id="auth-svc", control_id="IA-2")]
        # Two identical evidence entries
        registry = {
            "ev-a": EvidenceArtifact(
                id="ev-a", title="A", type="t", path="p",
                control_ids=["IA-2"], component_ids=["auth-svc"]
            ),
            "ev-a2": EvidenceArtifact(
                id="ev-a", title="A2", type="t", path="p",  # same id, different dict key
                control_ids=["IA-2"], component_ids=["auth-svc"]
            ),
        }
        enriched = enrich_links_with_evidence(links, registry)
        # IDs should be deduplicated
        assert len(enriched[0].evidence_ids) == len(set(enriched[0].evidence_ids))


# ── build_trace_matrix ────────────────────────────────────────────────────────

class TestBuildTraceMatrix:
    def test_matrix_fields(self) -> None:
        comps = _components()
        ctrls = _controls()
        links = [TraceLink(component_id="auth-svc", control_id="IA-2", evidence_ids=["ev-mfa"])]
        registry = _registry()
        matrix = build_trace_matrix("sys-1", "System 1", comps, ctrls, links, registry)
        assert matrix.system_id == "sys-1"
        assert matrix.system_name == "System 1"
        assert len(matrix.components) == 2
        assert len(matrix.controls) == 2
        assert len(matrix.links) == 1
        assert len(matrix.evidence) == len(registry)
        assert matrix.generated  # non-empty ISO string

    def test_matrix_generated_timestamp_format(self) -> None:
        matrix = build_trace_matrix("s", "S", [], {}, [], {})
        # Should match YYYY-MM-DDTHH:MM:SSZ
        import re
        assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", matrix.generated)


# ── export_matrix_json ────────────────────────────────────────────────────────

class TestExportMatrixJson:
    def test_output_shape(self, tmp_path: Path) -> None:
        comps = _components()
        ctrls = _controls()
        links = enrich_links_with_evidence(
            build_trace_links_from_controls(comps, ctrls), _registry()
        )
        matrix = build_trace_matrix("sys-1", "System 1", comps, ctrls, links, _registry())
        out = tmp_path / "matrix.json"
        export_matrix_json(matrix, str(out))

        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))

        # Required top-level keys
        for key in ("system_id", "system_name", "generated", "summary",
                    "components", "controls", "trace_links", "evidence_artifacts"):
            assert key in data, f"Missing key: {key}"

        # Summary sub-keys
        for key in ("total_components", "total_controls", "total_links",
                    "total_evidence_artifacts", "implemented", "partial"):
            assert key in data["summary"], f"Missing summary key: {key}"

        # Summary counts match list lengths
        assert data["summary"]["total_components"] == len(data["components"])
        assert data["summary"]["total_controls"] == len(data["controls"])
        assert data["summary"]["total_links"] == len(data["trace_links"])
        assert data["summary"]["total_evidence_artifacts"] == len(data["evidence_artifacts"])

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        matrix = build_trace_matrix("s", "S", [], {}, [], {})
        out = tmp_path / "deep" / "nested" / "matrix.json"
        export_matrix_json(matrix, str(out))
        assert out.exists()

    def test_implemented_partial_counts(self, tmp_path: Path) -> None:
        comps = _components()
        ctrls = _controls()
        # auth-svc → IA-2 has evidence (implemented)
        # web-app → SC-8 has evidence (implemented)
        links = [
            TraceLink(component_id="auth-svc", control_id="IA-2",
                      evidence_ids=["ev-mfa"], status="implemented"),
            TraceLink(component_id="web-app", control_id="SC-8",
                      evidence_ids=[], status="partial"),
        ]
        matrix = build_trace_matrix("s", "S", comps, ctrls, links, {})
        out = tmp_path / "m.json"
        export_matrix_json(matrix, str(out))
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["summary"]["implemented"] == 1
        assert data["summary"]["partial"] == 1


# ── Helper (avoids importing build_trace_links here — keeps test isolation) ──

def build_trace_links_from_controls(components, controls):
    """Minimal inline helper — mirrors control_mapper.build_trace_links logic."""
    from src.models import TraceLink as TL
    known = {c.id for c in components}
    return [
        TL(component_id=cmp_id, control_id=ctrl.id)
        for ctrl in controls.values()
        for cmp_id in ctrl.component_mapping
        if cmp_id in known
    ]
