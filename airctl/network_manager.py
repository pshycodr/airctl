from airctl.dbus.network_manager import NetworkManagerDBus, _band
from airctl.dbus.sync import DBusRunner
from airctl.models import ActiveNetwork

_runner = DBusRunner()
_manager = NetworkManagerDBus()

_runner.add_shutdown_hook(_manager.close)


def _call(coroutine):
    return _runner.call(coroutine)


class NetworkManager:
    @staticmethod
    def is_networkmanager_running():
        try:
            return _call(_manager.is_running())
        except Exception:
            return False

    @staticmethod
    def wifi_status():
        try:
            return _call(_manager.wifi_status())
        except Exception:
            return False

    @staticmethod
    def toggle_wifi():
        try:
            return _call(_manager.toggle_wifi())
        except Exception:
            return False

    @staticmethod
    def scan_networks() -> list[dict]:
        try:
            return _call(_manager.scan_networks())
        except Exception:
            return []

    @staticmethod
    def connect_network(ssid: str, password: str | None = None, ifname: str | None = None):
        try:
            return _call(_manager.connect_network(ssid, password, ifname))
        except Exception as error:
            return {
                "success": False,
                "message": f"Error connecting to {ssid}: {error}",
            }

    @staticmethod
    def disconnect_network():
        try:
            return _call(_manager.disconnect_network())
        except Exception as error:
            return {"success": False, "message": f"Error disconnecting: {error}"}

    @staticmethod
    def force_rescan(delay: float = 2.0):
        try:
            return _call(_manager.force_rescan(delay))
        except Exception as error:
            return {"success": False, "message": f"Error rescanning: {error}"}

    @staticmethod
    def _check_known_network(ssid: str) -> bool:
        try:
            return _call(_manager.check_known_network(ssid))
        except Exception:
            return False

    @staticmethod
    def get_network_info(ssid: str):
        try:
            return _call(_manager.get_network_info(ssid))
        except Exception:
            return None

    @staticmethod
    def get_active_network_info() -> ActiveNetwork:
        try:
            return _call(_manager.get_active_network_info())
        except Exception:
            return ActiveNetwork()

    @staticmethod
    def forget_network(ssid: str):
        try:
            return _call(_manager.forget_network(ssid))
        except Exception as error:
            return {
                "success": False,
                "message": f"Error while deleting the network: {error}",
            }

    @staticmethod
    def _get_frequency(freq) -> str:
        return _band(freq)
