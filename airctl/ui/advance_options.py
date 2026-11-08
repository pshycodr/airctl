import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from airctl.advanced_options import normalize_advanced_options


class AdvancedOptionsBox(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        self._change_callback = None
        self._build_toggle()
        self._build_options()
        self.set_expanded(False)

    def _build_toggle(self):
        toggle_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        self.toggle_button = Gtk.Button()
        self.toggle_button.add_css_class("flat")
        self.toggle_button.add_css_class("circular")
        self.toggle_button.add_css_class("advanced-options-toggle")
        self.toggle_button.connect("clicked", lambda *_: self.set_expanded(not self.is_expanded()))

        self.toggle_icon = Gtk.Image.new_from_icon_name("list-add-symbolic")
        self.toggle_button.set_child(self.toggle_icon)

        self.toggle_label = Gtk.Label(label="Advanced options")
        self.toggle_label.set_halign(Gtk.Align.START)
        self.toggle_label.set_hexpand(True)

        toggle_row.append(self.toggle_button)
        toggle_row.append(self.toggle_label)
        self.append(toggle_row)

        self.revealer = Gtk.Revealer()
        self.revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.append(self.revealer)

    def _build_options(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_max_content_height(360)
        scrolled.set_propagate_natural_height(True)

        self.options_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.options_box.set_margin_top(8)
        self.options_box.set_margin_bottom(4)
        scrolled.set_child(self.options_box)
        self.revealer.set_child(scrolled)

        self.metered = self._add_dropdown(
            self.options_box,
            "Metered",
            ["Detect automatically", "Treat as metered", "Treat as unmetered"],
        )

        self.proxy = self._add_dropdown(
            self.options_box,
            "Proxy",
            ["None", "Manual", "Proxy Auto-Config"],
        )

        self.proxy_manual_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.proxy_host = self._add_entry(
            self.proxy_manual_box,
            "Proxy host",
            "proxy.example.com",
        )
        self.proxy_port = self._add_entry(
            self.proxy_manual_box,
            "Proxy port",
            "8080",
        )
        self.options_box.append(self.proxy_manual_box)

        self.proxy_pac_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.pac_url = self._add_entry(
            self.proxy_pac_box,
            "PAC URL",
            "https://example.com/proxy.pac",
        )
        self.options_box.append(self.proxy_pac_box)

        self.proxy.connect("notify::selected", self._on_proxy_changed)
        self._on_proxy_changed(self.proxy, None)

        self.ip_settings = self._add_dropdown(
            self.options_box,
            "IP settings",
            ["DHCP", "Static"],
        )

        self.static_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.ip_address = self._add_entry(
            self.static_box,
            "IP address",
            "192.168.1.50",
        )
        self.ip_prefix = self._add_entry(
            self.static_box,
            "Prefix length",
            "24",
        )
        self.ip_gateway = self._add_entry(
            self.static_box,
            "Gateway",
            "192.168.1.1",
        )
        self.ip_dns = self._add_entry(
            self.static_box,
            "DNS servers",
            "1.1.1.1, 8.8.8.8",
        )
        self.options_box.append(self.static_box)

        self.ip_settings.connect("notify::selected", self._on_ip_changed)
        self._on_ip_changed(self.ip_settings, None)

        self.privacy = self._add_dropdown(
            self.options_box,
            "Privacy",
            ["Use randomised MAC", "Use device MAC"],
        )
        self.privacy.set_selected(1)

        self.send_hostname = self._add_dropdown(
            self.options_box,
            "Send device name",
            ["Send device name", "Don't send device name"],
        )

    def _add_dropdown(self, parent, title, options):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        label = Gtk.Label(label=title)
        label.set_halign(Gtk.Align.START)

        dropdown = Gtk.DropDown.new_from_strings(options)
        dropdown.connect("notify::selected", self._on_changed)

        box.append(label)
        box.append(dropdown)
        parent.append(box)

        return dropdown

    def _add_entry(self, parent, title, placeholder):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        label = Gtk.Label(label=title)
        label.set_halign(Gtk.Align.START)

        entry = Gtk.Entry()
        entry.set_placeholder_text(placeholder)
        entry.connect("changed", self._on_changed)

        box.append(label)
        box.append(entry)
        parent.append(box)

        return entry

    def _on_proxy_changed(self, dropdown, _):
        selected = dropdown.get_selected()
        self.proxy_manual_box.set_visible(selected == 1)
        self.proxy_pac_box.set_visible(selected == 2)
        self._emit_changed()

    def _on_ip_changed(self, dropdown, _):
        self.static_box.set_visible(dropdown.get_selected() == 1)
        self._emit_changed()

    def _on_changed(self, *_):
        self._emit_changed()

    def _emit_changed(self):
        if self._change_callback is not None:
            self._change_callback()

    def set_change_callback(self, callback):
        self._change_callback = callback

    def is_expanded(self) -> bool:
        return self.revealer.get_reveal_child()

    def set_expanded(self, expanded: bool):
        self.revealer.set_reveal_child(expanded)
        self.toggle_icon.set_from_icon_name(
            "list-remove-symbolic" if expanded else "list-add-symbolic"
        )
        self.toggle_button.set_tooltip_text(
            "Hide advanced options" if expanded else "Show advanced options"
        )

    def get_options(self) -> dict:
        proxy_values = ["none", "manual", "pac"]
        privacy_values = ["random", "device"]
        metered_values = ["auto", "metered", "unmetered"]

        proxy_mode = proxy_values[self.proxy.get_selected()]
        ip_mode = "static" if self.ip_settings.get_selected() == 1 else "dhcp"

        options = {
            "metered": metered_values[self.metered.get_selected()],
            "proxy": {"mode": proxy_mode},
            "ip": {"mode": ip_mode},
            "privacy": privacy_values[self.privacy.get_selected()],
            "send_device_name": self.send_hostname.get_selected() == 0,
        }

        if proxy_mode == "manual":
            options["proxy"].update(
                {
                    "host": self.proxy_host.get_text(),
                    "port": self.proxy_port.get_text(),
                }
            )
        elif proxy_mode == "pac":
            options["proxy"]["pac_url"] = self.pac_url.get_text()

        if ip_mode == "static":
            options["ip"].update(
                {
                    "address": self.ip_address.get_text(),
                    "prefix": self.ip_prefix.get_text(),
                    "gateway": self.ip_gateway.get_text(),
                    "dns": self.ip_dns.get_text(),
                }
            )

        return normalize_advanced_options(options)
