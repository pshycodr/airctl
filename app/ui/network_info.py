import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from models import NetworkInfo
from network_manager import NetworkManager
from ui.dialog_box import DialogBox



class NetworkInfoWindow(Gtk.Window):
    def __init__(self, parent, ssid: str):
        super().__init__()
        self.parent = parent
        self.ssid = ssid
        self.network_info = None

        self.set_title("Network Details")
        self.set_default_size(500, 700)
        self.set_transient_for(parent)
        self.set_modal(True)

        self.load_network_info()
        self.setup_ui()

    def load_network_info(self):
        try:
            self.network_info = NetworkManager.get_network_info(self.ssid)
        except Exception as e:
            print(f"Error loading network info: {e}")
            self.network_info = NetworkInfo(ssid=self.ssid)

    def setup_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_spacing(0)

        header_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        header_section.set_spacing(0)

        header_section.append(self.create_navigation())

        main_box.append(header_section)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_propagate_natural_height(False)

        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        info_box.set_spacing(16)
        info_box.set_margin_top(16)
        info_box.set_margin_bottom(16)
        info_box.set_margin_start(16)
        info_box.set_margin_end(16)

        info_box.append(self.create_info_section())
        info_box.append(self.create_network_details_section())

        scrolled.set_child(info_box)
        main_box.append(scrolled)

        self.set_child(main_box)

    def create_navigation(self):
        nav_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        nav_box.set_margin_top(8)
        nav_box.set_margin_bottom(8)
        nav_box.set_margin_start(8)
        nav_box.set_margin_end(8)

        back_button = Gtk.Button()
        back_button.set_icon_name("go-previous-symbolic")
        back_button.connect("clicked", lambda _: self.destroy())

        nav_box.append(back_button)

        return nav_box

    def create_header(self):
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        header_box.set_spacing(8)
        header_box.set_margin_top(16)
        header_box.set_margin_bottom(16)
        header_box.set_halign(Gtk.Align.CENTER)

        wifi_icon = Gtk.Image()
        signal_icon = self.get_signal_icon_name()
        wifi_icon.set_from_icon_name(signal_icon)
        wifi_icon.set_pixel_size(64)

        ssid_label = Gtk.Label(label=self.ssid)

        status_label = Gtk.Label(label="Connected")
        status_label.set_opacity(0.7)

        header_box.append(wifi_icon)
        header_box.append(ssid_label)
        header_box.append(status_label)

        return header_box

    def create_action_buttons(self):
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_box.set_spacing(16)
        button_box.set_margin_top(8)
        button_box.set_margin_bottom(16)
        button_box.set_halign(Gtk.Align.CENTER)

        forget_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        forget_box.set_spacing(4)
        forget_box.set_halign(Gtk.Align.CENTER)

        forget_button = Gtk.Button()
        forget_button.set_icon_name("user-trash-symbolic")
        forget_button.add_css_class("circular")
        forget_button.set_size_request(80, 80)
        forget_button.connect("clicked", self.on_forget_clicked)

        forget_label = Gtk.Label(label="Forget")

        forget_box.append(forget_button)
        forget_box.append(forget_label)

        disconnect_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        disconnect_box.set_spacing(4)
        disconnect_box.set_halign(Gtk.Align.CENTER)

        disconnect_button = Gtk.Button()
        disconnect_button.set_icon_name("window-close-symbolic")
        disconnect_button.add_css_class("circular")
        disconnect_button.set_size_request(80, 80)
        disconnect_button.connect("clicked", self.on_disconnect_clicked)

        disconnect_label = Gtk.Label(label="Disconnect")

        disconnect_box.append(disconnect_button)
        disconnect_box.append(disconnect_label)

        # share_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # share_box.set_spacing(4)
        # share_box.set_halign(Gtk.Align.CENTER)

        # share_button = Gtk.Button()
        # share_button.set_icon_name("share-symbolic")
        # share_button.add_css_class("circular")
        # share_button.set_size_request(80, 80)
        # share_button.connect("clicked", self.on_share_clicked)

        # share_label = Gtk.Label(label="Share")

        # share_box.append(share_button)
        # share_box.append(share_label)

        button_box.append(forget_box)
        button_box.append(disconnect_box)
        # button_box.append(share_box)

        return button_box

    def create_info_section(self):
        section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        section_box.set_spacing(0)

        section_box.append(self.create_header())
        section_box.append(self.create_action_buttons())

        items = []

        if self.network_info.signal_strength is not None:
            signal_strength = self.get_signal_strength_text()
            items.append(
                (
                    "network-wireless-signal-excellent-symbolic",
                    "Signal strength",
                    signal_strength,
                )
            )

        if self.network_info.frequency is not None:
            frequency_ghz = (
                self.network_info.frequency / 1000
                if self.network_info.frequency > 100
                else self.network_info.frequency
            )
            items.append(
                ("network-wireless-symbolic", "Frequency", f"{frequency_ghz} GHz")
            )

        if self.network_info.security is not None:
            items.append(
                ("security-high-symbolic", "Security", self.get_security_text())
            )

        for i, (icon_name, title, subtitle) in enumerate(items):
            item_box = self.create_info_item(icon_name, title, subtitle)
            section_box.append(item_box)

            if i < len(items) - 1:
                separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                section_box.append(separator)

        return section_box

    def create_info_item(self, icon_name: str, title: str, subtitle: str):
        item_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        item_box.set_spacing(12)
        item_box.set_margin_top(12)
        item_box.set_margin_bottom(12)
        item_box.set_margin_start(12)
        item_box.set_margin_end(12)

        icon = Gtk.Image()
        icon.set_from_icon_name(icon_name)
        icon.set_pixel_size(24)
        icon.set_opacity(0.7)

        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        text_box.set_spacing(2)
        text_box.set_hexpand(True)

        title_label = Gtk.Label(label=title, xalign=0)

        subtitle_label = Gtk.Label(label=subtitle, xalign=0)
        subtitle_label.set_opacity(0.7)

        text_box.append(title_label)
        text_box.append(subtitle_label)

        item_box.append(icon)
        item_box.append(text_box)

        return item_box

    def create_network_details_section(self):
        section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        section_box.set_spacing(8)

        header_label = Gtk.Label(label="Network details", xalign=0)
        header_label.set_margin_bottom(8)

        section_box.append(header_label)

        details_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        details_card.set_spacing(0)

        details = []

        if self.network_info.type:
            details.append(("Type", self.network_info.type))

        if self.network_info.mac_address:
            details.append(("MAC address", self.network_info.mac_address))

        if self.network_info.ip_address:
            details.append(("IP address", self.network_info.ip_address))

        if self.network_info.gateway:
            details.append(("Gateway", self.network_info.gateway))

        if self.network_info.subnet_mask:
            details.append(("Subnet mask", self.network_info.subnet_mask))

        if self.network_info.dns:
            for idx, dns in enumerate(self.network_info.dns):
                label = "DNS" if idx == 0 else f"DNS {idx + 1}"
                details.append((label, dns))

        if self.network_info.ipv6_address:
            details.append(("IPv6 address", self.network_info.ipv6_address))

        if self.network_info.transmit_link_speed:
            details.append(
                ("Transmit link speed", f"{self.network_info.transmit_link_speed} Mbps")
            )

        if self.network_info.receive_link_speed:
            details.append(
                ("Receive link speed", f"{self.network_info.receive_link_speed} Mbps")
            )

        if self.network_info.interface:
            details.append(("Interface", self.network_info.interface))

        if self.network_info.uuid:
            details.append(("UUID", self.network_info.uuid))

        if self.network_info.dhcp_lease_time:
            details.append(
                ("DHCP lease time", f"{self.network_info.dhcp_lease_time} seconds")
            )

        for i, (label, value) in enumerate(details):
            detail_box = self.create_detail_row(label, value)
            details_card.append(detail_box)

            if i < len(details) - 1:
                separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                details_card.append(separator)

        section_box.append(details_card)

        return section_box

    def create_detail_row(self, label: str, value: str):
        row_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        row_box.set_spacing(4)
        row_box.set_margin_top(12)
        row_box.set_margin_bottom(12)
        row_box.set_margin_start(12)
        row_box.set_margin_end(12)

        label_widget = Gtk.Label(label=label, xalign=0)

        value_widget = Gtk.Label(label=value, xalign=0)
        value_widget.set_opacity(0.7)
        value_widget.set_selectable(True)
        value_widget.set_wrap(True)
        value_widget.set_max_width_chars(50)

        row_box.append(label_widget)
        row_box.append(value_widget)

        return row_box

    def get_signal_icon_name(self):
        if not self.network_info or self.network_info.signal_strength is None:
            return "network-wireless-signal-excellent-symbolic"

        signal = self.network_info.signal_strength
        if signal >= 75:
            return "network-wireless-signal-excellent-symbolic"
        elif signal >= 50:
            return "network-wireless-signal-good-symbolic"
        elif signal >= 25:
            return "network-wireless-signal-ok-symbolic"
        else:
            return "network-wireless-signal-weak-symbolic"

    def get_signal_strength_text(self):
        if not self.network_info or self.network_info.signal_strength is None:
            return "Unknown"

        signal = self.network_info.signal_strength
        if signal >= 75:
            return "Excellent"
        elif signal >= 50:
            return "Good"
        elif signal >= 25:
            return "Fair"
        else:
            return "Weak"

    def get_security_text(self):
        if not self.network_info or not self.network_info.security:
            return "None"

        security = self.network_info.security.lower()
        if "wpa2" in security or "wpa-psk" in security:
            return "WPA/WPA2-Personal"
        elif "wpa3" in security:
            return "WPA3-Personal"
        elif "wpa" in security:
            return "WPA-Personal"
        else:
            return self.network_info.security

    def on_forget_clicked(self, button):
        def on_confirm(confirmed):
            if not confirmed:
                return

            result = NetworkManager.forget_network(self.ssid)
            if result["success"]:
                self.destroy()
                if self.parent:
                    DialogBox(self.parent, self.ssid, None).info(result["message"])
            else:
                DialogBox(self.parent, self.ssid, None).error(result["message"])

        DialogBox(self.parent, self.ssid, on_confirm).confirmation(
            message=f"Forget network {self.ssid}?"
        )

    def on_disconnect_clicked(self, button):
        def on_confirm(confirmed):
            if not confirmed:
                return

            result = NetworkManager.disconnect_network()
            if result["success"]:
                self.destroy()
                if self.parent:
                    DialogBox(self.parent, self.ssid, None).info(result["message"])
            else:
                DialogBox(self.parent, self.ssid, None).error(result["message"])

        DialogBox(self.parent, self.ssid, on_confirm).confirmation(
            message=f"Disconnect from {self.ssid}?"
        )

    def on_share_clicked(self, button):
        DialogBox(self.parent, self.ssid, None).info("Share feature coming soon")
