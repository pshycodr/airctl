import sys

import gi
from gi.repository import Gdk, GLib, Gtk

from core.network_manager import NetworkManager
from core.ui.app_header import AppHeader
from core.ui.network_list import NetworkListWidget
from core.ui.wifi_off_widget import WiFiOffWidget

gi.require_version("Gtk", "4.0")

css_provider = Gtk.CssProvider()
css_provider.load_from_path("styles/style.css")
Gtk.StyleContext.add_provider_for_display(
    Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)


class AppWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)

        self.set_title(title="AIRCTL")
        self.set_default_size(450, 350)

        header_bar = AppHeader()
        self.set_titlebar(header_bar)

        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_child(container)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        hbox.props.valign = Gtk.Align.START

        label = Gtk.Label(label="WiFi")
        label.set_css_classes(["label-wifi"])

        hbox.append(label)

        label = Gtk.Label(label="WiFi")

        label.set_margin_top(10)
        label.set_margin_bottom(5)
        label.set_margin_start(15)
        label.set_margin_end(15)

        self.toggle_switch = Gtk.Switch()
        self.toggle_switch.set_css_classes(["switch-custom"])
        self.toggle_switch.props.halign = Gtk.Align.END
        self.toggle_switch.props.active = NetworkManager.wifi_status()
        self.toggle_switch.connect("notify::active", self._switch_active)

        hbox.append(self.toggle_switch)

        container.append(hbox)

        self.widget_stack = Gtk.Stack()
        container.append(self.widget_stack)

        self.listBox = NetworkListWidget(self, self.widget_stack)
        self.listBox.props.selection_mode = Gtk.SelectionMode.NONE

        self.wifi_off_widget = WiFiOffWidget()

        self.widget_stack.add_titled(self.listBox, "network_list", "")
        self.widget_stack.add_titled(self.wifi_off_widget, "wifi_off", "")

        self._update_wifi_state(NetworkManager.wifi_status())

        # Poll wifi status every second to catch external changes
        GLib.timeout_add(1000, self._check_wifi_status)

    def _check_wifi_status(self):
        current_status = NetworkManager.wifi_status()
        switch_status = self.toggle_switch.get_active()

        if current_status != switch_status:
            # Block the signal handler to prevent recursive calls
            self.toggle_switch.handler_block_by_func(self._switch_active)
            self.toggle_switch.set_active(current_status)
            self.toggle_switch.handler_unblock_by_func(self._switch_active)
            self._update_wifi_state(current_status)

        return True  # Continue the timeout

    def _update_wifi_state(self, is_on):
        if is_on:
            self.widget_stack.set_visible_child_name("network_list")
            self.listBox.on_wifi_enabled()
        else:
            self.widget_stack.set_visible_child_name("wifi_off")
            self.listBox.on_wifi_disabled()

    def _switch_active(self, switch, param):
        is_active = switch.get_active()
        NetworkManager.toggle_wifi()

        # Wait a bit for wifi to actually change state
        GLib.timeout_add(500, lambda: self._update_wifi_state(is_active))


class MyApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="io.github.airctl")

    def do_activate(self):
        win = AppWindow(self)
        win.present()


if __name__ == "__main__":
    app = MyApp()
    app.run(sys.argv)
