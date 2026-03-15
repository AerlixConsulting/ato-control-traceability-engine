# Data Flow Diagram

<!-- SPDX-License-Identifier: Apache-2.0 -->

This diagram traces the data transformations from raw input files through to
the final compliance matrix and traceability graph.

```mermaid
%%{ init: { 'theme': 'base' } }%%
flowchart LR
    subgraph Inputs["① Input Files"]
        INV["system_inventory.yaml\n──────────────────\nsystem_id\nsystem_name\ncomponents[]"]
        CAT["control_catalog.yaml\n──────────────────\ncatalog.source\ncatalog.controls{}"]
        EV["evidence/*.yaml\n──────────────────\nid, title, type\npath\ncontrol_ids[]\ncomponent_ids[]"]
    end

    subgraph Parse["② Parse & Validate"]
        P1["load_system_inventory()\n→ system_id, system_name\n   List[Component]"]
        P2["load_control_catalog()\n→ Dict[str, Control]"]
        P3["load_artifact_registry()\n→ Dict[str, EvidenceArtifact]"]
    end

    subgraph Map["③ Map & Link"]
        M1["build_trace_links()\n→ List[TraceLink]\n  component_id\n  control_id\n  status=partial"]
        M2["enrich_links_with_evidence()\n→ List[TraceLink]\n  + evidence_ids[]\n  + status=implemented|partial"]
    end

    subgraph Assemble["④ Assemble Matrix"]
        A1["build_trace_matrix()\n→ TraceMatrix\n──────────────────\nsystem_id\nsystem_name\ngenerated\ncomponents[]\ncontrols[]\nlinks[]\nevidence[]"]
    end

    subgraph Export["⑤ Export"]
        E1["export_matrix_json()\n→ control_trace_matrix.json"]
        E2["build_mermaid_graph()\n→ Mermaid flowchart LR text\n\nsave_graph()\n→ traceability_graph.mmd"]
    end

    INV --> P1
    CAT --> P2
    EV  --> P3

    P1 --> M1
    P2 --> M1
    M1 --> M2
    P3 --> M2

    P1 --> A1
    P2 --> A1
    M2 --> A1
    P3 --> A1

    A1 --> E1
    A1 --> E2
```

---

## Data Type Reference

### `Component`
```
id:          str   — unique identifier (matches component_mapping in catalog)
name:        str   — human-readable display name
type:        str   — web_application | microservice | database | ...
owner:       str   — team or individual responsible
description: str
tags:        List[str]
```

### `Control`
```
id:               str        — NIST 800-53 control ID (e.g. "AC-2")
title:            str
family:           str        — e.g. "Access Control"
description:      str
baseline:         List[str]  — ["low", "moderate", "high"]
component_mapping: List[str] — component IDs that implement this control
```

### `EvidenceArtifact`
```
id:             str        — unique artifact identifier
title:          str
type:           str        — test_result | policy | log_sample | configuration | procedure
path:           str        — relative path or URL to the artifact
description:    str
control_ids:    List[str]  — controls this evidence satisfies
component_ids:  List[str]  — components this evidence covers (empty = all)
date_collected: str|None   — ISO-8601 date
```

### `TraceLink`
```
component_id: str       — FK → Component.id
control_id:   str       — FK → Control.id
evidence_ids: List[str] — FK → EvidenceArtifact.id[]
status:       str       — implemented | partial | not_implemented | not_applicable
```

### `TraceMatrix` (JSON output shape)
```json
{
  "system_id": "ato-demo-system",
  "system_name": "...",
  "generated": "2025-03-15T10:00:00Z",
  "summary": {
    "total_components": 8,
    "total_controls": 17,
    "total_links": 51,
    "total_evidence_artifacts": 6,
    "implemented": 24,
    "partial": 27,
    "not_implemented": 0
  },
  "components": [...],
  "controls": [...],
  "trace_links": [...],
  "evidence_artifacts": [...]
}
```
