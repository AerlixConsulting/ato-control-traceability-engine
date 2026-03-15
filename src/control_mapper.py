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

"""Control mapper: loads a controls catalog and maps system components to controls.

The control catalog YAML must have the following top-level structure::

    catalog:
      source: "NIST SP 800-53 Rev 5"
      controls:
        AC-1:
          title: Access Control Policy and Procedures
          family: Access Control
          description: >
            ...
          baseline: [low, moderate, high]
          component_mapping: [auth-service, api-gateway]

The :func:`build_trace_links` function derives :class:`~src.models.TraceLink`
objects from the ``component_mapping`` lists in each catalog control, then
cross-references the live inventory so only known components are linked.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Union

import yaml

from .models import Component, Control, TraceLink


def load_system_inventory(path: Union[str, Path]) -> tuple[str, str, List[Component]]:
    """Load a system component inventory from a YAML or JSON file.

    Returns a tuple of ``(system_id, system_name, components)``.

    The inventory file must have the structure::

        system_id: my-system
        system_name: My Information System
        components:
          - id: web-frontend
            name: Web Application Frontend
            type: web_application
            owner: Platform Team
            description: ...
            tags: [frontend]
    """
    p = Path(path)
    raw = p.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) if p.suffix in {".yaml", ".yml"} else json.loads(raw)

    if not isinstance(data, dict):
        raise ValueError(f"Inventory file {path!r} must be a YAML/JSON mapping at the top level.")

    system_id = str(data.get("system_id", "unknown-system"))
    system_name = str(data.get("system_name", system_id))
    raw_components = data.get("components", [])
    if not isinstance(raw_components, list):
        raise ValueError("'components' key must be a list.")

    components: List[Component] = []
    for item in raw_components:
        if not isinstance(item, dict):
            raise ValueError(f"Each component entry must be a dict, got: {type(item)}")
        cid = str(item.get("id", "")).strip()
        if not cid:
            raise ValueError("Every component must have a non-empty 'id' field.")
        components.append(
            Component(
                id=cid,
                name=str(item.get("name", cid)).strip(),
                type=str(item.get("type", "unknown")).strip(),
                owner=str(item.get("owner", "Unassigned")).strip(),
                description=str(item.get("description", "")).strip(),
                tags=list(item.get("tags", []) or []),
            )
        )
    return system_id, system_name, components


def load_control_catalog(path: Union[str, Path]) -> Dict[str, Control]:
    """Load a controls catalog from a YAML file and return a ``{control_id: Control}`` dict."""
    p = Path(path)
    data = yaml.safe_load(p.read_text(encoding="utf-8"))

    if not isinstance(data, dict) or "catalog" not in data:
        raise ValueError(f"Catalog file {path!r} must be a YAML dict with top-level key 'catalog'.")

    catalog_block = data["catalog"]
    raw_controls = catalog_block.get("controls", {})
    if not isinstance(raw_controls, dict):
        raise ValueError("'catalog.controls' must be a mapping of control_id -> fields.")

    out: Dict[str, Control] = {}
    for cid, fields in raw_controls.items():
        if not isinstance(fields, dict):
            raise ValueError(f"Control {cid!r} fields must be a dict.")
        out[cid] = Control(
            id=cid,
            title=str(fields.get("title", cid)).strip(),
            family=str(fields.get("family", "Unknown")).strip(),
            description=str(fields.get("description", "")).strip(),
            baseline=list(fields.get("baseline", []) or []),
            component_mapping=list(fields.get("component_mapping", []) or []),
        )
    return out


def build_trace_links(
    components: List[Component],
    controls: Dict[str, Control],
) -> List[TraceLink]:
    """Derive :class:`~src.models.TraceLink` objects from catalog ``component_mapping`` lists.

    Only component IDs that exist in *components* are linked; unknown IDs in
    the catalog are silently skipped so the catalog can include forward
    references to components not yet in the inventory.
    """
    known_ids = {c.id for c in components}
    links: List[TraceLink] = []

    for control in controls.values():
        for comp_id in control.component_mapping:
            if comp_id in known_ids:
                links.append(
                    TraceLink(
                        component_id=comp_id,
                        control_id=control.id,
                        status="implemented",
                    )
                )

    return links
