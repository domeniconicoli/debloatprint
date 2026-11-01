import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from probe import (
    format_report,
    parse_adapters,
    parse_cloud,
    parse_netapps,
    parse_product_config,
    parse_subscriptions,
)

PRODUCT = """<?xml version="1.0"?>
<prdcfgdyn2:ProductConfigDyn xmlns:dd="urn:dd" xmlns:prdcfgdyn2="urn:p">
  <prdcfgdyn2:ProductSettings>
    <dd:FriendlyName>HP LaserJet M110w</dd:FriendlyName>
    <dd:PowerSave>on</dd:PowerSave>
    <dd:PowerSaveTimeout>1hour</dd:PowerSaveTimeout>
    <prdcfgdyn2:ShutDownDelay>never</prdcfgdyn2:ShutDownDelay>
  </prdcfgdyn2:ProductSettings>
</prdcfgdyn2:ProductConfigDyn>
"""

NETAPPS = """<?xml version="1.0"?>
<nadyn:NetAppsDyn xmlns:dd="urn:dd" xmlns:nadyn="urn:n">
  <dd:MDNSSupport>enabled</dd:MDNSSupport>
  <dd:IPPSupport>enabled</dd:IPPSupport>
  <nadyn:DirectPrint>disabled</nadyn:DirectPrint>
</nadyn:NetAppsDyn>
"""

ADAPTERS = """<?xml version="1.0"?>
<io:Adapters xmlns:io="urn:io" xmlns:dd="urn:dd">
  <io:Adapter>
    <dd:Name>Wifi0</dd:Name>
    <dd:Power>on</dd:Power>
    <dd:IsConnected>true</dd:IsConnected>
    <io:WifiNetwork><dd:CommunicationMode>infrastructure</dd:CommunicationMode>
      <dd:SSID>686f6d652d77696669</dd:SSID></io:WifiNetwork>
  </io:Adapter>
  <io:Adapter>
    <dd:Name>Wifi1</dd:Name>
    <dd:Power>off</dd:Power>
    <dd:CommunicationMode>adHoc</dd:CommunicationMode>
  </io:Adapter>
</io:Adapters>
"""


class ParseTests(unittest.TestCase):
    def test_product_config(self):
        parsed = parse_product_config(PRODUCT)
        self.assertEqual(parsed["shutdown_delay"], "never")
        self.assertEqual(parsed["power_save"], "on")
        self.assertEqual(parsed["friendly_name"], "HP LaserJet M110w")

    def test_netapps_and_adapters(self):
        self.assertEqual(parse_netapps(NETAPPS)["direct_print"], "disabled")
        radios = {item["name"]: item for item in parse_adapters(ADAPTERS)}
        self.assertEqual(radios["Wifi0"]["ssid"], "home-wifi")
        self.assertEqual(radios["Wifi0"]["power"], "on")
        self.assertEqual(radios["Wifi1"]["power"], "off")

    def test_cloud_without_registration(self):
        parsed = parse_cloud(
            json.dumps({"cloudServicesEnabled": "true", "links": [{"rel": "newRegistration"}]})
        )
        self.assertFalse(parsed["registered"])
        self.assertEqual(parsed["cloud_services_enabled"], "true")

    def test_subscriptions_group_by_host(self):
        parsed = parse_subscriptions(
            json.dumps(
                {
                    "subscriptions": [
                        {
                            "eventCategory": "supply",
                            "callbackUri": "https://telemetry.example/supply",
                        },
                        {
                            "eventCategory": "jobError",
                            "callbackUri": "https://telemetry.example/jobError",
                        },
                    ]
                }
            )
        )
        self.assertEqual(parsed["count"], 2)
        self.assertEqual(parsed["hosts"]["telemetry.example"], ["supply", "jobError"])

    def test_report_mentions_the_open_radio(self):
        text = format_report(
            "192.168.1.50",
            {
                "product": parse_product_config(PRODUCT),
                "netapps": parse_netapps(NETAPPS),
                "adapters": parse_adapters(ADAPTERS),
                "cloud": {"registered": False, "cloud_services_enabled": "true"},
                "subscriptions": {"count": 0, "hosts": {}},
            },
        )
        self.assertIn("auto off: never", text)
        self.assertIn("Wifi0", text)
        self.assertIn("home-wifi", text)
        self.assertIn("not registered", text)
