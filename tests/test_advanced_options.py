import unittest

from airctl.advanced_options import (
    default_advanced_options,
    normalize_advanced_options,
    validate_password,
)


class AdvancedOptionsTest(unittest.TestCase):
    def test_defaults(self):
        self.assertEqual(normalize_advanced_options(None), default_advanced_options())

    def test_manual_proxy(self):
        options = normalize_advanced_options(
            {
                "proxy": {
                    "mode": "manual",
                    "host": " proxy.example.com ",
                    "port": "8080",
                }
            }
        )

        self.assertEqual(options["proxy"]["mode"], "manual")
        self.assertEqual(options["proxy"]["host"], "proxy.example.com")
        self.assertEqual(options["proxy"]["port"], 8080)

    def test_pac_proxy(self):
        options = normalize_advanced_options(
            {"proxy": {"mode": "pac", "pac_url": "https://example.com/proxy.pac"}}
        )

        self.assertEqual(options["proxy"]["pac_url"], "https://example.com/proxy.pac")

    def test_static_ip(self):
        options = normalize_advanced_options(
            {
                "ip": {
                    "mode": "static",
                    "address": "192.168.1.50",
                    "prefix": "24",
                    "gateway": "192.168.1.1",
                    "dns": "1.1.1.1, 8.8.8.8,1.1.1.1",
                }
            }
        )

        self.assertEqual(options["ip"]["mode"], "static")
        self.assertEqual(options["ip"]["address"], "192.168.1.50")
        self.assertEqual(options["ip"]["prefix"], 24)
        self.assertEqual(options["ip"]["gateway"], "192.168.1.1")
        self.assertEqual(options["ip"]["dns"], ["1.1.1.1", "8.8.8.8"])

    def test_dhcp_clears_static_fields(self):
        options = normalize_advanced_options(
            {
                "ip": {
                    "mode": "dhcp",
                    "address": "192.168.1.50",
                    "prefix": 24,
                    "gateway": "192.168.1.1",
                    "dns": ["1.1.1.1"],
                }
            }
        )

        self.assertIsNone(options["ip"]["address"])
        self.assertIsNone(options["ip"]["prefix"])
        self.assertIsNone(options["ip"]["gateway"])
        self.assertEqual(options["ip"]["dns"], [])

    def test_invalid_manual_proxy_port(self):
        with self.assertRaisesRegex(ValueError, "between 1 and 65535"):
            normalize_advanced_options(
                {"proxy": {"mode": "manual", "host": "proxy.example.com", "port": "70000"}}
            )

    def test_invalid_manual_proxy_host(self):
        with self.assertRaisesRegex(ValueError, "proxy host"):
            normalize_advanced_options(
                {"proxy": {"mode": "manual", "host": "proxy.example.com:8080", "port": "8080"}}
            )

    def test_invalid_static_gateway(self):
        with self.assertRaisesRegex(ValueError, "IPv4 gateway"):
            normalize_advanced_options(
                {
                    "ip": {
                        "mode": "static",
                        "address": "192.168.1.50",
                        "prefix": "24",
                        "gateway": "gateway",
                        "dns": "1.1.1.1",
                    }
                }
            )

    def test_static_requires_dns(self):
        with self.assertRaisesRegex(ValueError, "DNS server"):
            normalize_advanced_options(
                {
                    "ip": {
                        "mode": "static",
                        "address": "192.168.1.50",
                        "prefix": "24",
                        "gateway": "192.168.1.1",
                        "dns": "",
                    }
                }
            )

    def test_password_length(self):
        self.assertEqual(validate_password("12345678"), "12345678")
        self.assertEqual(validate_password("a" * 64), "a" * 64)

        with self.assertRaises(ValueError):
            validate_password("short")

        with self.assertRaises(ValueError):
            validate_password("z" * 64)


if __name__ == "__main__":
    unittest.main()
