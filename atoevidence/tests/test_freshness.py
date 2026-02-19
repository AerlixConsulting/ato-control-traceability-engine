from pathlib import Path
from atoevidence.freshness import _extract_latest_date_from_file

def test_extract_latest_date(tmp_path: Path):
    p = tmp_path / "x.md"
    p.write_text("Last Review: 2026-02-18\nNext: 2026-03-20\n", encoding="utf-8")
    d = _extract_latest_date_from_file(p)
    assert d is not None
    assert d.isoformat() == "2026-03-20"
