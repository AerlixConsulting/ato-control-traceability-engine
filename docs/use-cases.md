# Use Cases

<!-- SPDX-License-Identifier: Apache-2.0 -->

## UC-1: Initial ATO Package Assembly

**Actor:** Information System Security Officer (ISSO)

**Goal:** Produce an initial compliance trace matrix and traceability diagram
to accompany a System Security Plan (SSP) submission.

**Preconditions:**
- System component inventory documented in `examples/system_inventory.yaml`
- Applicable NIST 800-53 controls selected and cataloged in `examples/control_catalog.yaml`
- Initial evidence artifacts collected and described in `examples/evidence/*.yaml`

**Steps:**
1. ISSO runs:
   ```bash
   atotrace trace \
     --inventory examples/system_inventory.yaml \
     --catalog   examples/control_catalog.yaml \
     --evidence  examples/evidence \
     --matrix    ato-package/control_trace_matrix.json \
     --graph     ato-package/traceability_graph.mmd
   ```
2. Review `control_trace_matrix.json` — identify controls with `"status": "partial"`
   (i.e., no evidence yet collected).
3. Assign evidence collection tasks for partial controls to system owners.
4. Embed the Mermaid graph in the SSP or Confluence page for auditor visibility.

**Success criteria:**
- `control_trace_matrix.json` generated with summary statistics
- All high-baseline controls have at least one evidence artifact
- Traceability graph renders correctly in GitHub/Confluence

---

## UC-2: Continuous Monitoring — CI/CD Integration

**Actor:** DevSecOps pipeline (automated)

**Goal:** Automatically regenerate the trace matrix on every merge to `main`
that touches inventory, catalog, or evidence files.

**Steps:**
1. Developer commits an updated evidence YAML (e.g., new vulnerability scan result).
2. GitHub Actions `.github/workflows/ci.yml` triggers.
3. Pipeline runs `atotrace trace ...` with paths relative to repo root.
4. Outputs (`control_trace_matrix.json`, `traceability_graph.mmd`) are committed
   back to the repository or uploaded as CI artifacts.
5. Matrix `summary.partial` count is checked against a threshold; pipeline fails
   if more than N controls have no evidence.

**Success criteria:**
- Matrix regenerated on every relevant commit with zero manual intervention
- CI fails fast when evidence coverage drops below policy threshold

---

## UC-3: Evidence Freshness Review

**Actor:** ISSO / Continuous Monitoring Team

**Goal:** Identify stale evidence artifacts that have exceeded their required
review cadence.

**Steps:**
1. Run the freshness command (existing `atoevidence` package):
   ```bash
   atoevidence freshness controls/control-mapping.yaml
   ```
2. Review `metrics/evidence-freshness.generated.md` for controls with
   `status: Stale` or `status: Aging`.
3. File remediation tickets for owners of stale controls.
4. Re-collect evidence and update the corresponding YAML metadata files.
5. Re-run freshness report to verify improvement.

**Success criteria:**
- All critical controls show `status: Fresh`
- Freshness report exported as a CI artifact for auditor access

---

## UC-4: Auditor Walkthrough

**Actor:** Third-Party Assessor (3PAO)

**Goal:** Use the traceability engine outputs to navigate from a control ID to
its implementing components and supporting evidence without manual searching.

**Steps:**
1. Assessor opens `control_trace_matrix.json` and filters by `control_id: "IA-2"`.
2. Finds `component_id: auth-service` with `evidence_ids: ["ia-2-mfa-test-results-2025"]`.
3. Navigates to `examples/evidence/ia-2-mfa-test-results.yaml` for provenance
   metadata, then retrieves the actual artifact from the path field.
4. Confirms the artifact date is within the required review window.

**Success criteria:**
- Every required control has at least one resolvable evidence path
- The traceability graph provides a visual overview matching the matrix

---

## UC-5: New Control Addition

**Actor:** Security Architect

**Goal:** Add a new control (e.g., `SI-12 Information Management and Retention`)
to the catalog and immediately understand which components are affected and what
evidence needs to be collected.

**Steps:**
1. Add `SI-12` entry to `examples/control_catalog.yaml` with appropriate
   `component_mapping` entries.
2. Run `atotrace trace ...` — new `TraceLink` objects appear in the matrix
   with `status: partial` (no evidence yet).
3. Identify partial links and create evidence collection tasks.
4. Once evidence collected, add YAML metadata to `examples/evidence/`.
5. Re-run to confirm status changes from `partial` to `implemented`.

**Success criteria:**
- New control appears in matrix immediately after catalog update
- Evidence gap is visible and actionable before the next audit

---

## UC-6: Scope Reduction / Component Decommission

**Actor:** Platform Engineering Team

**Goal:** Remove a decommissioned component from the inventory and verify no
controls are left without any implementing component.

**Steps:**
1. Remove the component entry from `system_inventory.yaml`.
2. Remove or update `component_mapping` references in `control_catalog.yaml`.
3. Run `atotrace trace ...`.
4. Review matrix for any controls where all `component_ids` have been removed
   (these will appear as isolated control nodes in the Mermaid graph).
5. Either mark as `not_applicable` in the catalog or assign to a remaining component.

**Success criteria:**
- No orphaned control nodes in the traceability graph
- Matrix reflects reduced scope accurately
