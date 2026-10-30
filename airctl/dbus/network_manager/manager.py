import asyncio
from uuid import uuid4

from dbus_next.errors import DBusError
from dbus_next.signature import Variant

from airctl.models import ActiveNetwork, NetworkInfo

from ..constants import (
    ACCESS_POINT_INTERFACE,
    ACTIVE_CONNECTION_INTERFACE,
    ACTIVE_CONNECTION_STATE_ACTIVATED,
    ACTIVE_CONNECTION_STATE_DEACTIVATED,
    CONNECTION_INTERFACE,
    DEVICE_INTERFACE,
    DEVICE_STATE_NAMES,
    DEVICE_TYPE_ETHERNET,
    DHCP4_CONFIG_INTERFACE,
    IP4_CONFIG_INTERFACE,
    IP6_CONFIG_INTERFACE,
    NM_INTERFACE,
    NM_PATH,
    NM_SERVICE,
    NM_SETTINGS_PATH,
    SETTINGS_INTERFACE,
    WIRED_INTERFACE,
    WIRELESS_INTERFACE,
)
from .devices import DeviceMixin
from .parsing import (
    _band,
    _connection_matches,
    _decode_ssid,
    _dns_servers,
    _error_text,
    _first_ipv4,
    _first_ipv6,
    _get,
    _netmask,
    _security_from_ap,
)


class NetworkManagerDBus(DeviceMixin):
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

    async def get_active_network_info(self) -> ActiveNetwork:
        await self.start()

        active = await self._find_active_wifi()

        if active is None:
            return ActiveNetwork()

        _, properties = active
        ssid = await self._active_ssid(properties)
        interface = None
        state = None

        for device_path in properties.get("Devices") or []:
            try:
                device = await self._all(device_path, DEVICE_INTERFACE)
            except DBusError:
                continue

            interface = device.get("Interface") or interface
            state = DEVICE_STATE_NAMES.get(device.get("State"), state)

        return ActiveNetwork(
            connection=ssid or _get(properties, "Id") or "",
            state=state,
            interface=interface,
        )

    async def _fill_connection_details(self, info: NetworkInfo, device: dict):
        ip4_path = device.get("Ip4Config")

        if ip4_path and ip4_path != "/":
            ip4 = await self._all(ip4_path, IP4_CONFIG_INTERFACE)
            address, prefix = _first_ipv4(ip4)

            if address:
                info.ip_address = address
                info.subnet_mask = _netmask(prefix)

            info.gateway = ip4.get("Gateway") or info.gateway
            info.dns = _dns_servers(ip4)

        ip6_path = device.get("Ip6Config")

        if ip6_path and ip6_path != "/":
            ip6 = await self._all(ip6_path, IP6_CONFIG_INTERFACE)
            info.ipv6_address = _first_ipv6(ip6) or info.ipv6_address

        dhcp_path = device.get("Dhcp4Config")

        if dhcp_path and dhcp_path != "/":
            dhcp = await self._all(dhcp_path, DHCP4_CONFIG_INTERFACE)
            lease = _get(dhcp.get("Options") or {}, "dhcp_lease_time")

            if lease is not None:
                try:
                    info.dhcp_lease_time = int(lease)
                except (TypeError, ValueError):
                    pass

    async def _fill_wired_speed(self, info: NetworkInfo, device_path: str, device: dict):
        if device.get("DeviceType") != DEVICE_TYPE_ETHERNET:
            return

        try:
            wired = await self._all(device_path, WIRED_INTERFACE)
        except DBusError:
            return

        speed = wired.get("Speed")

        if speed:
            info.transmit_link_speed = int(speed)
            info.receive_link_speed = int(speed)

    async def get_network_info(self, ssid: str) -> NetworkInfo | None:
        await self.start()

        _, settings = await self._find_connection(ssid)
        active = await self._find_active_wifi()
        active_properties = active[1] if active else None

        if settings is None and active_properties is None:
            return None

        active_ssid = await self._active_ssid(active_properties) if active_properties else None
        is_active = bool(active_properties) and (
            active_ssid == ssid
            or (
                settings is not None
                and _get(settings.get("connection") or {}, "uuid")
                == _get(active_properties, "Uuid")
            )
        )

        if settings is None:
            if not is_active:
                return None
            ssid = active_ssid or ssid

        info = NetworkInfo(ssid=ssid)

        if settings:
            connection = settings.get("connection") or {}
            wireless = settings.get("802-11-wireless") or {}
            security = settings.get("802-11-wireless-security") or {}

            info.type = _get(connection, "type")
            info.uuid = _get(connection, "uuid")
            info.interface = _get(connection, "interface-name")
            info.security = _get(security, "key-mgmt")

            seen = _get(wireless, "seen-bssids") or []

            if seen:
                info.mac_address = ", ".join(str(address) for address in seen)

        access_point = None

        if is_active and active_properties:
            device_path = next(iter(active_properties.get("Devices") or []), None)

            if device_path:
                device = await self._all(device_path, DEVICE_INTERFACE)

                info.interface = device.get("Interface") or info.interface
                info.state = DEVICE_STATE_NAMES.get(device.get("State"), info.state)

                specific = _get(active_properties, "SpecificObject")

                if specific and specific != "/":
                    try:
                        access_point = await self._all(specific, ACCESS_POINT_INTERFACE)
                    except DBusError:
                        access_point = None

                await self._fill_connection_details(info, device)
                await self._fill_wired_speed(info, device_path, device)
        else:
            access_point = await self._find_access_point(ssid)
            info.state = info.state or "disconnected"

        if access_point:
            info.mac_address = access_point.get("HwAddress") or info.mac_address
            info.signal_strength = access_point.get("Strength")
            info.frequency = access_point.get("Frequency")

        return info

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
