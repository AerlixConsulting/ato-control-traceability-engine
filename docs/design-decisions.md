# Design Decisions

<!-- SPDX-License-Identifier: Apache-2.0 -->

## DD-1: Pure Python Dataclasses (No External Schema Library)

**Decision:** Use Python standard-library `dataclasses` for all data models
rather than Pydantic, attrs, or marshmallow.

**Rationale:**
- Zero additional runtime dependencies for the core model layer.
- Dataclasses are universally understood and require no framework knowledge.
- Serialisation to/from JSON is handled by `dataclasses.asdict()` in the
  evidence linker, keeping the dependency surface minimal.
- Pydantic v2 is a significant dependency with potential version conflicts in
  constrained regulated environments; avoiding it reduces supply-chain risk.

**Trade-off:** No automatic schema validation at deserialization time.
Input validation is performed explicitly in the loader functions.

**Future:** If stricter schema validation is needed (e.g., for untrusted
external input), Pydantic v2 or `jsonschema` can be added as an optional
dependency behind a validation flag.

---

## DD-2: YAML-First Input Format

**Decision:** Accept YAML as the primary input format for inventory and
catalog files; support JSON as a secondary format for the inventory.

**Rationale:**
- YAML is widely used in the DevSecOps/GRC tooling ecosystem (Ansible, GitHub
  Actions, Kubernetes, Open Policy Agent).
- Comments in YAML files make them self-documenting for non-developer audiences
  (ISSOs, system owners) who must maintain them.
- JSON is accepted for the inventory because many asset management systems
  export JSON directly.

**Trade-off:** YAML introduces the known `yaml.load()` security concern.
Mitigated by exclusively using `yaml.safe_load()` throughout the codebase.

---

## DD-3: Evidence Metadata Separate from Artifact Content

**Decision:** Evidence artifacts are described by lightweight YAML metadata
files (`*.yaml` in the evidence directory) that reference — but do not embed —
the actual artifact content (PDFs, screenshots, JSON reports).

**Rationale:**
- Actual artifacts can be large binary files (PDFs, disk images) and should
  not be committed to source control.
- Separating metadata from content allows the traceability engine to run
  without access to the actual artifact files (useful in air-gapped or
  restricted environments).
- Metadata files are diff-friendly and can be reviewed in pull requests.
- The `path` field in the metadata can reference a shared drive, S3 bucket,
  Jira attachment, or local file path — the engine is agnostic.

---

## DD-4: Catalog-Driven Component Mapping

**Decision:** Component-to-control mappings are declared in the control
catalog YAML (via `component_mapping:` lists on each control) rather than
in the inventory.

**Rationale:**
- Controls are the authoritative unit in an ATO; it is more natural for the
  control catalog to declare which components implement it.
- Avoids duplicating mapping information: a single entry in the catalog
  is the source of truth rather than scattered references in component files.
- Supports the RMF workflow where the security team owns control mappings
  while platform teams own the component inventory.

**Trade-off:** Adding a new component requires the security team to update
the catalog to map it to relevant controls.  This is intentional — it
prevents undocumented components from silently appearing as in-scope.

---

## DD-5: Evidence Linking Strategy

**Decision:** An evidence artifact is attached to a `TraceLink` when it
references **both** the link's `control_id` and the link's `component_id`.
If an artifact's `component_ids` list is empty, it is treated as
control-level evidence and attached to all links for that control.

**Rationale:**
- Some evidence (e.g., a system-wide policy document) covers a control across
  all components; requiring component references would force artificial duplication.
- The empty-`component_ids` fallback handles "universal" evidence gracefully.
- Links without any evidence are marked `"partial"` rather than
  `"not_implemented"` because the component-control mapping in the catalog
  asserts that implementation exists; missing evidence is a documentation gap,
  not an implementation gap.

---

## DD-6: Click Over argparse for the CLI

**Decision:** Use the `click` library for the CLI rather than `argparse`.

**Rationale:**
- `click` is already a declared dependency of the `atoevidence` package.
- `click` provides automatic `--help` generation, type coercion, and
  composable command groups with less boilerplate.
- `click.Path(exists=True)` gives clear, user-friendly error messages for
  missing files without manual validation code.

---

## DD-7: Mermaid for Architecture Diagrams

**Decision:** All architecture diagrams use Mermaid syntax embedded in
Markdown files rather than binary image formats (PNG, SVG) or vendor-specific
tools (Visio, Lucidchart).

**Rationale:**
- Mermaid diagrams are text-based, diff-friendly, and rendered natively by
  GitHub, GitLab, and most modern documentation platforms.
- No tooling required to view diagrams — they render in the browser.
- Changes to diagrams are visible in pull request diffs.
- Can be exported to PNG/SVG via the Mermaid CLI (`mmdc`) for formal
  documentation packages.

---

## DD-8: Coexistence of `src/` and `atoevidence/`

**Decision:** The new `src/` package (traceability engine) and the existing
`atoevidence/` package (evidence management) coexist in the same repository
as separate Python packages.

**Rationale:**
- The `atoevidence/` package has established workflows, tests, and CI
  integration that must not be disrupted.
- `src/` provides complementary capabilities (inventory-to-matrix pipeline,
  Mermaid graph generation) rather than replacing `atoevidence/`.
- Future consolidation is straightforward once the `src/` API stabilises.

**Interaction:** `src/` is exposed via the `atotrace` CLI entrypoint;
`atoevidence/` continues to be exposed via the `atoevidence` CLI entrypoint.
