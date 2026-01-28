import gi
from gi.repository import Gtk
from network_manager import NetworkManager

gi.require_version("Gtk", "4.0")


class NetworkListWidget(Gtk.ListBox):
    def __init__(self):
        super().__init__()

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        label = Gtk.Label(label="Wifi Networks", xalign=0)
        refresh_label = Gtk.Label(label="Refresh", xalign=1)

        header.append(label)
        header.append(refresh_label)

        self.append(header)

    def create_network_list(self):
        networks = NetworkManager.scan_network()

        for network in networks:
            network_row = self.nework_box(network)
            self.append(network_row)

    def refresh_handler():
        pass

    def nework_box(self, network):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_margin_top(5)
        box.set_margin_bottom(5)
        box.set_margin_start(10)
        box.set_margin_end(10)

        ssid_label = Gtk.Label(label=network["ssid"], xalign=0)
        ssid_label.set_hexpand(True)

        signal_label = Gtk.Label(label=f"{network['signal']}%")

        security_icon = Gtk.Image.new_from_icon_name(
            "network-wireless-encrypted-symbolic"
            if network["security"]
            else "network-wireless-symbolic"
        )

        box.append(ssid_label)
        box.append(signal_label)
        box.append(security_icon)

        return box
