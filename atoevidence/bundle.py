from __future__ import annotations
from datetime import date
from pathlib import Path
import hashlib
import json
import zipfile
from typing import Iterable, Dict

def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def build_bundle(repo_root: Path, include_paths: Iterable[str]) -> Path:
    out_dir = repo_root / "dist"
    out_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    zip_path = out_dir / f"audit-evidence-bundle-{today}.zip"

    manifest: Dict[str, Dict[str, str]] = {}
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for rel in sorted(set(include_paths)):
            p = repo_root / rel
            if p.exists() and p.is_file():
                z.write(p, arcname=rel)
                manifest[rel] = {"sha256": _sha256(p)}

        # add manifest inside bundle
        manifest_bytes = (json.dumps({"generated": today, "files": manifest}, indent=2) + "\n").encode("utf-8")
        z.writestr("MANIFEST.json", manifest_bytes)

    return zip_path
