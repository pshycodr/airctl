from dataclasses import dataclass


@dataclass
class scaned_networks:
    active: bool
    ssid: str
    signal: int
    security: str
