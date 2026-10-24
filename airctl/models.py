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
