import unittest

from airctl.advanced_options import normalize_advanced_options
from airctl.dbus.network_manager.advanced import (
    apply_advanced_settings,
    build_pac_script,
    parse_nm_version,
    supports_hostname_v2,
)


def _settings(options=None, version=(1, 58, 1)):
    normalized = normalize_advanced_options(options)
    return apply_advanced_settings({}, normalized, version)


class AdvancedMappingTest(unittest.TestCase):
    def test_defaults(self):
        settings = _settings()

        self.assertEqual(settings["connection"]["metered"].value, 0)
        self.assertEqual(settings["proxy"]["method"].value, 0)
        self.assertEqual(settings["802-11-wireless"]["assigned-mac-address"].value, "permanent")
        self.assertEqual(settings["ipv4"]["method"].value, "auto")
        self.assertEqual(settings["ipv4"]["dhcp-send-hostname-v2"].value, 1)
        self.assertEqual(settings["ipv6"]["method"].value, "auto")
        self.assertEqual(settings["ipv6"]["dhcp-send-hostname-v2"].value, 1)

    def test_metered_and_privacy(self):
        settings = _settings({"metered": "unmetered", "privacy": "random"})

        self.assertEqual(settings["connection"]["metered"].value, 1)
        self.assertEqual(settings["802-11-wireless"]["assigned-mac-address"].value, "random")

    def test_manual_proxy_uses_pac_script(self):
        settings = _settings(
            {"proxy": {"mode": "manual", "host": "proxy.example.com", "port": 8080}}
        )

        self.assertEqual(settings["proxy"]["method"].value, 1)
        self.assertIn("PROXY proxy.example.com:8080; DIRECT", settings["proxy"]["pac-script"].value)
        self.assertNotIn("pac-url", settings["proxy"])

    def test_manual_proxy_brackets_ipv6_host(self):
        self.assertIn("[::1]:8080", build_pac_script("::1", 8080))

    def test_pac_proxy(self):
        settings = _settings({"proxy": {"mode": "pac", "pac_url": "https://example.com/proxy.pac"}})

        self.assertEqual(settings["proxy"]["method"].value, 1)
        self.assertEqual(settings["proxy"]["pac-url"].value, "https://example.com/proxy.pac")
        self.assertNotIn("pac-script", settings["proxy"])

    def test_none_proxy_clears_pac_fields(self):
        settings = {
            "proxy": {
                "method": None,
                "pac-url": "https://example.com/proxy.pac",
                "pac-script": "stale",
            }
        }

        apply_advanced_settings(settings, normalize_advanced_options(None), (1, 58, 1))

        self.assertEqual(settings["proxy"]["method"].value, 0)
        self.assertNotIn("pac-url", settings["proxy"])
        self.assertNotIn("pac-script", settings["proxy"])

    def test_static_ip(self):
        settings = _settings(
            {
                "ip": {
                    "mode": "static",
                    "address": "192.168.1.50",
                    "prefix": 24,
                    "gateway": "192.168.1.1",
                    "dns": ["1.1.1.1", "8.8.8.8"],
                }
            }
        )

        ipv4 = settings["ipv4"]
        self.assertEqual(ipv4["method"].value, "manual")
        address_data = ipv4["address-data"].value
        self.assertEqual(address_data[0]["address"].value, "192.168.1.50")
        self.assertEqual(address_data[0]["prefix"].value, 24)
        self.assertEqual(ipv4["gateway"].value, "192.168.1.1")
        self.assertEqual(ipv4["dns-data"].value, ["1.1.1.1", "8.8.8.8"])
        self.assertNotIn("addresses", ipv4)
        self.assertNotIn("dns", ipv4)

    def test_dhcp_clears_stale_addresses(self):
        settings = {
            "ipv4": {
                "method": None,
                "addresses": "stale",
                "gateway": "stale",
                "dns": "stale",
                "address-data": "stale",
                "dns-data": "stale",
            }
        }

        apply_advanced_settings(settings, normalize_advanced_options(None), (1, 58, 1))

        self.assertEqual(settings["ipv4"]["method"].value, "auto")
        for key in ("addresses", "gateway", "dns", "address-data", "dns-data"):
            self.assertNotIn(key, settings["ipv4"])

    def test_hostname_legacy_for_old_networkmanager(self):
        settings = _settings({"send_device_name": False}, version=(1, 50, 0))

        self.assertEqual(settings["ipv4"]["dhcp-send-hostname"].value, False)
        self.assertEqual(settings["ipv6"]["dhcp-send-hostname"].value, False)
        self.assertNotIn("dhcp-send-hostname-v2", settings["ipv4"])

    def test_version_helpers(self):
        self.assertEqual(parse_nm_version("1.58.1"), (1, 58, 1))
        self.assertTrue(supports_hostname_v2((1, 52)))
        self.assertFalse(supports_hostname_v2((1, 51, 9)))
        self.assertFalse(supports_hostname_v2(None))


if __name__ == "__main__":
    unittest.main()
