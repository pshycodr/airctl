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
        try:
            if password:
                nmcli.device.wifi_connect(ssid, password, ifname)
            else:
                cmd = ["device", "wifi", "connect", ssid]
                nmcli._syscmd.nmcli(cmd)

            network = nmcli.device()[0]
            if network.connection == ssid and network.state == "connected":
                return {"success": True, "message": f"Successfully connected to {ssid}"}

            return {"success": False, "message": f"Failed to connect to {ssid}"}
        except Exception as err:
            return {
                "success": False,
                "message": f"Error connecting to {ssid}: {str(err)}",
            }

    @staticmethod
    def disconnect_network():
        try:
            device = nmcli.device.show()[0].device
            nmcli.device.disconnect(device)
            return {"success": True, "message": "Successfully disconnected"}
        except Exception as err:
            return {"success": False, "message": f"Error disconnecting: {str(err)}"}

    @staticmethod
    def force_rescan(delay: float = 2.0):
        try:
            nmcli.device.wifi_rescan()
            time.sleep(delay)
            return {"success": True, "networks": nmcli.device.wifi()}
        except Exception as err:
            return {"success": False, "message": f"Error rescanning: {str(err)}"}

    @staticmethod
    def _check_known_network(ssid: str) -> bool:
        try:
            nmcli.connection.show(name=ssid)
            return True
        except Exception:
            return False

    # def auto_connect():
    #     pass

    @staticmethod
    def get_network_info():
        pass

    @staticmethod
    def forget_network(ssid: str):
        try:
            if not NetworkManager._check_known_network(ssid):
                return {
                    "success": False,
                    "message": f"Network {ssid} is not a known network",
                }

            nmcli.connection.delete(name=ssid)

            if NetworkManager._check_known_network(ssid):
                return {
                    "success": False,
                    "message": f"Error forgetting the network {ssid}",
                }

            return {"success": True, "message": f"Successfully removed network {ssid}"}
        except Exception as err:
            return {
                "success": False,
                "message": f"Error while deleting the network: {str(err)}",
            }
