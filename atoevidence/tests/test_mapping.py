from pathlib import Path
from atoevidence.mapping import load_mapping

def test_load_mapping(tmp_path: Path):
    p = tmp_path / "m.yaml"
    p.write_text(
        "controls:\n"
        "  AU-2:\n"
        "    name: Audit Events\n"
        "    owner: Security\n"
        "    review_frequency_days: 30\n"
        "    implementation: impl.md\n"
        "    evidence: [e.md]\n"
        "    monitoring: [m.md]\n",
        encoding="utf-8",
    )
    m = load_mapping(str(p))
    assert "AU-2" in m
    assert m["AU-2"].review_frequency_days == 30
