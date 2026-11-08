import re

from dbus_next.signature import Variant

METERED_METHODS = {
    "auto": 0,
    "metered": 2,
    "unmetered": 1,
}

HOSTNAME_V2_VERSION = (1, 52)


def parse_nm_version(value) -> tuple[int, ...]:
    match = re.match(r"(\d+)(?:\.(\d+))?(?:\.(\d+))?", str(value or ""))
    if not match:
        return (0,)

    return tuple(int(part) for part in match.groups() if part is not None)


def supports_hostname_v2(version: tuple[int, ...] | None) -> bool:
    return version is not None and version >= HOSTNAME_V2_VERSION


def build_pac_script(host: str, port: int) -> str:
    proxy_host = f"[{host}]" if ":" in host and not host.startswith("[") else host
    return f'function FindProxyForURL(url, host) {{ return "PROXY {proxy_host}:{port}; DIRECT"; }}'


def apply_advanced_settings(
    settings: dict,
    options: dict,
    nm_version: tuple[int, ...] | None = None,
) -> dict:
    connection = settings.setdefault("connection", {})
    connection["metered"] = Variant("i", METERED_METHODS[options["metered"]])

    _apply_proxy(settings, options["proxy"])

    wireless = settings.setdefault("802-11-wireless", {})
    wireless.pop("cloned-mac-address", None)
    wireless["assigned-mac-address"] = Variant(
        "s", "random" if options["privacy"] == "random" else "permanent"
    )

    _apply_ip(settings, options["ip"])
    _apply_hostname(settings, options["send_device_name"], nm_version)

    return settings


def _apply_proxy(settings: dict, proxy: dict):
    config = settings.setdefault("proxy", {})
    mode = proxy["mode"]

    if mode == "none":
        config["method"] = Variant("i", 0)
        config.pop("pac-url", None)
        config.pop("pac-script", None)
        return

    config["method"] = Variant("i", 1)

    if mode == "manual":
        config["pac-script"] = Variant("s", build_pac_script(proxy["host"], proxy["port"]))
        config.pop("pac-url", None)
        return

    config["pac-url"] = Variant("s", proxy["pac_url"])
    config.pop("pac-script", None)


def _apply_ip(settings: dict, ip: dict):
    config = settings.setdefault("ipv4", {})

    if ip["mode"] == "dhcp":
        config["method"] = Variant("s", "auto")
        for key in ("addresses", "gateway", "dns", "address-data", "dns-data"):
            config.pop(key, None)
        return

    config["method"] = Variant("s", "manual")
    config["address-data"] = Variant(
        "aa{sv}",
        [
            {
                "address": Variant("s", ip["address"]),
                "prefix": Variant("u", ip["prefix"]),
            }
        ],
    )
    config["gateway"] = Variant("s", ip["gateway"])
    config["dns-data"] = Variant("as", ip["dns"])
    config.pop("addresses", None)
    config.pop("dns", None)


def _apply_hostname(settings: dict, send_device_name: bool, nm_version):
    use_v2 = supports_hostname_v2(nm_version)

    for family in ("ipv4", "ipv6"):
        config = settings.setdefault(family, {})
        if family == "ipv6" and "method" not in config:
            config["method"] = Variant("s", "auto")

        if use_v2:
            config.pop("dhcp-send-hostname", None)
            config["dhcp-send-hostname-v2"] = Variant("i", 1 if send_device_name else 0)
        else:
            config.pop("dhcp-send-hostname-v2", None)
            config["dhcp-send-hostname"] = Variant("b", send_device_name)
