# Component Architecture

<!-- SPDX-License-Identifier: Apache-2.0 -->

This diagram shows the internal Python module structure of the engine and
the data types that flow between them.

```mermaid
%%{ init: { 'theme': 'base' } }%%
flowchart TD
    subgraph CLI["CLI Layer — src/cli.py"]
        CMD_TRACE["atotrace trace"]
        CMD_GRAPH["atotrace graph"]
    end

    subgraph CORE["Core Processing — src/"]
        MAPPER["control_mapper.py
        ──────────────────
        load_system_inventory()
        load_control_catalog()
        build_trace_links()"]

        REGISTRY["artifact_registry.py
        ──────────────────────
        load_artifact_registry()
        find_artifacts_for_control()
        find_artifacts_for_component()"]

        LINKER["evidence_linker.py
        ──────────────────
        enrich_links_with_evidence()
        build_trace_matrix()
        export_matrix_json()"]

        GRAPH["traceability_graph.py
        ─────────────────────
        build_mermaid_graph()
        save_graph()"]

        MODELS["models.py
        ─────────────────
        Component
        Control
        EvidenceArtifact
        TraceLink
        TraceMatrix"]
    end

    subgraph LEGACY["Existing Package — atoevidence/"]
        MAPPING["mapping.py\nControl dataclass"]
        RENDER["render.py\nMarkdown reports"]
        FRESH["freshness.py\nEvidence scoring"]
        OSCAL["oscal_export.py\nOSCAL JSON stubs"]
        BUNDLE["bundle.py\nZip audit bundle"]
        ATOEV_CLI["cli.py\natoevidence CLI"]
    end

    subgraph FILES["File System"]
        INVENTORY["system_inventory.yaml"]
        CATALOG["control_catalog.yaml"]
        EVDIR["evidence/*.yaml"]
        MATRIX_JSON["control_trace_matrix.json"]
        MMD["traceability_graph.mmd"]
        CTRL_YAML["controls/control-mapping.yaml"]
    end

    %% CLI → Core
    CMD_TRACE --> MAPPER
    CMD_TRACE --> REGISTRY
    CMD_TRACE --> LINKER
    CMD_TRACE --> GRAPH
    CMD_GRAPH --> GRAPH

    %% Core internal
    MAPPER --> MODELS
    REGISTRY --> MODELS
    LINKER --> MODELS
    GRAPH --> MODELS

    %% Legacy
    ATOEV_CLI --> MAPPING
    ATOEV_CLI --> RENDER
    ATOEV_CLI --> FRESH
    ATOEV_CLI --> OSCAL
    ATOEV_CLI --> BUNDLE

    %% File I/O
    INVENTORY --> MAPPER
    CATALOG --> MAPPER
    EVDIR --> REGISTRY
    CTRL_YAML --> ATOEV_CLI
    LINKER --> MATRIX_JSON
    GRAPH --> MMD

    classDef cli fill:#4A90D9,color:#fff,stroke:#2C5F8A
    classDef core fill:#27AE60,color:#fff,stroke:#1A7A42
    classDef legacy fill:#8E44AD,color:#fff,stroke:#5B2C6F
    classDef file fill:#ECF0F1,color:#2C3E50,stroke:#BDC3C7

    class CMD_TRACE,CMD_GRAPH cli
    class MAPPER,REGISTRY,LINKER,GRAPH,MODELS core
    class MAPPING,RENDER,FRESH,OSCAL,BUNDLE,ATOEV_CLI legacy
    class INVENTORY,CATALOG,EVDIR,MATRIX_JSON,MMD,CTRL_YAML file
```

---

## Module Summary

| Module | Package | Responsibility |
|---|---|---|
| `cli.py` | `src` | Click-based CLI; orchestrates pipeline |
| `control_mapper.py` | `src` | Loads inventory + catalog; builds trace links |
| `artifact_registry.py` | `src` | Scans evidence dir; builds artifact registry |
| `evidence_linker.py` | `src` | Enriches links; assembles + exports matrix |
| `traceability_graph.py` | `src` | Generates Mermaid graph from matrix |
| `models.py` | `src` | Pure dataclass definitions (no I/O) |
| `cli.py` | `atoevidence` | Legacy CLI: freshness, OSCAL, bundle |
| `mapping.py` | `atoevidence` | Legacy control dataclass + YAML loader |
| `freshness.py` | `atoevidence` | Evidence freshness scoring |
| `oscal_export.py` | `atoevidence` | OSCAL JSON stub export |
| `bundle.py` | `atoevidence` | Audit bundle ZIP creation |
