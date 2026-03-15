# Control Mapping Reference

<!-- SPDX-License-Identifier: Apache-2.0 -->

This document maps the capabilities of the ATO Control Traceability Engine
to the NIST Cybersecurity Framework (CSF), NIST SP 800-53 Rev 5, and the
NIST Risk Management Framework (RMF) lifecycle.

---

## Capability-to-Control Mapping

### Capability: Component Inventory Management

**Description:** Load, validate, and maintain a structured inventory of all
system components within the authorization boundary.

| Framework | Control / Function | Mapping Rationale |
|---|---|---|
| NIST CSF | ID.AM-1: Physical devices and systems within the organization are inventoried | Inventory YAML defines all system components |
| NIST CSF | ID.AM-2: Software platforms and applications within the organization are inventoried | Covers microservices, databases, and web apps |
| NIST 800-53 | CM-8: System Component Inventory | Primary implementation of inventory management |
| NIST 800-53 | CM-2: Baseline Configuration | Inventory supports baseline configuration documentation |
| RMF Lifecycle | Step 2 — Categorize | Component inventory is fundamental to system categorization |
| RMF Lifecycle | Step 3 — Select | Inventory scope determines control selection |

---

### Capability: Control Catalog Loading and Mapping

**Description:** Ingest a NIST 800-53 (or similar) control catalog and map
controls to implementing system components.

| Framework | Control / Function | Mapping Rationale |
|---|---|---|
| NIST CSF | ID.GV-1: Organizational cybersecurity policy is established | Catalog defines applicable policies |
| NIST CSF | ID.RA-3: Threats, vulnerabilities, likelihoods, and impacts are identified | Control selection reflects risk decisions |
| NIST 800-53 | PL-2: System Security Plan | Control catalog is a core SSP input |
| NIST 800-53 | PL-7: Concept of Operations | Component-control mapping documents architecture |
| NIST 800-53 | CA-2: Control Assessments | Catalog provides assessment baseline |
| RMF Lifecycle | Step 3 — Select | Primary support for control selection activities |
| RMF Lifecycle | Step 4 — Implement | Maps controls to implementing components |

---

### Capability: Evidence Artifact Registration

**Description:** Discover, catalogue, and link audit evidence artifacts
(test results, policies, configurations, log samples) to controls and components.

| Framework | Control / Function | Mapping Rationale |
|---|---|---|
| NIST CSF | PR.IP-1: A baseline configuration of information technology / industrial control systems is created and maintained | Evidence includes configuration records |
| NIST CSF | DE.CM-1: The network is monitored to detect potential cybersecurity events | Log sample evidence supports detection |
| NIST 800-53 | CA-2: Control Assessments | Evidence supports assessment findings |
| NIST 800-53 | CA-7: Continuous Monitoring | Evidence freshness tracking enables continuous monitoring |
| NIST 800-53 | AU-2: Event Logging | Log sample artifacts map to AU-2 compliance |
| NIST 800-53 | AU-12: Audit Record Generation | Evidence confirms audit record generation |
| RMF Lifecycle | Step 5 — Assess | Evidence registry is the primary assessment input |
| RMF Lifecycle | Step 6 — Authorize | Complete evidence set supports authorization decision |

---

### Capability: Compliance Trace Matrix Generation

**Description:** Produce a machine-readable JSON matrix linking every
component to every applicable control with supporting evidence references
and implementation status.

| Framework | Control / Function | Mapping Rationale |
|---|---|---|
| NIST CSF | ID.GV-4: Governance and risk management processes address cybersecurity risks | Matrix documents governance posture |
| NIST CSF | RS.CO-5: Voluntary information sharing occurs with external stakeholders | Machine-readable matrix supports sharing |
| NIST 800-53 | PL-2: System Security Plan | Trace matrix is a machine-readable SSP supplement |
| NIST 800-53 | CA-5: Plan of Action and Milestones | Partial-status links identify POA&M candidates |
| NIST 800-53 | CA-6: Authorization | Provides authoritative traceability for ATO decision |
| NIST 800-53 | CM-8: System Component Inventory | Matrix supplements inventory with control coverage |
| RMF Lifecycle | Step 5 — Assess | Matrix is the primary assessment artifact |
| RMF Lifecycle | Step 6 — Authorize | Presented to AO as authoritative traceability evidence |
| RMF Lifecycle | Step 7 — Monitor | Matrix updated continuously as evidence is collected |

---

### Capability: Mermaid Traceability Graph Generation

