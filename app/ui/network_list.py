import threading

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk

from network_manager import NetworkManager
from ui.dialog_box import DialogBox
from ui.network_info import NetworkInfoWindow



class NetworkListWidget(Gtk.Box):
    def __init__(self, parent, widget_stack):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.parent = parent
        self.widget_stack = widget_stack
        self.set_spacing(0)

        self.wifi_enabled = NetworkManager.wifi_status()
        self.connecting_ssid = None
        self.refresh_timeout_id = None
        self.active_network = None

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content_box.set_spacing(16)
        content_box.set_margin_top(16)
        content_box.set_margin_bottom(16)
        content_box.set_margin_start(16)
        content_box.set_margin_end(16)

        self.connected_card_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.connected_card_box.set_spacing(0)
        content_box.append(self.connected_card_box)

        networks_header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        networks_header_box.set_spacing(12)

        networks_label = Gtk.Label(label="Networks")
        networks_label.set_halign(Gtk.Align.START)
        networks_label.set_hexpand(True)
        networks_label.add_css_class("networks-title")

        self.spinner = Gtk.Spinner()
        self.spinner.set_visible(False)

        self.refresh_button = Gtk.Button()
        self.refresh_button.set_icon_name("view-refresh-symbolic")
        self.refresh_button.add_css_class("flat")
        self.refresh_button.add_css_class("circular")
        self.refresh_button.set_tooltip_text("Refresh networks")
        self.refresh_button.connect("clicked", lambda _: self._scan_with_spinner())

        networks_header_box.append(networks_label)
        networks_header_box.append(self.spinner)
        networks_header_box.append(self.refresh_button)

        content_box.append(networks_header_box)

        self.networks_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.networks_list_box.set_spacing(8)
        content_box.append(self.networks_list_box)

        scrolled.set_child(content_box)
        self.append(scrolled)

        if self.wifi_enabled:
            GLib.idle_add(self._scan_with_spinner)
            self._start_auto_refresh()

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
        self.active_network = None

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
        while True:
            child = self.connected_card_box.get_first_child()
            if child is None:
                break
            self.connected_card_box.remove(child)

        while True:
            child = self.networks_list_box.get_first_child()
            if child is None:
                break
            self.networks_list_box.remove(child)

    def _populate_networks(self):
        if not self.wifi_enabled:
            return

        networks = NetworkManager.scan_networks()
        self.active_network = None

        for network in networks:
            if network["active"]:
                self.active_network = network
                self.connected_card_box.append(self._create_connected_card(network))
            else:
                self.networks_list_box.append(self._create_network_item(network))

    def _get_signal_class(self, signal):
        if signal >= 75:
            return "signal-excellent"
        elif signal >= 50:
            return "signal-good"
        elif signal >= 25:
            return "signal-fair"
        return "signal-weak"

    def _create_connected_card(self, network):
        card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        card.set_spacing(16)
        card.add_css_class("connected-card")

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
        signal_icon.set_pixel_size(32)
        signal_icon.add_css_class(signal_class)

        card.append(signal_icon)

        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        text_box.set_spacing(4)
        text_box.set_hexpand(True)

        ssid_label = Gtk.Label(label=network["ssid"])
        ssid_label.set_halign(Gtk.Align.START)
        ssid_label.add_css_class("connected-ssid")

        status_label = Gtk.Label(label="Connected")
        status_label.set_halign(Gtk.Align.START)
        status_label.set_opacity(0.7)

        text_box.append(ssid_label)
        text_box.append(status_label)

        card.append(text_box)

        signal_percentage_label = Gtk.Label(label=f"{signal_strength}%")
        signal_percentage_label.add_css_class(signal_class)
        signal_percentage_label.set_valign(Gtk.Align.CENTER)
        signal_percentage_label.set_margin_end(8)

        card.append(signal_percentage_label)

        network_info_btn = Gtk.Button()
        network_info_btn.set_icon_name("go-next-symbolic")
        network_info_btn.add_css_class("flat")
        network_info_btn.add_css_class("circular")
        network_info_btn.set_valign(Gtk.Align.CENTER)
        network_info_btn.set_tooltip_text("Network Actions and Info")
        network_info_btn.connect("clicked", lambda _: self._open_network_info(network["ssid"]))

        card.append(network_info_btn)

        click = Gtk.GestureClick()
        click.connect("released", lambda *args: self._open_network_info(network["ssid"]))
        card.add_controller(click)

        return card

    def _create_network_item(self, network):
        item = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        item.set_spacing(12)
        item.add_css_class("network-item")

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
        signal_icon.set_pixel_size(24)
        signal_icon.add_css_class(signal_class)

        item.append(signal_icon)

        ssid_label = Gtk.Label(label=network["ssid"])
        ssid_label.set_halign(Gtk.Align.START)
        ssid_label.set_hexpand(True)
        ssid_label.set_ellipsize(3)

        item.append(ssid_label)

        signal_label = Gtk.Label(label=f"{signal_strength}%")
        signal_label.set_width_chars(4)
        signal_label.add_css_class(signal_class)

        item.append(signal_label)

        if self.connecting_ssid == network["ssid"]:
            spinner = Gtk.Spinner()
            spinner.start()
            spinner.set_tooltip_text("Connecting...")
            item.append(spinner)
        else:
            if network["security"]:
                security_icon = Gtk.Image()
                security_icon.set_from_icon_name("network-wireless-encrypted-symbolic")
                security_icon.set_pixel_size(20)
                security_icon.set_opacity(0.7)
                security_icon.set_tooltip_text("Secured network")
                item.append(security_icon)

        click = Gtk.GestureClick()
        click.connect("released", lambda *args, n=network: self._on_network_click(n))
        item.add_controller(click)

        return item

    def _on_network_click(self, network):
        if not self.wifi_enabled:
            return

        if network["active"]:
            self._open_network_info(network["ssid"])
        elif network["security"] and NetworkManager._check_known_network(network["ssid"]):
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
