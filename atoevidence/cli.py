from __future__ import annotations
import argparse
import sys
from pathlib import Path

from .mapping import load_mapping
from .render import render_evidence_index, render_status_report
from .freshness import compute_freshness, render_freshness_report
from .oscal_export import export_oscal_stubs
from .bundle import build_bundle

def cmd_validate(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    controls = load_mapping(args.mapping)

    missing = []
    for cid, c in controls.items():
        for rel in [c.implementation, *c.evidence, *c.monitoring]:
            if not rel or not (repo_root / rel).exists():
                missing.append((cid, rel))
    if missing:
        print("Missing referenced paths:")
        for cid, rel in missing:
            print(f"- {cid}: {rel}")
        return 1
    print("OK: mapping validated and referenced files exist.")
    return 0

def cmd_build_index(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    controls = load_mapping(args.mapping)
    out = render_evidence_index(controls)
    out_path = repo_root / "audit-support" / "evidence-index.generated.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out, encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0

def cmd_status_report(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    controls = load_mapping(args.mapping)
    out = render_status_report(controls)
    out_path = repo_root / "monitoring" / "control-status-report.generated.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out, encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0

def cmd_freshness(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    controls = load_mapping(args.mapping)
    results = compute_freshness(repo_root, controls)
    out = render_freshness_report(results)
    out_path = repo_root / "metrics" / "evidence-freshness.generated.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out, encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0

def cmd_oscal(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    controls = load_mapping(args.mapping)
    paths = export_oscal_stubs(repo_root, controls)
    print(f"Wrote {paths['catalog']}")
    print(f"Wrote {paths['assessment_results']}")
    return 0

def cmd_bundle(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    controls = load_mapping(args.mapping)

    include_paths = set([args.mapping])
    for c in controls.values():
        include_paths.add(c.implementation)
        include_paths.update(c.evidence)
        include_paths.update(c.monitoring)

    # include key audit navigation + metrics
    include_paths.update([
        "audit-support/evidence-index.md",
        "audit-support/auditor-walkthrough.md",
        "audit-support/evidence-bundle-guide.md",
        "metrics/control-metrics.md",
        "metrics/control-effectiveness-score.md",
    ])

    zip_path = build_bundle(repo_root, include_paths)
    print(f"Wrote bundle {zip_path}")
    return 0

def main() -> None:
    ap = argparse.ArgumentParser(prog="atoevidence", description="ATO Evidence Traceability CLI (portfolio)")
    ap.add_argument("--repo-root", default=".", help="Path to repository root")
    sub = ap.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="Validate mapping references exist")
    v.add_argument("mapping", help="Path to controls/control-mapping.yaml")
    v.set_defaults(func=cmd_validate)

    bi = sub.add_parser("build-index", help="Generate evidence index")
    bi.add_argument("mapping", help="Path to controls/control-mapping.yaml")
    bi.set_defaults(func=cmd_build_index)

    sr = sub.add_parser("status-report", help="Generate status report")
    sr.add_argument("mapping", help="Path to controls/control-mapping.yaml")
    sr.set_defaults(func=cmd_status_report)

    fr = sub.add_parser("freshness", help="Generate evidence freshness scoring report")
    fr.add_argument("mapping", help="Path to controls/control-mapping.yaml")
    fr.set_defaults(func=cmd_freshness)

    os = sub.add_parser("oscal", help="Export OSCAL-style JSON stubs")
    os.add_argument("mapping", help="Path to controls/control-mapping.yaml")
    os.set_defaults(func=cmd_oscal)

    b = sub.add_parser("bundle", help="Create audit evidence bundle zip")
    b.add_argument("mapping", help="Path to controls/control-mapping.yaml")
    b.set_defaults(func=cmd_bundle)

    args = ap.parse_args()
    try:
        sys.exit(args.func(args))
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
