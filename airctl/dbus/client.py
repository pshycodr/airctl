from dbus_next.aio.message_bus import MessageBus
from dbus_next.constants import BusType
from dbus_next.signature import Variant

from .constants import PROPERTIES_INTERFACE


class DBusClient:
    def __init__(self, bus_type: BusType = BusType.SYSTEM):
        self._bus_type = bus_type
        self.bus: MessageBus | None = None
        self._objects: dict[tuple[str, str], object] = {}
        self._interfaces: dict[tuple[str, str, str], object] = {}

    async def connect(self) -> MessageBus:
        if self.bus is not None and self.bus.connected:
            return self.bus

        if self.bus is not None:
            try:
                self.bus.disconnect()
            except Exception:
                pass

            self._objects.clear()
            self._interfaces.clear()

        self.bus = await MessageBus(bus_type=self._bus_type).connect()

        return self.bus

    async def close(self):
        if self.bus is None:
            return

        if self.bus.connected:
            self.bus.disconnect()

        self.bus = None
        self._objects.clear()
        self._interfaces.clear()

    async def object(
        self,
        service: str,
        path: str,
    ):
        await self.connect()

        key = (service, path)

        if key in self._objects:
            return self._objects[key]

        introspection = await self.bus.introspect(
            service,
            path,
        )

        obj = self.bus.get_proxy_object(
            service,
            path,
            introspection,
        )

        self._objects[key] = obj

        return obj

    async def interface(
        self,
        service: str,
        path: str,
        interface: str,
    ):
        key = (service, path, interface)

        if key in self._interfaces:
            return self._interfaces[key]

        obj = await self.object(
            service,
            path,
        )

        iface = obj.get_interface(interface)

        self._interfaces[key] = iface

        return iface

    async def get_property(
        self,
        service: str,
        path: str,
        interface: str,
        property_name: str,
    ):
        props = await self.interface(
            service,
            path,
            PROPERTIES_INTERFACE,
        )

        value = await props.call_get(
            interface,
            property_name,
        )

        return value.value

    async def get_all_properties(
        self,
        service: str,
        path: str,
        interface: str,
    ) -> dict[str, object]:
        props = await self.interface(
            service,
            path,
            PROPERTIES_INTERFACE,
        )

        values = await props.call_get_all(interface)

        return {name: value.value for name, value in values.items()}

    async def set_property(
        self,
        service: str,
        path: str,
        interface: str,
        property_name: str,
        signature: str,
        value,
    ):
        props = await self.interface(
            service,
            path,
            PROPERTIES_INTERFACE,
        )

        await props.call_set(
            interface,
            property_name,
            Variant(signature, value),
        )
