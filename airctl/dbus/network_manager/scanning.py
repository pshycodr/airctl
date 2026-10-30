import asyncio

from dbus_next.errors import DBusError

from ..constants import ACCESS_POINT_INTERFACE, NM_SERVICE, WIRELESS_INTERFACE
from .devices import DeviceMixin
from .parsing import _band, _decode_ssid, _error_text, _security_from_ap


class ScanMixin(DeviceMixin):
    async def scan_networks(self, request_scan: bool = True, timeout: float = 10.0) -> list[dict]:
        await self.start()

        networks: dict[str, dict] = {}

        for path, _ in await self._wifi_devices():
            wireless = await self.dbus.interface(NM_SERVICE, path, WIRELESS_INTERFACE)

            if request_scan:
                try:
                    previous = await wireless.get_last_scan()
                except DBusError:
                    previous = None

                try:
                    await wireless.call_request_scan({})
                except DBusError:
                    pass
                else:
                    await self._wait_for_scan(wireless, previous, timeout)

            properties = await self._all(path, WIRELESS_INTERFACE)
            active_ap = properties.get("ActiveAccessPoint")

            for ap_path in await wireless.call_get_access_points():
                ap = await self._all(ap_path, ACCESS_POINT_INTERFACE)
                ssid = _decode_ssid(ap.get("Ssid"))

                if not ssid:
                    continue

                signal = int(ap.get("Strength") or 0)
                security = _security_from_ap(
                    ap.get("Flags"),
                    ap.get("WpaFlags"),
                    ap.get("RsnFlags"),
                )
                band = _band(ap.get("Frequency"))

                entry = networks.get(ssid)

                if entry is None:
                    entry = {
                        "active": False,
                        "ssid": ssid,
                        "signal": signal,
                        "security": security,
                        "freq": band,
                    }
                    networks[ssid] = entry
                elif signal > entry["signal"] and not entry["active"]:
                    entry["signal"] = signal
                    entry["security"] = security
                    entry["freq"] = band

                if ap_path == active_ap:
                    entry["active"] = True
                    entry["signal"] = signal
                    entry["security"] = security
                    entry["freq"] = band

        return sorted(networks.values(), key=lambda network: network["signal"], reverse=True)

    async def _wait_for_scan(self, wireless, previous, timeout: float):
        loop = asyncio.get_running_loop()
        deadline = loop.time() + max(timeout, 0.5)

        while loop.time() < deadline:
            await asyncio.sleep(0.2)

            try:
                current = await wireless.get_last_scan()
            except DBusError:
                return

            if current != previous:
                await asyncio.sleep(0.2)
                return

    async def force_rescan(self, delay: float = 2.0) -> dict:
        await self.start()

        device = await self._wifi_device()

        if device is None:
            return {"success": False, "message": "No Wi-Fi device found"}

        path, _ = device
        wireless = await self.dbus.interface(NM_SERVICE, path, WIRELESS_INTERFACE)

        try:
            previous = await wireless.get_last_scan()
        except DBusError:
            previous = None

        try:
            await wireless.call_request_scan({})
        except DBusError as error:
            return {"success": False, "message": f"Error rescanning: {_error_text(error)}"}

        await self._wait_for_scan(wireless, previous, max(delay, 10.0))

        return {
            "success": True,
            "networks": await self.scan_networks(request_scan=False),
        }
