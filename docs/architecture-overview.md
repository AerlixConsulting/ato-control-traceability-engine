# Architecture Overview

<!-- SPDX-License-Identifier: Apache-2.0 -->

## Purpose

The ATO Control Traceability Engine automates the construction and maintenance
of a compliance traceability matrix for information systems undergoing an
Authorization to Operate (ATO) or continuous monitoring programme under NIST
Risk Management Framework (RMF).

The engine ingests three sources of truth:

| Input | Format | Description |
|---|---|---|
| System Component Inventory | YAML / JSON | Authoritative list of all system components within the authorization boundary |
| Control Catalog | YAML | Subset of NIST SP 800-53 (or other catalog) controls applicable to the system |
| Evidence Artifacts | YAML (metadata) | Structured metadata for audit evidence: policies, test results, screenshots, logs |

It produces two outputs:

| Output | Format | Description |
|---|---|---|
| Compliance Trace Matrix | JSON | Machine-readable matrix linking every component to every applicable control, with supporting evidence |
| Traceability Graph | Mermaid (.mmd) | Human-readable directed graph: Components → Controls → Evidence |

---

## High-Level Pipeline

```
system_inventory.yaml
       │
       ▼
┌─────────────────────┐    control_catalog.yaml
│  control_mapper.py  │◄──────────────────────
│  load_system_       │
│  inventory()        │  1. Load components
│  load_control_      │  2. Load controls
│  catalog()          │  3. Build component↔control
│  build_trace_links()│     trace links
└─────────┬───────────┘
          │ TraceLink[]
          ▼
┌─────────────────────┐    examples/evidence/*.yaml
│ artifact_registry.py│◄──────────────────────────
│ load_artifact_      │
│ registry()          │  4. Scan evidence directory
└─────────┬───────────┘
          │ EvidenceArtifact{}
          ▼
┌─────────────────────┐
│  evidence_linker.py │
│  enrich_links_with_ │  5. Attach evidence IDs to
│  evidence()         │     each TraceLink
│  build_trace_matrix │  6. Assemble TraceMatrix
│  export_matrix_json │  7. Write JSON output
└─────────┬───────────┘
          │ TraceMatrix
          ▼
┌──────────────────────┐
│ traceability_graph.py│  8. Build Mermaid flowchart
│ build_mermaid_graph()│     LR diagram
│ save_graph()         │
└──────────────────────┘
```

---

## Module Responsibilities

### `src/models.py`
Pure dataclass definitions — no I/O, no dependencies beyond the Python
standard library.  All other modules import from here.

Key types: `Component`, `Control`, `EvidenceArtifact`, `TraceLink`,
`TraceMatrix`.

### `src/control_mapper.py`
Responsible for I/O and mapping:
- **`load_system_inventory()`** — parses inventory YAML/JSON into `Component` objects
- **`load_control_catalog()`** — parses catalog YAML into `{control_id: Control}` dict
- **`build_trace_links()`** — derives `TraceLink` objects from `component_mapping` lists in the catalog

### `src/artifact_registry.py`
Scans an evidence directory for `*.yaml` files and builds a
`{artifact_id: EvidenceArtifact}` dictionary.  Designed to be tolerant of
malformed files (warnings rather than hard failures).

### `src/evidence_linker.py`
- **`enrich_links_with_evidence()`** — iterates over trace links and attaches
  relevant artifact IDs based on `control_ids` and `component_ids` in each
  evidence YAML.  Marks links without evidence as `"partial"`.
- **`build_trace_matrix()`** — assembles the final `TraceMatrix` dataclass.
- **`export_matrix_json()`** — serialises the matrix to a structured JSON file
  with a human-friendly summary block.

### `src/traceability_graph.py`
Generates a Mermaid `flowchart LR` diagram with three subgraphs (Components,
Controls, Evidence) and styled directed edges.  Accepts a `max_evidence_nodes`
parameter to cap graph size.

### `src/cli.py`
Click-based CLI exposing two commands:
- **`atotrace trace`** — runs the full pipeline end-to-end
- **`atotrace graph`** — re-generates the Mermaid graph from an existing matrix

### `atoevidence/` *(existing package)*
The original ATO evidence management package handling freshness scoring,
OSCAL export, and audit bundle generation.  Retained alongside `src/` to
preserve backward compatibility.

---

## Data Flow Diagram

See [data-flow.md](../architecture/data-flow.md) for the full annotated
Mermaid diagram.

---

## Deployment Context

The engine is a **pure Python CLI tool** with no server component.  It is
designed to run:

1. **Locally** during ATO package assembly
2. **In CI/CD pipelines** on every commit that touches component inventory,
   control catalog, or evidence metadata
3. **Scheduled** (cron-based) to detect evidence freshness degradation

See [use-cases.md](use-cases.md) for detailed workflow descriptions.
