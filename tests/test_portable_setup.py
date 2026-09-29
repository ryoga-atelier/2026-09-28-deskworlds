import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from portable_setup import install_lively, lively_library, target_platform, ensure_upstream


class PortableSetupTests(unittest.TestCase):
    def test_platform_detection(self):
        with patch("platform.system", return_value="Windows"):
            self.assertEqual(target_platform("auto"), "windows")
        with patch("platform.system", return_value="Darwin"):
            self.assertEqual(target_platform("auto"), "macos")

    def test_reads_custom_library_without_modifying_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); library = base / "custom library"
            (library / "wallpapers").mkdir(parents=True)
            settings = base / "Lively Wallpaper/Settings.json"
            settings.parent.mkdir()
            original = json.dumps({"WallpaperDir": str(library), "OtherSetting": "keep"})
            settings.write_text(original, encoding="utf-8")
            self.assertEqual(lively_library(base), library)
            self.assertEqual(settings.read_text(encoding="utf-8"), original)

    def test_missing_or_invalid_library_stops_before_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                lively_library(Path(tmp))
            with self.assertRaises(ValueError):
                lively_library(explicit=tmp)

    def test_second_install_preserves_previous_package_and_uses_argument_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); source = base / "source folder"
            source.mkdir(); (source / "index.html").write_text("aquarium", encoding="utf-8")
            library = base / "Library"; (library / "wallpapers").mkdir(parents=True)
            exe = base / "Lively Wallpaper/Lively.exe"
            with patch("portable_setup.run") as dispatch:
                first = install_lively(source, library, exe, 2)
                second = install_lively(source, library, exe, 2)
            self.assertNotEqual(first["installed_folder"], second["installed_folder"])
            self.assertEqual((Path(first["installed_folder"]) / "index.html").read_text(), "aquarium")
            self.assertEqual(dispatch.call_args.args[0][-2:], ["--monitor", "2"])
            self.assertEqual(first["status"], "command_sent_visual_check_required")

    def test_wrong_pin_refuses_to_modify_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / "upstream/deskworlds"
            (source / ".git").mkdir(parents=True)
            with patch("portable_setup.subprocess.check_output", return_value="wrong-pin\n"):
                with self.assertRaisesRegex(ValueError, "pin mismatch"):
                    ensure_upstream(root)


if __name__ == "__main__":
    unittest.main()
