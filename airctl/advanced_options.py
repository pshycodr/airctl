import ipaddress
from urllib.parse import urlparse

METERED_VALUES = ("auto", "metered", "unmetered")
PROXY_VALUES = ("none", "manual", "pac")
IP_VALUES = ("dhcp", "static")
PRIVACY_VALUES = ("random", "device")


def default_advanced_options() -> dict:
    return {
        "metered": "auto",
        "proxy": {
            "mode": "none",
            "host": None,
            "port": None,
            "pac_url": None,
        },
        "ip": {
            "mode": "dhcp",
            "address": None,
            "prefix": None,
            "gateway": None,
            "dns": [],
        },
        "privacy": "device",
        "send_device_name": True,
    }


def validate_password(password: str) -> str:
    if not isinstance(password, str) or not password:
        raise ValueError("Enter the Wi-Fi password.")

    if any(ord(character) < 32 or ord(character) == 127 for character in password):
        raise ValueError("The Wi-Fi password contains invalid characters.")

    if len(password) == 64 and all(character in "0123456789abcdefABCDEF" for character in password):
        return password

    if 8 <= len(password) <= 63:
        return password

    raise ValueError("The Wi-Fi password must be 8-63 characters or 64 hexadecimal digits.")


def normalize_advanced_options(options: dict | None) -> dict:
    if options is None:
        options = {}

    if not isinstance(options, dict):
        raise ValueError("Advanced options must be a mapping.")

    normalized = default_advanced_options()

    metered = options.get("metered", "auto")
    if metered not in METERED_VALUES:
        raise ValueError("Select a valid metered option.")
    normalized["metered"] = metered

    normalized["proxy"] = _normalize_proxy(options.get("proxy"))
    normalized["ip"] = _normalize_ip(options.get("ip"))

    privacy = options.get("privacy", "device")
    if privacy not in PRIVACY_VALUES:
        raise ValueError("Select a valid privacy option.")
    normalized["privacy"] = privacy

    send_device_name = options.get("send_device_name", True)
    if isinstance(send_device_name, str):
        values = {
            "send": True,
            "dont_send": False,
            "don't send": False,
        }
        if send_device_name not in values:
            raise ValueError("Select a valid device name option.")
        send_device_name = values[send_device_name]

    if not isinstance(send_device_name, bool):
        raise ValueError("Select a valid device name option.")
    normalized["send_device_name"] = send_device_name

    return normalized


def _normalize_proxy(proxy) -> dict:
    if proxy is None:
        proxy = {}

    if not isinstance(proxy, dict):
        raise ValueError("Proxy options must be a mapping.")

    mode = proxy.get("mode", "none")
    if mode not in PROXY_VALUES:
        raise ValueError("Select a valid proxy option.")

    normalized = {
        "mode": mode,
        "host": None,
        "port": None,
        "pac_url": None,
    }

    if mode == "manual":
        host = str(proxy.get("host") or "").strip()
        if not host:
            raise ValueError("Proxy host is required.")
        if any(character.isspace() for character in host) or "/" in host:
            raise ValueError("Enter a valid proxy host.")
        if ":" in host:
            address = host[1:-1] if host.startswith("[") and host.endswith("]") else host
            try:
                ipaddress.IPv6Address(address)
            except ValueError as error:
                raise ValueError("Enter a valid proxy host.") from error

        port = _parse_integer(proxy.get("port"), "Proxy port")
        if not 1 <= port <= 65535:
            raise ValueError("Proxy port must be between 1 and 65535.")

        normalized["host"] = host
        normalized["port"] = port

    elif mode == "pac":
        pac_url = str(proxy.get("pac_url") or "").strip()
        parsed = urlparse(pac_url)

        if (
            parsed.scheme not in ("http", "https")
            or not parsed.netloc
            or any(character.isspace() for character in pac_url)
        ):
            raise ValueError("Enter a valid PAC URL.")

        normalized["pac_url"] = pac_url

    return normalized


def _normalize_ip(ip) -> dict:
    if ip is None:
        ip = {}

    if not isinstance(ip, dict):
        raise ValueError("IP options must be a mapping.")

    mode = ip.get("mode", "dhcp")
    if mode not in IP_VALUES:
        raise ValueError("Select a valid IP option.")

    normalized = {
        "mode": mode,
        "address": None,
        "prefix": None,
        "gateway": None,
        "dns": [],
    }

    if mode == "static":
        address = str(ip.get("address") or "").strip()
        gateway = str(ip.get("gateway") or "").strip()

        try:
            ipaddress.IPv4Address(address)
        except ValueError as error:
            raise ValueError("Enter a valid IPv4 address.") from error

        if not gateway:
            raise ValueError("Gateway is required for a static IP.")
        try:
            ipaddress.IPv4Address(gateway)
        except ValueError as error:
            raise ValueError("Enter a valid IPv4 gateway.") from error

        prefix = _parse_integer(ip.get("prefix"), "Prefix length")
        if not 1 <= prefix <= 32:
            raise ValueError("IPv4 prefix must be between 1 and 32.")

        dns = _normalize_dns(ip.get("dns"))

        normalized["address"] = address
        normalized["prefix"] = prefix
        normalized["gateway"] = gateway
        normalized["dns"] = dns

    return normalized


def _normalize_dns(value) -> list[str]:
    if value is None:
        entries = []
    elif isinstance(value, str):
        entries = value.split(",")
    elif isinstance(value, (list, tuple)):
        entries = value
    else:
        raise ValueError("Enter valid DNS servers.")

    servers = []
    for entry in entries:
        address = str(entry).strip()
        if not address:
            continue

        try:
            ipaddress.IPv4Address(address)
        except ValueError as error:
            raise ValueError(f"Invalid DNS server: {address}") from error

        if address not in servers:
            servers.append(address)

    if not servers:
        raise ValueError("At least one DNS server is required for a static IP.")

    return servers


def _parse_integer(value, label: str) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError) as error:
        raise ValueError(f"{label} must be a number.") from error
