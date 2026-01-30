import threading

import gi
from gi.repository import GLib, Gtk

from core.network_manager import NetworkManager
from core.ui.dialog_box import DialogBox
from core.ui.network_info import NetworkInfoWindow

gi.require_version("Gtk", "4.0")


class NetworkListWidget(Gtk.ListBox):
    def __init__(self, parent, widget_stack):
        super().__init__()
        self.parent = parent
        self.widget_stack = widget_stack
        self.set_selection_mode(Gtk.SelectionMode.NONE)

        self.wifi_enabled = NetworkManager.wifi_status()
        self.connecting_ssid = None
        self.refresh_timeout_id = None

        self._create_header()

        if self.wifi_enabled:
            GLib.idle_add(self._scan_with_spinner)
            self._start_auto_refresh()

    def _create_header(self):
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header.add_css_class("network-header")

        title = Gtk.Label(label="WiFi Networks", xalign=0)
        title.set_hexpand(True)

        self.spinner = Gtk.Spinner()
        self.spinner.set_visible(False)

        self.refresh_button = Gtk.Button()
        self.refresh_button.set_icon_name("view-refresh-symbolic")
        self.refresh_button.add_css_class("flat")
        self.refresh_button.add_css_class("circular")
        self.refresh_button.set_tooltip_text("Refresh networks")
        self.refresh_button.connect("clicked", lambda _: self._scan_with_spinner())

        header.append(title)
        header.append(self.spinner)
        header.append(self.refresh_button)

        self.append(header)

    def on_wifi_enabled(self):
        self.wifi_enabled = True
        self._clear_networks()
        GLib.idle_add(self._scan_with_spinner)
        self._start_auto_refresh()

    def on_wifi_disabled(self):
        self.wifi_enabled = False
        self._clear_networks()
        self._stop_auto_refresh()
        self.connecting_ssid = None

    def _start_auto_refresh(self):
        if self.refresh_timeout_id is None:
            self.refresh_timeout_id = GLib.timeout_add(
                5000, self._auto_refresh_callback
            )

    def _stop_auto_refresh(self):
        if self.refresh_timeout_id:
            GLib.source_remove(self.refresh_timeout_id)
            self.refresh_timeout_id = None

    def _auto_refresh_callback(self):
        if self.wifi_enabled:
            self._scan_with_spinner()
            return True
        return False

    def _scan_with_spinner(self):
        self._toggle_loading(True)
        GLib.timeout_add(300, self._complete_scan)

    def _complete_scan(self):
        self._clear_networks()
        self._populate_networks()
        self._toggle_loading(False)

    def _toggle_loading(self, loading):
        self.spinner.set_visible(loading)
        if loading:
            self.spinner.start()
        else:
            self.spinner.stop()
        self.refresh_button.set_sensitive(not loading)

    def _clear_networks(self):
        for row in list(self)[1:]:
            self.remove(row)

    def _populate_networks(self):
        if not self.wifi_enabled:
            return

        for network in NetworkManager.scan_networks():
            row = Gtk.ListBoxRow()
            row.set_activatable(False)
            row.set_child(self._create_network_row(network))

            click = Gtk.GestureClick()
            click.connect(
                "released", lambda *args, n=network: self._on_network_click(n)
            )
            row.get_child().add_controller(click)

            self.append(row)

    def _create_network_row(self, network):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        # SSID and status
        ssid_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        ssid_box.set_hexpand(True)

        ssid_label = Gtk.Label(label=network["ssid"], xalign=0)
        ssid_label.set_ellipsize(3)
        ssid_label.set_max_width_chars(30)
        ssid_box.append(ssid_label)

        # Status label
        if network["active"]:
            status = Gtk.Label(label="Connected", xalign=0)
            status.set_opacity(0.7)
            status.set_css_classes(["caption", "dim-label"])
            ssid_box.append(status)
        elif self.connecting_ssid == network["ssid"]:
            status = Gtk.Label(label="Connecting...", xalign=0)
            status.set_opacity(0.7)
            status.set_css_classes(["caption", "dim-label"])
            ssid_box.append(status)

        box.append(ssid_box)

        # Signal icon and strength
        signal_icon = Gtk.Image()
        signal_strength = network["signal"]
        signal_class = self._get_signal_class(signal_strength)

        if signal_strength >= 75:
            signal_icon.set_from_icon_name("network-wireless-signal-excellent-symbolic")
        elif signal_strength >= 50:
            signal_icon.set_from_icon_name("network-wireless-signal-good-symbolic")
        elif signal_strength >= 25:
            signal_icon.set_from_icon_name("network-wireless-signal-ok-symbolic")
        else:
            signal_icon.set_from_icon_name("network-wireless-signal-weak-symbolic")
        signal_icon.add_css_class(signal_class)

        signal_label = Gtk.Label(label=f"{signal_strength}%")
        signal_label.set_width_chars(4)
        signal_label.add_css_class(signal_class)

        box.append(signal_icon)
        box.append(signal_label)

        # Security icon
        security_icon = Gtk.Image()
        if network["security"]:
            security_icon.set_from_icon_name("network-wireless-encrypted-symbolic")
            security_icon.set_tooltip_text("Secured network")
        else:
            security_icon.set_from_icon_name("network-wireless-no-route-symbolic")
            security_icon.set_tooltip_text("Open network")
            security_icon.set_opacity(0.5)
        box.append(security_icon)

        # Connecting spinner or info button
        if self.connecting_ssid == network["ssid"]:
            spinner = Gtk.Spinner()
            spinner.start()
            spinner.set_tooltip_text("Connecting...")
            box.append(spinner)
        elif network["active"]:
            info_btn = Gtk.Button()
            info_btn.set_icon_name("go-next-symbolic")
            info_btn.add_css_class("flat")
            info_btn.add_css_class("circular")
            info_btn.add_css_class("network-info-button")
            info_btn.set_tooltip_text("Network Info")
            info_btn.connect(
                "clicked", lambda *_: self._open_network_info(network["ssid"])
            )
            box.append(info_btn)

        # Set row style
        if network["active"]:
            box.set_css_classes(["connected-network"])
        elif self.connecting_ssid == network["ssid"]:
            box.set_css_classes(["connecting-network"])
        elif NetworkManager._check_known_network(network["ssid"]):
            box.set_css_classes(["known-network"])
        else:
            box.set_css_classes(["unknown-network"])

        return box

    def _get_signal_class(self, signal):
        if signal >= 75:
            return "signal-excellent"
        elif signal >= 50:
            return "signal-good"
        elif signal >= 25:
            return "signal-fair"
        return "signal-weak"

    def _on_network_click(self, network):
        if not self.wifi_enabled:
            return

        if network["active"]:
            self._open_network_info(network["ssid"])
        elif network["security"] and NetworkManager._check_known_network(
            network["ssid"]
        ):
            self._show_connection_confirm(network["ssid"])
        elif network["security"]:
            self._show_password_dialog(network["ssid"])
        else:
            self._connect_to_network(network["ssid"])

    def _open_network_info(self, ssid):
        info_window = NetworkInfoWindow(self.parent, ssid)
        info_window.connect("close-request", lambda _: self._scan_with_spinner())
        info_window.present()

    def _show_password_dialog(self, ssid):
        def on_password(password):
            if password:
                self._connect_to_network(ssid, password)

        DialogBox(self.parent, ssid, on_password).password()

    def _show_connection_confirm(self, ssid):
        def on_confirm(confirmed):
            if confirmed:
                self._connect_to_network(ssid)

        DialogBox(self.parent, ssid, on_confirm).confirmation(
            message=f"Connect to {ssid}?"
        )

    def _connect_to_network(self, ssid, password=None):
        self.connecting_ssid = ssid
        self._scan_with_spinner()

        def connect_thread():
            result = NetworkManager.connect_network(ssid, password)
            GLib.idle_add(self._show_connection_result, ssid, result)

        threading.Thread(target=connect_thread, daemon=True).start()

    def _show_connection_result(self, ssid, result):
        self.connecting_ssid = None
        self._scan_with_spinner()

        def callback(_):
            return self._scan_with_spinner() if result["success"] else None

        if result["success"]:
            DialogBox(self.parent, ssid, callback).info(result["message"])
        else:
            DialogBox(self.parent, ssid, None).error(result["message"])
