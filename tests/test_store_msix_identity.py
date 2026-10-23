"""Store-draft identity and manifest regression guards (offline, stdlib only)."""
import json
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "store" / "product_identity.json"
MANIFEST = ROOT / "store" / "AppxManifest.template.xml"
BUILDER = ROOT / "store" / "build_msix_draft.ps1"
WINDOWS_BUILDER = ROOT / "build_windows.ps1"
WORKFLOW = ROOT / ".github" / "workflows" / "windows-build.yml"

NAMESPACE = "http://schemas.microsoft.com/appx/manifest/foundation/windows10"
UAP10 = "http://schemas.microsoft.com/appx/manifest/uap/windows10/10"
EXPECTED_NAME = "OkinawaDesktopTools.WorkflowAutomationHub"
EXPECTED_PUBLISHER = "CN=46263F21-A700-41DB-8C9B-114C22FB82FC"
EXPECTED_PFN = "OkinawaDesktopTools.WorkflowAutomationHub_j8yefg9jgfh58"


class StoreIdentityDraftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.identity = json.loads(DATA.read_text(encoding="utf-8"))
        cls.template = MANIFEST.read_text(encoding="utf-8")

    def test_store_id_matches_owner_provided_partner_center(self):
        self.assertEqual(self.identity["store_id"], "9P6SXJNNB5KK")
        self.assertEqual(self.identity["package_identity_name"], EXPECTED_NAME)
        self.assertEqual(self.identity["publisher"], EXPECTED_PUBLISHER)
        self.assertEqual(self.identity["publisher_display_name"], "Okinawa Desktop Tools")
        self.assertEqual(self.identity["package_family_name"], EXPECTED_PFN)

    def test_pfn_is_exact_name_plus_13_character_windows_publisher_id(self):
        pfn_name, separator, publisher_id = self.identity["package_family_name"].rpartition("_")
        self.assertEqual(separator, "_")
        self.assertEqual(pfn_name, self.identity["package_identity_name"])
        self.assertEqual(len(publisher_id), 13)
        self.assertRegex(publisher_id, r"^[0-9a-hjkmnp-tv-z]{13}$")
        self.assertEqual(EXPECTED_PFN, f"{EXPECTED_NAME}_{publisher_id}")

    def test_never_confuse_product_draft_with_certified_package(self):
        self.assertEqual(self.identity["store_status_at_capture"], "In draft")
        self.assertIs(self.identity["submission_allowed"], False)
        self.assertEqual(self.identity["initial_msix_version"], "1.0.0.0")
        self.assertEqual(self.identity["legacy_initial_msix_version"], "0.1.0.0")
        self.assertEqual(self.identity["msix_package_version_status"], "TECHNICAL_DRAFT_ONLY_PUBLIC_RELEASE_HOLD")
        self.assertIs(self.identity["store_version_history_verified"], False)

    def test_valid_four_component_msix_version(self):
        version = self.identity["initial_msix_version"]
        self.assertRegex(version, r"^\d+\.\d+\.\d+\.0$")
        self.assertTrue(all(int(x) <= 65535 for x in version.split(".")))
        self.assertGreaterEqual(int(version.split(".")[0]), 1)

    def test_generated_manifest_identity_and_runtime_contract(self):
        replacements = {
            "__PACKAGE_IDENTITY_NAME__": self.identity["package_identity_name"],
            "__PUBLISHER__": self.identity["publisher"],
            "__PUBLISHER_DISPLAY_NAME__": self.identity["publisher_display_name"],
            "__VERSION__": self.identity["initial_msix_version"],
        }
        xmltext = self.template
        for key, value in replacements.items():
            self.assertIn(key, xmltext)
            xmltext = xmltext.replace(key, value)
        self.assertNotRegex(xmltext, r"__[A-Z_]+__")
        root = ET.fromstring(xmltext)
        ident = root.find(f"{{{NAMESPACE}}}Identity")
        self.assertIsNotNone(ident)
        self.assertEqual(ident.attrib["Name"], self.identity["package_identity_name"])
        self.assertEqual(ident.attrib["Publisher"], self.identity["publisher"])
        self.assertEqual(ident.attrib["Version"], self.identity["initial_msix_version"])
        self.assertEqual(ident.attrib["ProcessorArchitecture"], "x64")
        app = root.find(f".//{{{NAMESPACE}}}Application")
        self.assertIsNotNone(app)
        self.assertEqual(app.attrib[f"{{{UAP10}}}RuntimeBehavior"], "packagedClassicApp")
        self.assertEqual(app.attrib[f"{{{UAP10}}}TrustLevel"], "mediumIL")
        self.assertEqual(app.attrib["Executable"], "WorkflowAutomationHub.exe")
        self.assertIsNotNone(root.find(".//{*}Capability[@Name='runFullTrust']"))
        self.assertEqual(root.find(f"{{{NAMESPACE}}}Properties/{{{NAMESPACE}}}DisplayName").text, "Workflow Automation Hub")

    def test_ci_uses_signed_off_identity_builder_not_raw_exe_as_msix(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("store/build_msix_draft.ps1", workflow)
        self.assertIn("WorkflowAutomationHub-Store-MSIX-UNSIGNED-DRAFT", workflow)
        builder = BUILDER.read_text(encoding="utf-8")
        self.assertIn("MakeAppx.exe", builder)
        self.assertIn("unpack /p", builder)
        self.assertIn("manifest_identity_verified", builder)
        self.assertIn("submission_allowed", builder)
        self.assertIn("Store MSIX version major component must be >= 1", builder)
        self.assertIn("store_version_history_verified", builder)
        self.assertNotIn("SALES_RELEASE_APPROVED.txt", builder)

    def test_windows_builder_can_pin_the_base_python(self):
        builder = WINDOWS_BUILDER.read_text(encoding="utf-8")
        self.assertIn('param([string]$BasePythonPath = "")', builder)
        self.assertIn('& $BasePythonPath -m venv .venv', builder)
        self.assertIn('python -m venv .venv', builder)
        self.assertNotIn('py -3 -m venv .venv', builder)


if __name__ == "__main__":
    unittest.main()
