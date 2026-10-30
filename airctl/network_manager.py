from airctl.dbus.network_manager import NetworkManagerDBus
from airctl.dbus.network_manager.parsing import _band
from airctl.dbus.sync import DBusRunner
from airctl.models import ActiveNetwork

_fast_runner = DBusRunner()
_fast = NetworkManagerDBus()

_scan_runner = DBusRunner()
_scan = NetworkManagerDBus()

_action_runner = DBusRunner()
_action = NetworkManagerDBus()

for _runner, _manager in (
    (_fast_runner, _fast),
    (_scan_runner, _scan),
    (_action_runner, _action),
):
    _runner.add_shutdown_hook(_manager.close)


class NetworkManager:
    @staticmethod
    def is_networkmanager_running():
        try:
            return _fast_runner.call(_fast.is_running())
        except Exception:
            return False

    @staticmethod
    def wifi_status():
        try:
            return _fast_runner.call(_fast.wifi_status())
        except Exception:
            return False

    @staticmethod
    def toggle_wifi():
        try:
            return _fast_runner.call(_fast.toggle_wifi())
        except Exception:
            return False

    @staticmethod
    def scan_networks() -> list[dict]:
        try:
            return _scan_runner.call(_scan.scan_networks())
        except Exception:
            return []

    @staticmethod
    def connect_network(ssid: str, password: str | None = None, ifname: str | None = None):
        try:
            return _action_runner.call(_action.connect_network(ssid, password, ifname))
        except Exception as error:
            return {
                "success": False,
                "message": f"Error connecting to {ssid}: {error}",
            }

    @staticmethod
    def disconnect_network():
        try:
            return _fast_runner.call(_fast.disconnect_network())
        except Exception as error:
            return {"success": False, "message": f"Error disconnecting: {error}"}

    @staticmethod
    def force_rescan(delay: float = 2.0):
        try:
            return _action_runner.call(_action.force_rescan(delay))
        except Exception as error:
            return {"success": False, "message": f"Error rescanning: {error}"}

    @staticmethod
    def _check_known_network(ssid: str) -> bool:
        try:
            return _fast_runner.call(_fast.check_known_network(ssid))
        except Exception:
            return False

    @staticmethod
    def get_network_info(ssid: str):
        try:
            return _fast_runner.call(_fast.get_network_info(ssid))
        except Exception:
            return None

    @staticmethod
    def get_active_network_info() -> ActiveNetwork:
        try:
            return _fast_runner.call(_fast.get_active_network_info())
        except Exception:
            return ActiveNetwork()

    @staticmethod
    def forget_network(ssid: str):
        try:
            return _fast_runner.call(_fast.forget_network(ssid))
        except Exception as error:
            return {
                "success": False,
                "message": f"Error while deleting the network: {error}",
            }

    @staticmethod
    def _get_frequency(freq) -> str:
        return _band(freq)
