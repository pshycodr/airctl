import gi
from gi.repository import Gtk

from core.network_manager import NetworkManager
from core.ui.dialog_box import DialogBox

gi.require_version("Gtk", "4.0")


class NetworkListWidget(Gtk.ListBox):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.set_selection_mode(Gtk.SelectionMode.NONE)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header.set_spacing(12)
        header.add_css_class("network-header")

        label = Gtk.Label(label="WiFi Networks", xalign=0)
        label.set_hexpand(True)

        refresh = Gtk.Button()
        refresh.set_icon_name("view-refresh-symbolic")
        refresh.add_css_class("flat")
        refresh.add_css_class("circular")
        refresh.set_tooltip_text("Refresh networks")
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
            row.set_activatable(False)
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

    def get_signal_class(self, signal):
        if signal >= 75:
            return "signal-excellent"
        elif signal >= 50:
            return "signal-good"
        elif signal >= 25:
            return "signal-fair"
        else:
            return "signal-weak"

    def network_box(self, network):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        ssid_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        ssid_box.set_hexpand(True)

        ssid_label = Gtk.Label(label=network["ssid"], xalign=0)
        ssid_label.set_ellipsize(3)
        ssid_label.set_max_width_chars(30)

        ssid_box.append(ssid_label)

        if network["active"]:
            status_label = Gtk.Label(label="Connected", xalign=0)
            status_label.set_opacity(0.7)
            status_label.set_css_classes(["caption", "dim-label"])
            ssid_box.append(status_label)

        signal_label = Gtk.Label(label=f"{network['signal']}%")
        signal_label.set_width_chars(4)
        signal_label.add_css_class(self.get_signal_class(network["signal"]))

        signal_icon = Gtk.Image()
        if network["signal"] >= 75:
            signal_icon.set_from_icon_name("network-wireless-signal-excellent-symbolic")
        elif network["signal"] >= 50:
            signal_icon.set_from_icon_name("network-wireless-signal-good-symbolic")
        elif network["signal"] >= 25:
            signal_icon.set_from_icon_name("network-wireless-signal-ok-symbolic")
        else:
            signal_icon.set_from_icon_name("network-wireless-signal-weak-symbolic")
        signal_icon.add_css_class(self.get_signal_class(network["signal"]))

        security_icon = Gtk.Image()
        if network["security"]:
            security_icon.set_from_icon_name("network-wireless-encrypted-symbolic")
            security_icon.set_tooltip_text("Secured network")
        else:
            security_icon.set_from_icon_name("network-wireless-no-route-symbolic")
            security_icon.set_tooltip_text("Open network")
            security_icon.set_opacity(0.5)

        info_button = Gtk.Button()
        info_button.set_icon_name("go-next-symbolic")
        info_button.add_css_class("flat")
        info_button.add_css_class("circular")
        info_button.add_css_class("network-info-button")
        info_button.set_tooltip_text("Connect")
        info_button.connect(
            "clicked",
            lambda *_: self.on_network_selected(network),
        )

        box.set_css_classes(["unknown-network"])

        if NetworkManager._check_known_network(network["ssid"]):
            box.set_css_classes(["known-network"])
        if network["active"]:
            box.set_css_classes(["connected-network"])

        box.append(ssid_box)
        box.append(signal_icon)
        box.append(signal_label)
        box.append(security_icon)

        if network["active"]:
            box.append(info_button)

        return box
