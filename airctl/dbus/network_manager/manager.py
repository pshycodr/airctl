from ..constants import (
    NM_INTERFACE,
    NM_PATH,
)
from .connections import ConnectionMixin
from .info import InfoMixin
from .scanning import ScanMixin


class NetworkManagerDBus(ScanMixin, ConnectionMixin, InfoMixin):
    async def is_running(self) -> bool:
        try:
            await self.start()
            return bool(await self._prop(NM_PATH, NM_INTERFACE, "Version"))
        except Exception:
            return False

    async def wifi_status(self) -> bool:
        nm = await self._nm()

        return bool(await nm.get_wireless_enabled())

    async def toggle_wifi(self) -> bool:
        nm = await self._nm()
        enabled = bool(await nm.get_wireless_enabled())

        await nm.set_wireless_enabled(not enabled)

        return not enabled
