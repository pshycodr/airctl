import gi
from gi.repository import Gtk

from core.network_manager import NetworkManager
from core.ui.dialog_box import DialogBox

gi.require_version("Gtk", "4.0")


class NetworkListWidget(Gtk.ListBox):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        label = Gtk.Label(label="Wifi Networks", xalign=0)
        refresh = Gtk.Button()
        refresh.set_icon_name("view-refresh-symbolic")
        refresh.add_css_class("flat")
        refresh.connect("clicked", self.refresh_networks)

        header.append(label)
        header.append(refresh)

        self.append(header)

        self.create_network_list()

    def clear_networks(self):
        rows = list(self)
        for row in rows[1:]:
            self.remove(row)

    def refresh_networks(self, *_):
        self.clear_networks()
        self.create_network_list()

    def create_network_list(self):
        networks = NetworkManager.scan_networks()

        for network in networks:
            row = Gtk.ListBoxRow()
            box = self.network_box(network)
            row.set_child(box)

            click = Gtk.GestureClick()
            click.connect(
                "released",
                lambda _, __, ___, ____, n=network: self.on_network_selected(n),
            )
            box.add_controller(click)

            self.append(row)

    def on_network_selected(self, network):
        if network["active"]:
            NetworkManager.disconnect_network()
            self.refresh_networks()
            return

        if network["security"]:
            DialogBox(
                self.parent,
                network["ssid"],
                lambda password: password
                and NetworkManager.connect_network(network["ssid"], password),
            ).password()
        else:
            NetworkManager.connect_network(network["ssid"], None)

    def network_box(self, network):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_margin_top(5)
        box.set_margin_bottom(5)
        box.set_margin_start(10)
        box.set_margin_end(10)

        ssid_label = Gtk.Label(label=network["ssid"], xalign=0)
        ssid_label.set_hexpand(True)

        if network["active"]:
            ssid_label.add_css_class("suggested-action")

        signal_label = Gtk.Label(label=f"{network['signal']}%")

        security_icon = Gtk.Image.new_from_icon_name(
            "network-wireless-encrypted-symbolic"
            if network["security"]
            else "network-wireless-symbolic"
        )

        info_button = Gtk.Button()
        info_button.set_icon_name("help-about-symbolic")
        info_button.add_css_class("flat")
        info_button.connect(
            "clicked",
            lambda *_: self.on_network_selected(network),
        )

        box.append(ssid_label)
        box.append(signal_label)
        box.append(security_icon)
        box.append(info_button)

        return box
