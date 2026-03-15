# Contributing Guidelines

<!-- SPDX-License-Identifier: Apache-2.0 -->

We welcome contributions that improve security, automation, compliance coverage,
or documentation quality.  This project is a reference implementation for
enterprise, federal, and regulated delivery audiences — contributions must
meet the same standard of technical rigour.

---

## Getting Started

```bash
# 1. Fork and clone the repository
git clone https://github.com/<your-fork>/ato-control-traceability-engine.git
cd ato-control-traceability-engine

# 2. Create a feature branch
git checkout -b feature/my-improvement

# 3. Install in editable mode with dev dependencies
pip install -e ".[dev]"
pip install ruff

# 4. Make your changes, run tests and linting
ruff check src/ atoevidence/
pytest -q

# 5. Push and open a PR against main
git push origin feature/my-improvement
```

---

## Branching Model

| Branch | Purpose |
|---|---|
| `main` | Protected. All changes via PR with at least one reviewer approval. |
| `feature/<name>` | New capabilities |
| `fix/<name>` | Bug fixes |
| `docs/<name>` | Documentation-only changes |
| `chore/<name>` | Tooling, CI, dependency updates |

---

## Commit Message Standards

We follow the [Conventional Commits](https://www.conventionalcommits.org/)
specification.

```
<type>(<scope>): <short summary>

[optional body]
[optional footer]
```

| Type | When to use |
|---|---|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `docs` | Documentation change only |
| `test` | Adding or updating tests |
| `chore` | Tooling, CI, or dependency updates |
| `refactor` | Code restructuring without behaviour change |

**Examples:**
```
feat(src): add CSV export option for trace matrix
fix(artifact_registry): handle YAML files with null component_ids
docs(architecture): update data-flow diagram for new evidence model
```

---

## Code Quality Standards

- **Linting:** All Python code must pass `ruff check` with no errors.
- **Tests:** New Python functionality must be accompanied by pytest tests in
  `tests/` or `atoevidence/tests/`.
- **Type hints:** Use type annotations on all new function signatures.
- **Docstrings:** Public functions and modules require docstrings.
- **No secrets:** Never commit credentials, API keys, or sensitive data.
  Use environment variables or GitHub Secrets.
- **`yaml.safe_load()`:** All YAML parsing must use `safe_load()` — never
  the unsafe `yaml.load()`.

---

## Documentation Expectations

- Architecture diagrams must use Mermaid syntax embedded in Markdown.
- New capabilities should be reflected in:
  - `docs/architecture-overview.md` (if the pipeline changes)
  - `docs/use-cases.md` (if a new use case is enabled)
  - `controls/control-mapping.md` (if new controls are addressed)
  - `roadmap.md` (move completed items from future milestones)

---

## Adding New Controls

To add support for a new control or control family:

1. Add the control entry to `examples/control_catalog.yaml` (and any relevant
   real catalog files).
2. Add at least one example evidence metadata file to `examples/evidence/`.
3. Update `controls/control-mapping.md` with the capability → control mapping.
4. Re-run `atotrace trace ...` to regenerate example outputs.
5. Commit the updated `examples/control_trace_matrix.json` and
   `examples/traceability_graph.mmd`.

---

## Pull Request Checklist

Before opening a PR, confirm:

- [ ] `ruff check src/ atoevidence/` passes with no errors
- [ ] `pytest -q` passes (all existing tests + new tests)
- [ ] New functions have docstrings and type annotations
- [ ] Example outputs regenerated if catalog/inventory/evidence changed
- [ ] `CHANGELOG.md` updated with a brief description of the change
- [ ] No secrets or sensitive data committed

---

## Code of Conduct

All contributors are expected to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## License

By contributing, you agree that your contributions will be licensed under the
[Apache License, Version 2.0](LICENSE) of this repository.
