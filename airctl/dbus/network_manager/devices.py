from dbus_next.errors import DBusError

from ..constants import (
    ACCESS_POINT_INTERFACE,
    ACTIVE_CONNECTION_INTERFACE,
    DEVICE_INTERFACE,
    DEVICE_TYPE_WIFI,
    NM_SERVICE,
    WIRELESS_INTERFACE,
)
from .base import NMBase
from .parsing import _decode_ssid, _get


class DeviceMixin(NMBase):
    async def _wifi_devices(self) -> list[tuple[str, dict]]:
        nm = await self._nm()
        devices = []

        for path in await nm.call_get_devices():
            properties = await self._all(path, DEVICE_INTERFACE)
            if properties.get("DeviceType") == DEVICE_TYPE_WIFI:
                devices.append((path, properties))

        return devices

    async def _wifi_device(self, ifname: str | None = None):
        devices = await self._wifi_devices()

        if ifname:
            for path, properties in devices:
                if properties.get("Interface") == ifname:
                    return path, properties
            return None

        return devices[0] if devices else None

    async def _find_active_wifi(self):
        nm = await self._nm()

        for path in await nm.get_active_connections():
            properties = await self._all(path, ACTIVE_CONNECTION_INTERFACE)
            if properties.get("Type") == "802-11-wireless":
                return path, properties

        return None

    async def _active_ssid(self, properties: dict) -> str:
        for device_path in properties.get("Devices") or []:
            try:
                wireless = await self._all(device_path, WIRELESS_INTERFACE)
            except DBusError:
                continue

            ap_path = wireless.get("ActiveAccessPoint")

            if not ap_path or ap_path == "/":
                continue

            try:
                access_point = await self._all(ap_path, ACCESS_POINT_INTERFACE)
            except DBusError:
                continue

            ssid = _decode_ssid(access_point.get("Ssid"))

            if ssid:
                return ssid

        return _get(properties, "Id") or ""

    async def _find_access_point(self, ssid: str):
        best = None
        best_signal = -1

        for device_path, _ in await self._wifi_devices():
            wireless = await self.dbus.interface(NM_SERVICE, device_path, WIRELESS_INTERFACE)

            for ap_path in await wireless.call_get_access_points():
                access_point = await self._all(ap_path, ACCESS_POINT_INTERFACE)

                if _decode_ssid(access_point.get("Ssid")) != ssid:
                    continue

                signal = int(access_point.get("Strength") or 0)

                if signal > best_signal:
                    best = access_point
                    best_signal = signal

        return best
