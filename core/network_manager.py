import time

import nmcli

from core.models import scaned_networks

"""
Responsibilities:
1. Scan all available Wifi
2. Connect to the choosen wifi
3. Disconnect to the choosen
4. Handle refresh network (force rescan)
5. Get info about the connected network
"""

nmcli.disable_use_sudo()


class NetworkManager:
    @staticmethod
    def scan_networks() -> list[scaned_networks]:
        nmcli.device.wifi_rescan()
        nets = nmcli.device.wifi()

        networks = []
        for net in nets:
            if not net.ssid:
                continue

            networks.append(
                {
                    "active": net.in_use,
                    "ssid": net.ssid,
                    "signal": int(net.signal),
                    "security": net.security,
                }
            )

        return networks

    @staticmethod
    def connect_network(
        ssid: str, password: str | None = None, ifname: str | None = None
    ):
        if password:
            nmcli.device.wifi_connect(ssid, password, ifname)
        else:
            nmcli.device.wifi_connect(ssid)

    @staticmethod
    def disconnect_network():
        device = nmcli.device.show()[0].device
        nmcli.device.disconnect(device)

    @staticmethod
    def force_rescan(delay: float = 2.0):
        nmcli.device.wifi_rescan()
        time.sleep(delay)
        return nmcli.device.wifi()

    def _check_known_network(ssid: str) -> bool:
        try:
            nmcli.connection.show(name=ssid)
            return True
        except Exception:
            return False

    def auto_connect():
        pass

    def get_network_info():
        pass

    def forget_network(ssid: str):
        try:
            if not NetworkManager._check_known_network(ssid):
                return
            nmcli.connection.delete(name=ssid)

            if NetworkManager._check_known_network(ssid):
                return f"Error forgetting the network {ssid}"

            return f"Successfully removed network {ssid}"
        except Exception as err:
            return f"Error while deleting the network: {err}"
