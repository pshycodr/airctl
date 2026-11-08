from ..client import DBusClient
from ..constants import NM_INTERFACE, NM_PATH, NM_SERVICE
from .advanced import parse_nm_version


class NMBase:
    def __init__(self):
        self.dbus = DBusClient()

    async def start(self):
        await self.dbus.connect()

    async def close(self):
        await self.dbus.close()

    async def _nm(self):
        return await self.dbus.interface(NM_SERVICE, NM_PATH, NM_INTERFACE)

    async def _all(self, path: str, interface: str) -> dict:
        return await self.dbus.get_all_properties(NM_SERVICE, path, interface)

    async def _prop(self, path: str, interface: str, name: str):
        return await self.dbus.get_property(NM_SERVICE, path, interface, name)

    async def version(self) -> tuple[int, ...]:
        try:
            value = await self._prop(NM_PATH, NM_INTERFACE, "Version")
        except Exception:
            return (0,)

        return parse_nm_version(value)
