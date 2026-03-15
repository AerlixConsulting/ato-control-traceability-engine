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

"""Data models for the ATO Control Traceability Engine.

These dataclasses are the canonical in-memory representations used throughout
the pipeline.  They are intentionally dependency-free (stdlib only) so they
can be serialised to/from any format (JSON, YAML, CSV) by the caller.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Component:
    """A deployable or logical system component in the assessed information system."""

    id: str
    name: str
    type: str  # e.g. web_application, microservice, database, network_device
    owner: str
    description: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class Control:
    """A security or privacy control from a regulatory catalog (e.g. NIST 800-53)."""

    id: str
    title: str
    family: str
    description: str = ""
    baseline: List[str] = field(default_factory=list)
    # Component IDs explicitly mapped in the catalog
    component_mapping: List[str] = field(default_factory=list)


@dataclass
class EvidenceArtifact:
    """A piece of audit evidence that satisfies one or more controls for one or more components."""

    id: str
    title: str
    type: str  # test_result | policy | screenshot | log_sample | procedure | configuration
    path: str  # relative path or URL to the artifact
    description: str = ""
    control_ids: List[str] = field(default_factory=list)
    component_ids: List[str] = field(default_factory=list)
    date_collected: Optional[str] = None  # ISO-8601 date string


@dataclass
class TraceLink:
    """A resolved link between a single component and a single control, with supporting evidence."""

    component_id: str
    control_id: str
    evidence_ids: List[str] = field(default_factory=list)
    # implemented | partial | not_implemented | not_applicable
    status: str = "implemented"


@dataclass
class TraceMatrix:
    """The complete compliance traceability matrix for the assessed system."""

    system_id: str
    system_name: str
    generated: str  # ISO-8601 datetime string
    components: List[Component] = field(default_factory=list)
    controls: List[Control] = field(default_factory=list)
    links: List[TraceLink] = field(default_factory=list)
    evidence: List[EvidenceArtifact] = field(default_factory=list)
