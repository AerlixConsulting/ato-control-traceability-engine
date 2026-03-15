# Copyright 2024 Aerlix Consulting
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Tests for src/control_mapper.py — inventory loading, catalog loading, trace link building."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.control_mapper import build_trace_links, load_control_catalog, load_system_inventory
from src.models import Component, Control

# ── Helpers ──────────────────────────────────────────────────────────────────

INVENTORY_YAML = """\
system_id: test-system
system_name: Test System
components:
  - id: web-app
    name: Web Application
    type: web_application
    owner: Platform Team
    description: Test web app
    tags: [frontend]
  - id: db
    name: Database
    type: database
    owner: Data Team
"""

CATALOG_YAML = """\
catalog:
  source: NIST SP 800-53 Rev 5
  controls:
    AC-2:
      title: Account Management
      family: Access Control
      description: Manage accounts.
      baseline: [low, moderate, high]
      component_mapping: [web-app, db]
    SC-8:
      title: Transmission Confidentiality
      family: System and Communications Protection
      description: Encrypt in transit.
      baseline: [moderate, high]
      component_mapping: [web-app]
"""


# ── load_system_inventory ────────────────────────────────────────────────────

class TestLoadSystemInventory:
    def test_basic_yaml(self, tmp_path: Path) -> None:
        p = tmp_path / "inv.yaml"
        p.write_text(INVENTORY_YAML, encoding="utf-8")
        system_id, system_name, components = load_system_inventory(str(p))
        assert system_id == "test-system"
        assert system_name == "Test System"
        assert len(components) == 2
        assert components[0].id == "web-app"
        assert components[0].type == "web_application"
        assert components[0].tags == ["frontend"]

    def test_json_input(self, tmp_path: Path) -> None:
        data = {
            "system_id": "json-sys",
            "system_name": "JSON System",
            "components": [
                {"id": "svc", "name": "Service", "type": "microservice", "owner": "Team A"}
            ],
        }
        p = tmp_path / "inv.json"
        p.write_text(json.dumps(data), encoding="utf-8")
        sid, sname, comps = load_system_inventory(str(p))
        assert sid == "json-sys"
        assert len(comps) == 1
        assert comps[0].id == "svc"

    def test_missing_id_raises(self, tmp_path: Path) -> None:
        p = tmp_path / "bad.yaml"
        p.write_text(
            "system_id: s\nsystem_name: S\ncomponents:\n  - name: X\n    type: t\n    owner: O\n",
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="non-empty 'id'"):
            load_system_inventory(str(p))

    def test_default_values(self, tmp_path: Path) -> None:
        p = tmp_path / "minimal.yaml"
        p.write_text(
            "system_id: s\nsystem_name: S\ncomponents:\n  - id: c1\n    name: C1\n    type: t\n    owner: O\n",
            encoding="utf-8",
        )
        _, _, comps = load_system_inventory(str(p))
        assert comps[0].description == ""
        assert comps[0].tags == []


# ── load_control_catalog ─────────────────────────────────────────────────────

class TestLoadControlCatalog:
    def test_basic_catalog(self, tmp_path: Path) -> None:
        p = tmp_path / "cat.yaml"
        p.write_text(CATALOG_YAML, encoding="utf-8")
        controls = load_control_catalog(str(p))
        assert "AC-2" in controls
        assert "SC-8" in controls
        assert controls["AC-2"].title == "Account Management"
        assert controls["AC-2"].family == "Access Control"
        assert controls["AC-2"].baseline == ["low", "moderate", "high"]
        assert controls["AC-2"].component_mapping == ["web-app", "db"]

    def test_missing_catalog_key_raises(self, tmp_path: Path) -> None:
        p = tmp_path / "bad.yaml"
        p.write_text("controls:\n  AC-1:\n    title: foo\n", encoding="utf-8")
        with pytest.raises(ValueError, match="top-level key 'catalog'"):
            load_control_catalog(str(p))

    def test_empty_component_mapping_defaults(self, tmp_path: Path) -> None:
        p = tmp_path / "cat.yaml"
        p.write_text(
            "catalog:\n  controls:\n    CM-2:\n      title: Baseline\n      family: CM\n",
            encoding="utf-8",
        )
        controls = load_control_catalog(str(p))
        assert controls["CM-2"].component_mapping == []


# ── build_trace_links ────────────────────────────────────────────────────────

class TestBuildTraceLinks:
    def test_links_created_for_known_components(self, tmp_path: Path) -> None:
        inv_p = tmp_path / "inv.yaml"
        cat_p = tmp_path / "cat.yaml"
        inv_p.write_text(INVENTORY_YAML, encoding="utf-8")
        cat_p.write_text(CATALOG_YAML, encoding="utf-8")

        _, _, components = load_system_inventory(str(inv_p))
        controls = load_control_catalog(str(cat_p))
        links = build_trace_links(components, controls)

        # AC-2 maps to [web-app, db] → 2 links; SC-8 maps to [web-app] → 1 link
        assert len(links) == 3
        control_ids = {lnk.control_id for lnk in links}
        assert "AC-2" in control_ids
        assert "SC-8" in control_ids

    def test_unknown_component_ids_skipped(self) -> None:
        components = [Component(id="known", name="K", type="t", owner="O")]
        controls = {
            "AC-2": Control(
                id="AC-2",
                title="T",
                family="F",
                component_mapping=["known", "unknown-ghost"],
            )
        }
        links = build_trace_links(components, controls)
        assert len(links) == 1
        assert links[0].component_id == "known"

    def test_empty_inventory_yields_no_links(self) -> None:
        controls = {
            "AC-2": Control(id="AC-2", title="T", family="F", component_mapping=["web-app"])
        }
        links = build_trace_links([], controls)
        assert links == []

    def test_link_initial_status_is_implemented(self, tmp_path: Path) -> None:
        inv_p = tmp_path / "inv.yaml"
        cat_p = tmp_path / "cat.yaml"
        inv_p.write_text(INVENTORY_YAML, encoding="utf-8")
        cat_p.write_text(CATALOG_YAML, encoding="utf-8")
        _, _, components = load_system_inventory(str(inv_p))
        controls = load_control_catalog(str(cat_p))
        links = build_trace_links(components, controls)
        for link in links:
            assert link.status == "implemented"
            assert link.evidence_ids == []
