import asyncio
from uuid import uuid4

from dbus_next.errors import DBusError
from dbus_next.signature import Variant

from ..constants import (
    ACTIVE_CONNECTION_INTERFACE,
    ACTIVE_CONNECTION_STATE_ACTIVATED,
    ACTIVE_CONNECTION_STATE_DEACTIVATED,
    CONNECTION_INTERFACE,
    NM_SERVICE,
)
from .devices import DeviceMixin
from .parsing import _error_text, _get
from .profiles import ProfileMixin


class ConnectionMixin(DeviceMixin, ProfileMixin):
    def _build_settings(self, ssid: str, password: str | None = None) -> dict:
        settings = {
            "connection": {
                "id": Variant("s", ssid),
                "type": Variant("s", "802-11-wireless"),
                "uuid": Variant("s", str(uuid4())),
                "autoconnect": Variant("b", True),
            },
            "802-11-wireless": {
                "ssid": Variant("ay", ssid.encode("utf-8")),
                "mode": Variant("s", "infrastructure"),
            },
        }

        if password:
            settings["802-11-wireless"]["security"] = Variant("s", "802-11-wireless-security")
            settings["802-11-wireless-security"] = {
                "key-mgmt": Variant("s", "wpa-psk"),
                "psk": Variant("s", password),
            }

        return settings

    async def _set_password(self, path: str, settings: dict, password: str):
        connection = await self.dbus.interface(NM_SERVICE, path, CONNECTION_INTERFACE)

        wireless = settings.setdefault("802-11-wireless", {})
        wireless["security"] = Variant("s", "802-11-wireless-security")

        security = settings.setdefault("802-11-wireless-security", {})
        key_mgmt = _get(security, "key-mgmt")

        if not key_mgmt or key_mgmt == "none":
            key_mgmt = "wpa-psk"

        security["key-mgmt"] = Variant("s", key_mgmt)
        security["psk"] = Variant("s", password)

        await connection.call_update2(settings, 0)

    async def _wait_for_activation(self, active_path: str, timeout: float = 30.0) -> bool:
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout

        while loop.time() < deadline:
            try:
                state = await self._prop(active_path, ACTIVE_CONNECTION_INTERFACE, "State")
            except DBusError:
                return False

            if state == ACTIVE_CONNECTION_STATE_ACTIVATED:
                return True

            if state == ACTIVE_CONNECTION_STATE_DEACTIVATED:
                return False

            await asyncio.sleep(0.25)

        return False

    async def connect_network(self, ssid: str, password: str | None = None, ifname=None) -> dict:
        await self.start()

        device = await self._wifi_device(ifname)

        if device is None:
            message = f"Wi-Fi interface {ifname} not found" if ifname else "No Wi-Fi device found"
            return {"success": False, "message": message}

        device_path, _ = device

        try:
            connection_path, settings = await self._find_connection(ssid)
            nm = await self._nm()

            if connection_path is not None:
                if password:
                    await self._set_password(connection_path, settings, password)
                active_path = await nm.call_activate_connection(connection_path, device_path, "/")
            else:
                _, active_path = await nm.call_add_and_activate_connection(
                    self._build_settings(ssid, password), device_path, "/"
                )

            if await self._wait_for_activation(active_path):
                return {"success": True, "message": f"Successfully connected to {ssid}"}

            return {"success": False, "message": f"Failed to connect to {ssid}"}
        except Exception as error:
            return {
                "success": False,
                "message": f"Error connecting to {ssid}: {_error_text(error)}",
            }

    async def disconnect_network(self) -> dict:
        await self.start()

        active = await self._find_active_wifi()

        if active is None:
            return {"success": False, "message": "No active Wi-Fi connection to disconnect"}

        active_path, _ = active

        try:
            nm = await self._nm()
            await nm.call_deactivate_connection(active_path)
            return {"success": True, "message": "Successfully disconnected"}
        except Exception as error:
            return {"success": False, "message": f"Error disconnecting: {_error_text(error)}"}

    async def forget_network(self, ssid: str) -> dict:
        await self.start()

        connection_path, _ = await self._find_connection(ssid)

        if connection_path is None:
            return {
                "success": False,
                "message": f"Network {ssid} is not a known network",
            }

        try:
            connection = await self.dbus.interface(
                NM_SERVICE, connection_path, CONNECTION_INTERFACE
            )
            await connection.call_delete()
        except Exception as error:
            return {
                "success": False,
                "message": f"Error while deleting the network: {_error_text(error)}",
            }

        if await self._connection_exists(connection_path):
            return {
                "success": False,
                "message": f"Error forgetting the network {ssid}",
            }

        return {"success": True, "message": f"Successfully removed network {ssid}"}
