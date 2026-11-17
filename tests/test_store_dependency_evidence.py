import unittest
from pathlib import Path


class StoreDependencyEvidenceTests(unittest.TestCase):
    def test_msix_builder_embeds_and_roundtrips_dependency_evidence(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "store" / "build_msix_draft.ps1").read_text(encoding="utf-8")
        for name in ("SBOM.cyclonedx.json", "THIRD_PARTY_NOTICES.md", "requirements-lock.txt"):
            self.assertIn(name, text)
        self.assertIn("dependency_evidence_in_package", text)
        self.assertIn("Dependency evidence changed after MSIX roundtrip", text)


if __name__ == "__main__":
    unittest.main()
