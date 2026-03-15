# Trust Boundaries

<!-- SPDX-License-Identifier: Apache-2.0 -->

This diagram identifies trust zones and data sensitivity classifications
within the ATO Control Traceability Engine deployment.

```mermaid
%%{ init: { 'theme': 'base' } }%%
flowchart TB
    subgraph TB_PUBLIC["Trust Zone: Public / Uncontrolled"]
        INTERNET["Internet / External Networks"]
    end

    subgraph TB_DEVELOPER["Trust Zone: Developer Workstation"]
        DEV_CLI["atotrace / atoevidence CLI"]
        DEV_FILES["Local copies of\ninventory, catalog, evidence"]
    end

    subgraph TB_VCS["Trust Zone: Version Control (GitHub)"]
        subgraph TB_REPO["Repository: ato-control-traceability-engine"]
            REPO_SRC["src/ — Engine code"]
            REPO_EXAMPLES["examples/ — Non-sensitive demo data"]
            REPO_CONTROLS["controls/ — Control mappings"]
            REPO_DOCS["docs/ + architecture/ — Documentation"]
        end
        subgraph TB_ACTIONS["GitHub Actions (Ephemeral Runner)"]
            CI_RUNNER["CI Pipeline\n(ruff + pytest + atotrace trace)"]
        end
        REPO_PROTECTED["Protected Branches\n(main — require PR + review)"]
    end

    subgraph TB_SENSITIVE["Trust Zone: Restricted — Actual Evidence Artifacts"]
        EVIDENCE_STORE["Evidence Store\n(SharePoint / S3 / Confluence)\n🔒 Access-controlled"]
        ACTUAL_ARTIFACTS["Actual PDFs, Screenshots,\nTest Reports, Log Exports\n⚠️ May contain sensitive data"]
    end

    subgraph TB_AUDIT["Trust Zone: Auditor / Assessor"]
        ASSESSOR_WS["Assessor Workstation\n(read-only access to bundle)"]
        OSCAL_TOOLS["OSCAL Processing Tools\n(GovReady, XSLT, etc.)"]
    end

    %% Public boundary
    INTERNET -.->|"no direct connection\n(offline tool)"| TB_VCS

    %% Developer → Repo
    DEV_CLI -->|"git push"| TB_REPO
    DEV_FILES -->|"committed as YAML metadata\n(no sensitive content)"| TB_REPO

    %% Repo → CI
    TB_REPO -->|"trigger on PR / push"| CI_RUNNER
    CI_RUNNER -->|"reads"| REPO_EXAMPLES
    CI_RUNNER -->|"generates outputs\n(matrix JSON, graph)"| REPO_EXAMPLES

    %% Repo → Evidence Store (out-of-band)
    DEV_FILES -.->|"actual artifacts stored\nout-of-band"| EVIDENCE_STORE
    EVIDENCE_STORE --- ACTUAL_ARTIFACTS

    %% Assessor access
    CI_RUNNER -->|"uploads audit bundle\n(atoevidence bundle)"| EVIDENCE_STORE
    EVIDENCE_STORE -->|"scoped read access"| ASSESSOR_WS
    ASSESSOR_WS --> OSCAL_TOOLS

    classDef public fill:#E74C3C,color:#fff,stroke:#C0392B
    classDef developer fill:#3498DB,color:#fff,stroke:#2980B9
    classDef vcs fill:#27AE60,color:#fff,stroke:#1A7A42
    classDef sensitive fill:#E67E22,color:#fff,stroke:#D35400
    classDef audit fill:#8E44AD,color:#fff,stroke:#6C3483

    class INTERNET public
    class DEV_CLI,DEV_FILES developer
    class REPO_SRC,REPO_EXAMPLES,REPO_CONTROLS,REPO_DOCS,CI_RUNNER,REPO_PROTECTED vcs
    class EVIDENCE_STORE,ACTUAL_ARTIFACTS sensitive
    class ASSESSOR_WS,OSCAL_TOOLS audit
```

---

## Trust Boundary Summary

| Zone | Contents | Sensitivity |
|---|---|---|
| **Public** | External networks | N/A — no access |
| **Developer Workstation** | CLI tools, local file copies | LOW — no production secrets |
| **Version Control (GitHub)** | Source code, YAML metadata, demo data | LOW — public repo; no sensitive evidence |
| **GitHub Actions** | Ephemeral CI runners | LOW — no secrets; read-only evidence |
| **Restricted Evidence Store** | Actual PDFs, test reports, log exports | **HIGH — may contain sensitive system info** |
| **Auditor / Assessor** | Read-only access to bundles and OSCAL | MEDIUM — scoped access only |

---

## Key Security Properties

1. **No secrets in source control** — all credentials are managed via GitHub
   Secrets / AWS IAM roles; no hard-coded secrets in any file.

2. **Evidence metadata ≠ evidence content** — YAML metadata files committed to
   the repository contain only paths and descriptions.  Actual evidence files
   (potentially sensitive) are stored out-of-band in an access-controlled store.

3. **`yaml.safe_load()` enforced everywhere** — all YAML parsing uses
   `safe_load()` to prevent arbitrary code execution via malicious YAML.

4. **Read-only CI runner** — the CI pipeline reads input files and writes
   outputs within the repository; it does not have write access to external
   systems.

5. **Branch protection** — the `main` branch requires a pull request and
   reviewer approval before any changes merge, preventing unauthorised
   modification of catalog or inventory files.
