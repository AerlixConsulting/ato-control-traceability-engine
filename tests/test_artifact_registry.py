# Copyright 2024 Aerlix Consulting
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Tests for src/artifact_registry.py — evidence directory scanning and lookup helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.artifact_registry import (
    find_artifacts_for_component,
    find_artifacts_for_control,
    load_artifact_registry,
)

GOOD_ARTIFACT = """\
id: ev-001
title: MFA Test Results 2025
type: test_result
path: evidence/mfa-test.pdf
description: Penetration test for MFA bypass
control_ids: [IA-2, AC-3]
component_ids: [auth-service]
date_collected: "2025-03-01"
"""

ANOTHER_ARTIFACT = """\
id: ev-002
title: TLS Scan
type: configuration
path: evidence/tls.json
control_ids: [SC-8]
component_ids: [api-gateway, web-frontend]
"""


class TestLoadArtifactRegistry:
    def test_loads_yaml_files(self, tmp_path: Path) -> None:
        (tmp_path / "ev-001.yaml").write_text(GOOD_ARTIFACT, encoding="utf-8")
        (tmp_path / "ev-002.yaml").write_text(ANOTHER_ARTIFACT, encoding="utf-8")
        registry = load_artifact_registry(str(tmp_path))
        assert len(registry) == 2
        assert "ev-001" in registry
        assert "ev-002" in registry

    def test_artifact_fields_populated(self, tmp_path: Path) -> None:
        (tmp_path / "ev.yaml").write_text(GOOD_ARTIFACT, encoding="utf-8")
        registry = load_artifact_registry(str(tmp_path))
        art = registry["ev-001"]
        assert art.title == "MFA Test Results 2025"
        assert art.type == "test_result"
        assert art.path == "evidence/mfa-test.pdf"
        assert art.control_ids == ["IA-2", "AC-3"]
        assert art.component_ids == ["auth-service"]
        assert art.date_collected == "2025-03-01"

    def test_skips_file_without_id(self, tmp_path: Path) -> None:
        (tmp_path / "no-id.yaml").write_text("title: No ID here\ntype: policy\n", encoding="utf-8")
        registry = load_artifact_registry(str(tmp_path))
        assert len(registry) == 0

    def test_skips_malformed_yaml(self, tmp_path: Path) -> None:
        (tmp_path / "bad.yaml").write_text("id: x\n  broken: [unclosed\n", encoding="utf-8")
        (tmp_path / "good.yaml").write_text(GOOD_ARTIFACT, encoding="utf-8")
        # Should not raise; bad file skipped, good file loaded
        registry = load_artifact_registry(str(tmp_path))
        assert "ev-001" in registry

    def test_missing_directory_raises(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_artifact_registry("/nonexistent/path/to/evidence")

    def test_empty_directory(self, tmp_path: Path) -> None:
        registry = load_artifact_registry(str(tmp_path))
        assert registry == {}

    def test_non_yaml_files_ignored(self, tmp_path: Path) -> None:
        (tmp_path / "notes.txt").write_text("id: should-not-load\n", encoding="utf-8")
        (tmp_path / "ev.yaml").write_text(GOOD_ARTIFACT, encoding="utf-8")
        registry = load_artifact_registry(str(tmp_path))
        assert len(registry) == 1

    def test_default_values_for_optional_fields(self, tmp_path: Path) -> None:
        (tmp_path / "minimal.yaml").write_text(
            "id: min\ntitle: Min\ntype: policy\npath: p.pdf\n",
            encoding="utf-8",
        )
        registry = load_artifact_registry(str(tmp_path))
        art = registry["min"]
        assert art.description == ""
        assert art.control_ids == []
        assert art.component_ids == []
        assert art.date_collected is None


class TestFindArtifacts:
    def _registry(self, tmp_path: Path):
        (tmp_path / "ev-001.yaml").write_text(GOOD_ARTIFACT, encoding="utf-8")
        (tmp_path / "ev-002.yaml").write_text(ANOTHER_ARTIFACT, encoding="utf-8")
        return load_artifact_registry(str(tmp_path))

    def test_find_by_control(self, tmp_path: Path) -> None:
        registry = self._registry(tmp_path)
        results = find_artifacts_for_control(registry, "IA-2")
        assert len(results) == 1
        assert results[0].id == "ev-001"

    def test_find_by_control_no_match(self, tmp_path: Path) -> None:
        registry = self._registry(tmp_path)
        results = find_artifacts_for_control(registry, "CM-99")
        assert results == []

    def test_find_by_component(self, tmp_path: Path) -> None:
        registry = self._registry(tmp_path)
        results = find_artifacts_for_component(registry, "api-gateway")
        assert len(results) == 1
        assert results[0].id == "ev-002"

    def test_find_by_component_multiple(self, tmp_path: Path) -> None:
        registry = self._registry(tmp_path)
        results = find_artifacts_for_component(registry, "web-frontend")
        ids = {r.id for r in results}
        assert "ev-002" in ids

    def test_find_control_multiple_results(self, tmp_path: Path) -> None:
        """AC-3 appears in ev-001; check multiple control refs work."""
        registry = self._registry(tmp_path)
        results = find_artifacts_for_control(registry, "AC-3")
        assert any(r.id == "ev-001" for r in results)
