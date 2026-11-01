import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from guard import FLOOR, Refused, assert_allowed


class GuardTests(unittest.TestCase):
    def test_floor_blocks_printing_path(self):
        for name in ("wifi0", "IPP", "AirPrint", "bonjour", "mdns", "dhcp", "ipv4"):
            with self.assertRaises(Refused):
                assert_allowed(name)

    def test_profile_cannot_unprotect_ipp(self):
        with self.assertRaises(Refused):
            assert_allowed("ipp", extra_never_touch=[])

    def test_profile_changes_are_outside_the_floor(self):
        profile = json.loads(
            (ROOT / "profiles" / "hp-laserjet-m110w" / "profile.json").read_text()
        )
        self.assertTrue(FLOOR.issuperset(name.lower() for name in profile["never_touch"]))
        for change in profile["changes"]:
            assert_allowed(change["id"], profile["never_touch"])

    def test_extra_name_can_be_blocked(self):
        with self.assertRaises(Refused):
            assert_allowed("syslog", extra_never_touch=["syslog"])
