import time
import nmcli
from airctl.models import NetworkInfo, scaned_networks

nmcli.disable_use_sudo()


class NetworkManager:
    @staticmethod
    def is_networkmanager_running():
        try:
            nmcli.radio.wifi()
            return True
        except nmcli._exception.NetworkManagerNotRunningException:
            return False
        except Exception:
            return False

    @staticmethod
    def wifi_status():
        try:
            return nmcli.radio.wifi()
        except nmcli._exception.NetworkManagerNotRunningException:
            return False
        except Exception:
            return False

    @staticmethod
    def toggle_wifi():
        try:
            if nmcli.radio.wifi():
                return nmcli.radio.wifi_off()

            return nmcli.radio.wifi_on()

        except nmcli._exception.NetworkManagerNotRunningException:
            return False
        except Exception:
            return False

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
                    "freq" : NetworkManager._get_frequency(freq=net.freq)
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
            name = nmcli.device()[0].connection
            nmcli.connection.down(name=name)
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

    @staticmethod
    def get_network_info(ssid: str):
        try:
            res = nmcli.connection.show(name=ssid)
            return NetworkInfo.from_nmcli_dict(dict(res))
        except Exception:
            return None

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
            
    @staticmethod
    def _get_frequency(freq) -> str:

        if freq is None:
            return ""

        try:
            freq = int(float(freq))
        except (ValueError, TypeError):
            return ""

        if 2400 <= freq <= 2500:
            return "2.4GHz"
        elif 4900 <= freq <= 5900:
            return "5GHz"
        elif 5925 <= freq <= 7125:
            return "6GHz"

        return ""
