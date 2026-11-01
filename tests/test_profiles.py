import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from probe import collected_never_touch, main, verify_profile, verify_profiles


def _write(root: Path, folder: str, profile: dict) -> Path:
    path = root / folder
    path.mkdir()
    target = path / "profile.json"
    target.write_text(json.dumps(profile))
    return target


def _profile(change_id="wifi-direct", never=None):
    return {
        "id": "desk-printer",
        "models": ["Desk Printer"],
        "never_touch": never
        or ["wifi0", "ipv4", "dhcp", "ipp", "airprint", "bonjour"],
        "changes": [
            {
                "id": change_id,
                "why": "it is unused",
                "risk": "low",
                "verify": "home wifi still answers",
                "restore": "turn it back on",
                "request": {"method": "PUT", "url": "http://{host}/example"},
            }
        ],
    }


class ProfileTests(unittest.TestCase):
    def test_repo_profiles_pass(self):
        self.assertEqual(verify_profiles(), [])
        self.assertIn("ipp", collected_never_touch())

    def test_walks_every_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = _profile()
            _write(root, "desk-printer", first)
            second = _profile()
            second["id"] = "other-printer"
            second["never_touch"] = list(first["never_touch"]) + ["syslog"]
            _write(root, "other-printer", second)
            self.assertEqual(verify_profiles(root), [])
            self.assertIn("syslog", collected_never_touch(root))

    def test_rejects_a_change_on_the_floor(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = _write(root, "desk-printer", _profile(change_id="ipp"))
            problems = verify_profile(path)
            self.assertTrue(any("ipp is on the never-touch list" in line for line in problems))

    def test_rejects_a_dropped_never_touch_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = _write(
                root,
                "desk-printer",
                _profile(never=["wifi0", "ipv4", "dhcp", "ipp", "airprint"]),
            )
            problems = verify_profile(path)
            self.assertTrue(any("drops bonjour" in line for line in problems))

    def test_cli_prints_each_repo_profile(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main(["--profiles"])
        self.assertEqual(code, 0)
        self.assertIn("hp-laserjet-m110w: 4 changes, never-touch ok", stdout.getvalue())

    def test_cli_refuses_a_name_from_the_profiles(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--check", "bonjour"]), 2)
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.assertEqual(main(["--check", "wifi-direct"]), 0)
        self.assertIn("wifi-direct is not on the never-touch list", stdout.getvalue())
