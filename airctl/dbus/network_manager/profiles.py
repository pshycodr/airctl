from dbus_next.errors import DBusError

from ..constants import (
    CONNECTION_INTERFACE,
    NM_SERVICE,
    NM_SETTINGS_PATH,
    SETTINGS_INTERFACE,
)
from .base import NMBase
from .parsing import _connection_matches


class ProfileMixin(NMBase):
    async def _find_connection(self, ssid: str):
        settings = await self.dbus.interface(NM_SERVICE, NM_SETTINGS_PATH, SETTINGS_INTERFACE)

        for path in await settings.call_list_connections():
            connection = await self.dbus.interface(NM_SERVICE, path, CONNECTION_INTERFACE)

            try:
                data = await connection.call_get_settings()
            except DBusError:
                continue

            if _connection_matches(data, ssid):
                return path, data

        return None, None

    async def _connection_exists(self, path: str) -> bool:
        settings = await self.dbus.interface(NM_SERVICE, NM_SETTINGS_PATH, SETTINGS_INTERFACE)

        return path in await settings.call_list_connections()

    async def check_known_network(self, ssid: str) -> bool:
        path, _ = await self._find_connection(ssid)

        return path is not None
