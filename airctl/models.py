import ipaddress
from dataclasses import dataclass, field


@dataclass
class scaned_networks:
    active: bool
    ssid: str
    signal: int
    security: str


@dataclass
class ActiveNetwork:
    connection: str = ""
    state: str | None = None
    interface: str | None = None


@dataclass
class NetworkInfo:
    ssid: str
    security: str | None = None
    type: str | None = None
    mac_address: str | None = None

    signal_strength: int | None = None
    frequency: int | None = None

    ip_address: str | None = None
    gateway: str | None = None
    subnet_mask: str | None = None
    dns: list[str] = field(default_factory=list)

    ipv6_address: str | None = None

    transmit_link_speed: int | None = None
    receive_link_speed: int | None = None

    interface: str | None = None
    state: str | None = None
    uuid: str | None = None
    dhcp_lease_time: int | None = None

    @classmethod
    def from_nmcli_dict(cls, data: dict) -> "NetworkInfo":
        ip_address = None
        subnet_mask = None

        ip4_raw = data.get("IP4.ADDRESS[1]")
        if ip4_raw:
            interface = ipaddress.IPv4Interface(ip4_raw)
            ip_address = str(interface.ip)
            subnet_mask = str(interface.network.netmask)

        ipv6_address = None
        ip6_raw = data.get("IP6.ADDRESS[1]")
        if ip6_raw:
            interface6 = ipaddress.IPv6Interface(ip6_raw)
            ipv6_address = str(interface6.ip)

        dns_servers = [value for key, value in data.items() if key.startswith("IP4.DNS") and value]

        lease_time = None
        for key, value in data.items():
            if key.startswith("DHCP4.OPTION") and value:
                if value.startswith("dhcp_lease_time"):
                    lease_time = int(value.split("=")[1].strip())
                    break

        return cls(
            ssid=data.get("802-11-wireless.ssid") or data.get("GENERAL.NAME") or "",
            security=data.get("802-11-wireless-security.key-mgmt"),
            type=data.get("connection.type"),
            mac_address=data.get("802-11-wireless.seen-bssids"),
            ip_address=ip_address,
            gateway=data.get("IP4.GATEWAY"),
            subnet_mask=subnet_mask,
            dns=dns_servers,
            ipv6_address=ipv6_address,
            interface=data.get("GENERAL.DEVICES"),
            state=data.get("GENERAL.STATE"),
            uuid=data.get("GENERAL.UUID"),
            dhcp_lease_time=lease_time,
        )