**Description:** Produce a directed Mermaid graph visualising the
Component → Control → Evidence chain.

| Framework | Control / Function | Mapping Rationale |
|---|---|---|
| NIST CSF | ID.AM-3: Organizational communication and data flows are mapped | Graph is a data-flow and dependency map |
| NIST CSF | ID.BE-4: Dependencies and critical functions for delivery of critical services are established | Component relationships visible in graph |
| NIST 800-53 | PL-7: Concept of Operations | Graph supports CONOPS documentation |
| NIST 800-53 | SA-17: Developer Security and Privacy Architecture | Supports security architecture documentation |
| RMF Lifecycle | Step 2 — Categorize | Graph supports system boundary documentation |
| RMF Lifecycle | Step 5 — Assess | Visual aid for assessor walkthrough |

---

### Capability: Evidence Freshness Scoring

**Description:** Score the freshness of evidence artifacts relative to their
required review cadence; identify stale controls.

| Framework | Control / Function | Mapping Rationale |
|---|---|---|
| NIST CSF | DE.CM-6: External service provider activity is monitored | Freshness applies to third-party evidence |
| NIST CSF | RS.MI-3: Newly identified vulnerabilities are mitigated or documented | Stale evidence may indicate unaddressed vulnerabilities |
| NIST 800-53 | CA-7: Continuous Monitoring | Freshness scoring IS the continuous monitoring metric |
| NIST 800-53 | CA-7(1): Automated Support for Continuous Monitoring | Automated scoring supports CA-7(1) |
| NIST 800-53 | PL-4: Rules of Behavior | Review cadences are rules of behaviour for evidence |
| RMF Lifecycle | Step 7 — Monitor | Primary support for ongoing monitoring activities |

---

### Capability: OSCAL Export

**Description:** Generate OSCAL-style catalog and assessment results stubs
for import into OSCAL-aware tooling (GovReady, Trestle, Xacta, etc.).

| Framework | Control / Function | Mapping Rationale |
|---|---|---|
| NIST CSF | ID.GV-1: Organizational cybersecurity policy is established | OSCAL catalog documents policy posture |
| NIST 800-53 | CA-2: Control Assessments | Assessment results stub supports CA-2 |
| NIST 800-53 | SA-5: System Documentation | OSCAL output is machine-readable system documentation |
| RMF Lifecycle | Step 5 — Assess | OSCAL output is directly consumable by assessment tools |
| RMF Lifecycle | Step 6 — Authorize | OSCAL catalog supports authorization package |

---

### Capability: Audit Evidence Bundle Creation

**Description:** Package all referenced evidence files, the trace matrix, and
a signed MANIFEST into a versioned ZIP for assessor delivery.

| Framework | Control / Function | Mapping Rationale |
|---|---|---|
| NIST 800-53 | CA-3: Information Exchange | Secure evidence handoff to assessors |
| NIST 800-53 | AU-9: Protection of Audit Information | Bundle integrity via SHA-256 manifest |
| NIST 800-53 | SI-7: Software, Firmware, and Information Integrity | Manifest provides integrity verification |
| RMF Lifecycle | Step 5 — Assess | Primary evidence delivery mechanism |
| RMF Lifecycle | Step 6 — Authorize | ATO package delivery artefact |

---

## RMF Lifecycle Coverage Summary

| RMF Step | Engine Capability |
|---|---|
| **Step 1 — Prepare** | N/A (organisation-level) |
| **Step 2 — Categorize** | Component Inventory, Traceability Graph (boundary documentation) |
| **Step 3 — Select** | Control Catalog Loading, Component Mapping |
| **Step 4 — Implement** | Component-to-control links document implementation claims |
| **Step 5 — Assess** | Trace Matrix, Evidence Registry, OSCAL Export, Audit Bundle |
| **Step 6 — Authorize** | Complete matrix + bundle delivered to AO |
| **Step 7 — Monitor** | Evidence Freshness Scoring, CI/CD integration for continuous update |

---

## NIST CSF Function Coverage Summary

| CSF Function | Primary Capabilities |
|---|---|
| **Identify (ID)** | Component Inventory, Control Catalog, Traceability Graph |
| **Protect (PR)** | Evidence of control implementation (configuration, policies) |
| **Detect (DE)** | Evidence Freshness Scoring, Log Sample evidence type |
| **Respond (RS)** | POA&M candidates from partial-status links |
| **Recover (RC)** | N/A — out of scope for this tool |
