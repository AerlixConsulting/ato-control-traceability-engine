# System Context Diagram

<!-- SPDX-License-Identifier: Apache-2.0 -->

This diagram shows the ATO Control Traceability Engine in the context of the
broader ATO and continuous monitoring ecosystem.

```mermaid
%%{ init: { 'theme': 'base' } }%%
flowchart TB
    subgraph Actors["External Actors"]
        ISSO["🧑 ISSO / Security Team"]
        ASSESSOR["🔍 Third-Party Assessor\n(3PAO)"]
        DEVOPS["👩‍💻 DevSecOps Engineer"]
        AUTHORIZER["🏛️ Authorizing Official\n(AO)"]
    end

    subgraph Engine["ATO Control Traceability Engine"]
        CLI["atotrace CLI\natotrace trace / graph"]
        ATOEV["atoevidence CLI\nfreshness / bundle / oscal"]
    end

    subgraph Inputs["Input Artifacts"]
        INV["system_inventory.yaml\nComponent Inventory"]
        CAT["control_catalog.yaml\nControl Catalog"]
        EVDIR["evidence/*.yaml\nEvidence Metadata"]
    end

    subgraph Outputs["Output Artifacts"]
        MATRIX["control_trace_matrix.json\nCompliance Matrix"]
        GRAPH["traceability_graph.mmd\nMermaid Diagram"]
        BUNDLE["audit-evidence-bundle.zip\nAudit Bundle"]
        OSCAL["OSCAL JSON Stubs\ncatalog + assessment-results"]
    end

    subgraph Consumers["Downstream Consumers"]
        SSP["📄 System Security Plan\n(SSP)"]
        DASHBOARD["📊 Compliance Dashboard"]
        CICD["⚙️ CI/CD Pipeline\nGitHub Actions"]
        AUTHORIZER
    end

    ISSO -->|"maintains"| INV
    ISSO -->|"maintains"| CAT
    ISSO -->|"collects"| EVDIR
    DEVOPS -->|"runs"| CLI
    DEVOPS -->|"runs"| ATOEV

    INV --> CLI
    CAT --> CLI
    EVDIR --> CLI
    EVDIR --> ATOEV

    CLI --> MATRIX
    CLI --> GRAPH
    ATOEV --> BUNDLE
    ATOEV --> OSCAL

    MATRIX --> SSP
    MATRIX --> DASHBOARD
    GRAPH --> SSP
    BUNDLE --> ASSESSOR
    OSCAL --> ASSESSOR
    MATRIX --> CICD

    ASSESSOR -->|"reviews"| BUNDLE
    AUTHORIZER -->|"approves based on"| SSP
```

---

## Actors

| Actor | Role |
|---|---|
| **ISSO** | Maintains inventory, catalog, and evidence files; triggers pipeline |
| **DevSecOps Engineer** | Integrates engine into CI/CD; automates evidence collection |
| **Third-Party Assessor** | Consumes audit bundles and OSCAL exports for assessment activities |
| **Authorizing Official** | Uses SSP and compliance matrix to make risk acceptance decisions |

## System Boundary

The ATO Control Traceability Engine operates entirely within the source
control repository.  It has **no network dependencies** at runtime — all inputs
are local files and all outputs are local files.

The only external interaction is via the CI/CD pipeline which may publish
outputs to an artifact store or documentation site.
