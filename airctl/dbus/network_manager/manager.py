from dbus_next.errors import DBusError

from airctl.models import ActiveNetwork, NetworkInfo

from ..constants import (
    ACCESS_POINT_INTERFACE,
    DEVICE_INTERFACE,
    DEVICE_STATE_NAMES,
    DEVICE_TYPE_ETHERNET,
    DHCP4_CONFIG_INTERFACE,
    IP4_CONFIG_INTERFACE,
    IP6_CONFIG_INTERFACE,
    NM_INTERFACE,
    NM_PATH,
    WIRED_INTERFACE,
)
from .connections import ConnectionMixin
from .parsing import (
    _dns_servers,
    _first_ipv4,
    _first_ipv6,
    _get,
    _netmask,
)
from .scanning import ScanMixin


class NetworkManagerDBus(ScanMixin, ConnectionMixin):
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
