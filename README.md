# ATO Control Traceability Engine

<!-- SPDX-License-Identifier: Apache-2.0 -->

<p align="center">
  <strong>Component Inventory → Control Mapping → Evidence Linking → Compliance Trace Matrix</strong><br>
  <a href="https://aerlixconsulting.com">aerlixconsulting.com</a>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="Apache 2.0 License"></a>
  <a href=".github/workflows/ci.yml"><img src="https://img.shields.io/badge/CI-ruff%20%2B%20pytest-green" alt="CI"></a>
  <img src="https://img.shields.io/badge/python-%3E%3D3.9-blue" alt="Python 3.9+">
</p>

---

## Purpose

The ATO Control Traceability Engine is a Python-based reference implementation
that automates the construction and continuous maintenance of a compliance
traceability matrix for systems undergoing Authorization to Operate (ATO) under
NIST Risk Management Framework (RMF).

It ingests three sources of truth:

| Input | Description |
|---|---|
| **System Component Inventory** (`YAML/JSON`) | All components within the authorization boundary |
| **Control Catalog** (`YAML`) | Applicable NIST 800-53 controls mapped to components |
| **Evidence Artifacts** (`YAML metadata`) | Audit evidence: test results, policies, configs, log samples |

And produces two outputs:

| Output | Description |
|---|---|
| **Compliance Trace Matrix** (`JSON`) | Component ↔ Control ↔ Evidence links with status |
| **Traceability Graph** (`Mermaid .mmd`) | Visual directed graph: Components → Controls → Evidence |

---

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Run the full traceability pipeline
atotrace trace \
  --inventory examples/system_inventory.yaml \
  --catalog   examples/control_catalog.yaml \
  --evidence  examples/evidence \
  --matrix    examples/control_trace_matrix.json \
  --graph     examples/traceability_graph.mmd

# Re-generate graph from existing matrix
atotrace graph \
  --matrix examples/control_trace_matrix.json \
  --graph  examples/traceability_graph.mmd

# Evidence freshness scoring (existing atoevidence CLI)
atoevidence freshness controls/control-mapping.yaml

# Generate OSCAL-style JSON stubs
atoevidence oscal controls/control-mapping.yaml

# Create audit evidence bundle ZIP
atoevidence bundle controls/control-mapping.yaml
```

---

## Repository Structure

```
ato-control-traceability-engine/
├── src/                          # Core traceability engine
│   ├── __init__.py
│   ├── models.py                 # Dataclass definitions (Component, Control, TraceLink, …)
│   ├── control_mapper.py         # Inventory + catalog loader; trace link builder
│   ├── artifact_registry.py      # Evidence artifact directory scanner
│   ├── evidence_linker.py        # Evidence enrichment; matrix assembly + JSON export
│   ├── traceability_graph.py     # Mermaid graph generator
│   └── cli.py                    # atotrace CLI (click)
│
├── atoevidence/                  # Existing evidence management package
│   ├── cli.py                    # atoevidence CLI (validate, freshness, oscal, bundle)
│   ├── mapping.py                # Control YAML loader
│   ├── freshness.py              # Evidence freshness scoring
│   ├── oscal_export.py           # OSCAL JSON stub export
│   ├── bundle.py                 # Audit bundle ZIP creator
│   └── tests/                   # Package tests
│
├── examples/
│   ├── system_inventory.yaml     # Example: 8-component cloud system
│   ├── control_catalog.yaml      # Example: 17 NIST 800-53 Rev 5 controls
│   ├── evidence/                 # Example evidence metadata YAML files
│   ├── control_trace_matrix.json # Generated: compliance matrix
│   └── traceability_graph.mmd   # Generated: Mermaid diagram
│
├── docs/
│   ├── architecture-overview.md  # Pipeline + module responsibilities
│   ├── use-cases.md              # Six detailed use cases
│   └── design-decisions.md      # Eight documented design decisions
│
├── architecture/
│   ├── system-context.md         # Mermaid: actors + system boundary
│   ├── component-architecture.md # Mermaid: internal module structure
│   ├── data-flow.md              # Mermaid: data transformations
│   └── trust-boundaries.md      # Mermaid: trust zones + security properties
│
├── controls/
│   ├── control-mapping.md        # Capability → NIST CSF / 800-53 / RMF mapping
│   └── control-mapping.yaml     # atoevidence CLI input (freshness, OSCAL, bundle)
│
├── tests/                        # pytest tests for src/ modules
├── assets/                       # Visual assets (see assets/README.md)
├── .github/workflows/ci.yml      # CI: ruff lint + pytest
├── roadmap.md
├── CONTRIBUTING.md
└── LICENSE                       # Apache-2.0
```

---

## Example Output

### Trace Matrix Summary (`control_trace_matrix.json`)

```json
{
  "system_id": "ato-demo-system",
  "system_name": "ATO Demo Information System — Healthcare Analytics Platform",
  "generated": "2025-03-15T10:00:00Z",
  "summary": {
    "total_components": 8,
    "total_controls": 17,
    "total_links": 51,
    "total_evidence_artifacts": 6,
    "implemented": 24,
    "partial": 27,
    "not_implemented": 0
  }
}
```

### Traceability Graph (Mermaid preview)

The generated `examples/traceability_graph.mmd` file renders in GitHub as a
directed flowchart with three subgraphs: **Components** (blue), **Controls**
(green), and **Evidence** (orange).

---

## Architecture

See [docs/architecture-overview.md](docs/architecture-overview.md) for the
complete pipeline description.

Architecture diagrams (Mermaid):
- [System Context](architecture/system-context.md)
- [Component Architecture](architecture/component-architecture.md)
- [Data Flow](architecture/data-flow.md)
- [Trust Boundaries](architecture/trust-boundaries.md)

---

## Control Coverage

See [controls/control-mapping.md](controls/control-mapping.md) for the
complete capability-to-control mapping across:
- **NIST Cybersecurity Framework (CSF)** — Identify, Protect, Detect, Respond
- **NIST SP 800-53 Rev 5** — AC, AU, CA, CM, IA, PL, RA, SC, SI, SA families
- **NIST RMF Lifecycle** — Steps 2–7 (Categorize through Monitor)

---

## Security

- All YAML parsing uses `yaml.safe_load()` — no arbitrary code execution risk.
- No hard-coded secrets; all credentials managed via environment variables.
- Evidence metadata files contain paths only — actual sensitive artifacts are
  stored out-of-band in an access-controlled store.
- See [SECURITY.md](SECURITY.md) for vulnerability reporting instructions.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for branching model, commit standards,
and pull request checklist.

## License

Licensed under the [Apache License, Version 2.0](LICENSE).

Copyright 2024 Aerlix Consulting

## Contact

For questions or to propose collaborations: **dylan@aerlixconsulting.com**
