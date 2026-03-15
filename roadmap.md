# Roadmap

<!-- SPDX-License-Identifier: Apache-2.0 -->

This document outlines the planned development roadmap for the ATO Control
Traceability Engine.  Items are ordered roughly by priority within each
milestone.

---

## Milestone 1 — Core Engine (✅ Complete)

- [x] System component inventory loader (YAML/JSON)
- [x] Control catalog loader (NIST 800-53 style YAML)
- [x] Component-to-control trace link builder
- [x] Evidence artifact registry (directory scan)
- [x] Evidence-to-link enrichment with status tracking
- [x] Compliance trace matrix JSON export
- [x] Mermaid traceability graph generation
- [x] `atotrace` CLI with `trace` and `graph` commands
- [x] Evidence freshness scoring (`atoevidence freshness`)
- [x] OSCAL-style JSON stub export
- [x] Audit evidence bundle creation (ZIP + SHA-256 manifest)
- [x] NIST CSF / 800-53 / RMF control mapping documentation
- [x] Apache-2.0 licensing

---

## Milestone 2 — Schema Validation and Policy Enforcement

- [ ] JSON Schema definitions for inventory, catalog, and evidence YAML files
- [ ] Strict validation mode (`--validate-schema`) rejecting inputs that fail
      JSON Schema checks
- [ ] Policy rule engine: configurable thresholds for evidence coverage
      (e.g., fail CI if >10% of controls have `status: partial`)
- [ ] Custom baseline profiles (FedRAMP Low / Moderate / High overlays)
- [ ] Control inheritance and overlay support (parent/child control relationships)

---

## Milestone 3 — Integrations and Automation

- [ ] **OSCAL full compliance**: proper OSCAL 1.1.x catalog, component
      definition, SSP, and assessment results output (replacing stubs)
- [ ] **GRC platform connectors**: export adapters for ServiceNow GRC,
      Archer, and Xacta
- [ ] **GitHub Issues integration**: auto-create issues for partial-status
      controls and evidence gaps; close issues when evidence is added
- [ ] **Jira integration**: create remediation tickets from POA&M candidates
- [ ] **SIEM integration**: ingest real log samples from Splunk / OpenSearch
      as evidence metadata via API

---

## Milestone 4 — Multi-System and Inheritance

- [ ] **Multi-system support**: single catalog shared across multiple system
      inventories; consolidated cross-system compliance dashboard
- [ ] **Inherited controls**: model FedRAMP cloud service provider (CSP)
      inheritance — mark controls as fully/partially inherited from provider
- [ ] **System interconnections**: track data flows between systems and
      propagate control applicability across trust boundaries
- [ ] **Overlay support**: apply organization-defined parameters (ODPs) and
      overlay values to control descriptions in the catalog

---

## Milestone 5 — Dashboard and Reporting

- [ ] **HTML report generation**: self-contained HTML compliance dashboard
      rendered from the trace matrix JSON (no server required)
- [ ] **Trend tracking**: time-series evidence freshness and coverage metrics
      stored in a lightweight SQLite database
- [ ] **Metrics API**: simple REST API endpoint for CI/CD pipeline status
      polling (e.g., coverage percentage, stale control count)
- [ ] **Executive summary PDF**: one-page compliance status PDF for
      authorizing officials

---

## Milestone 6 — Cloud and Platform Integrations

- [ ] **AWS Security Hub integration**: ingest Security Hub findings as
      evidence artifacts and map them to 800-53 controls
- [ ] **AWS Config integration**: auto-populate evidence from Config Rule
      compliance results
- [ ] **Terraform provider**: declare component inventory and control
      mappings as Terraform resources; state file becomes inventory
- [ ] **Kubernetes operator**: watch cluster resources and auto-update
      component inventory on pod/service changes

---

## Long-Term Vision

- **AI-assisted evidence collection**: use LLM analysis to suggest evidence
  gaps and recommend existing artifacts for unmapped controls
- **Zero-trust architecture alignment**: extend control catalog to include
  NIST SP 800-207 zero-trust maturity indicators
- **FedRAMP automation**: direct integration with the FedRAMP automated
  package validation service
- **Supply chain integrity integration**: link SBOM artifacts and SLSA
  provenance attestations as evidence for SI-7 and CM-14 controls

---

## Contributing to the Roadmap

If you have a feature request or use case not listed here, please open a
GitHub Issue with the `enhancement` label and describe your scenario.  See
[CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.
