import ipaddress
import struct

from dbus_next.signature import Variant

from ..constants import (
    AP_FLAG_PRIVACY,
    AP_SEC_KEY_MGMT_802_1X,
    AP_SEC_KEY_MGMT_OWE,
    AP_SEC_KEY_MGMT_PSK,
    AP_SEC_KEY_MGMT_SAE,
)


def _value(value, default=None):
    if isinstance(value, Variant):
        return value.value
    if value is None:
        return default
    return value


def _get(mapping, key, default=None):
    if not mapping:
        return default
    return _value(mapping.get(key), default)


def _error_text(error) -> str:
    return getattr(error, "text", None) or str(error)


def _decode_ssid(value) -> str | None:
    if value is None:
        return None

    if isinstance(value, bytes):
        raw = value
    elif isinstance(value, (bytearray, list, tuple)):
        raw = bytes(value)
    else:
        return str(value)

    return raw.decode("utf-8", errors="replace")


def _band(frequency) -> str:
    if frequency is None:
        return ""

    try:
        frequency = int(frequency)
    except (TypeError, ValueError):
        return ""

    if 2400 <= frequency <= 2500:
        return "2.4GHz"
    if 4900 <= frequency <= 5900:
        return "5GHz"
    if 5925 <= frequency <= 7125:
        return "6GHz"

    return ""


def _security_from_ap(flags, wpa_flags, rsn_flags) -> str:
    parts = []

    if wpa_flags:
        parts.append("WPA1")

    if rsn_flags:
        if rsn_flags & (AP_SEC_KEY_MGMT_PSK | AP_SEC_KEY_MGMT_802_1X):
            parts.append("WPA2")
        if rsn_flags & AP_SEC_KEY_MGMT_SAE:
            parts.append("WPA3")
        if rsn_flags & AP_SEC_KEY_MGMT_OWE:
            parts.append("OWE")
        if not rsn_flags & (AP_SEC_KEY_MGMT_PSK | AP_SEC_KEY_MGMT_802_1X | AP_SEC_KEY_MGMT_SAE):
            parts.append("WPA2")

    if not parts and (flags or 0) & AP_FLAG_PRIVACY:
        parts.append("WEP")

    return " ".join(parts)


def _connection_matches(settings: dict, ssid: str) -> bool:
    connection = settings.get("connection") or {}

    if _get(connection, "type") != "802-11-wireless":
        return False

    if _get(connection, "id") == ssid:
        return True

    wireless = settings.get("802-11-wireless") or {}

    return _decode_ssid(_get(wireless, "ssid")) == ssid


def _unpack_ipv4(value) -> str:
    return str(ipaddress.IPv4Address(struct.pack("<I", int(value))))


def _netmask(prefix) -> str | None:
    if prefix is None:
        return None

    try:
        return str(ipaddress.IPv4Network(f"0.0.0.0/{int(prefix)}").netmask)
    except (TypeError, ValueError):
        return None


def _first_ipv4(config: dict) -> tuple[str | None, int | None]:
    for entry in config.get("AddressData") or []:
        address = _get(entry, "address")
        if not address:
            continue

        prefix = _get(entry, "prefix")

        if "/" in str(address):
            try:
                interface = ipaddress.IPv4Interface(str(address))
            except ValueError:
                continue
            return str(interface.ip), interface.network.prefixlen

        return str(address), int(prefix) if prefix is not None else None

    for entry in config.get("Addresses") or []:
        if not entry:
            continue

        try:
            return _unpack_ipv4(entry[0]), int(entry[1])
        except (TypeError, ValueError, struct.error):
            continue

    return None, None


def _first_ipv6(config: dict) -> str | None:
    fallback = None

    for entry in config.get("AddressData") or []:
        address = _get(entry, "address")
        if not address:
            continue

        address = str(address).split("/")[0]

        try:
            parsed = ipaddress.IPv6Address(address)
        except ValueError:
            continue

        if not parsed.is_link_local:
            return str(parsed)

        if fallback is None:
            fallback = str(parsed)

    return fallback


def _dns_servers(config: dict) -> list[str]:
    servers = []

    for entry in config.get("NameserverData") or []:
        address = _get(entry, "address")
        if address and str(address) not in servers:
            servers.append(str(address))

    if servers:
        return servers

    for value in config.get("Nameservers") or []:
        try:
            address = _unpack_ipv4(value)
        except (TypeError, ValueError, struct.error):
            continue
        if address not in servers:
            servers.append(address)

    return servers
