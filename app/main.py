import sys

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, GLib, Gtk, Gio

from network_manager import NetworkManager
from ui.app_header import AppHeader
from ui.network_list import NetworkListWidget
from ui.wifi_off_widget import WiFiOffWidget


css_provider = Gtk.CssProvider()
css_provider.load_from_path("styles/style.css")
Gtk.StyleContext.add_provider_for_display(
    Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)


class AppWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)

        self.set_title(title="AIRCTL")
        self.set_default_size(450, 600)

        header_bar = AppHeader()
        self.set_titlebar(header_bar)

        self._setup_actions()

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_spacing(0)
        self.set_child(main_box)

        wifi_toggle_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        wifi_toggle_box.set_margin_top(16)
        wifi_toggle_box.set_margin_bottom(16)
        wifi_toggle_box.set_margin_start(16)
        wifi_toggle_box.set_margin_end(16)
        wifi_toggle_box.set_spacing(12)

        wifi_label = Gtk.Label(label="Use Wi-Fi")
        wifi_label.set_halign(Gtk.Align.START)
        wifi_label.set_hexpand(True)
        wifi_label.add_css_class("wifi-toggle-label")

        self.toggle_switch = Gtk.Switch()
        self.toggle_switch.set_halign(Gtk.Align.END)
        self.toggle_switch.set_active(NetworkManager.wifi_status())
        self.toggle_switch.connect("notify::active", self._switch_active)

        wifi_toggle_box.append(wifi_label)
        wifi_toggle_box.append(self.toggle_switch)

        main_box.append(wifi_toggle_box)

        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_start(16)
        separator.set_margin_end(16)
        main_box.append(separator)

        self.widget_stack = Gtk.Stack()
        self.widget_stack.set_vexpand(True)
        main_box.append(self.widget_stack)

        self.listBox = NetworkListWidget(self, self.widget_stack)

        self.wifi_off_widget = WiFiOffWidget()

        self.widget_stack.add_titled(self.listBox, "network_list", "")
        self.widget_stack.add_titled(self.wifi_off_widget, "wifi_off", "")

        self._update_wifi_state(NetworkManager.wifi_status())

        GLib.timeout_add(1000, self._check_wifi_status)

    def _setup_actions(self):
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self._show_about_dialog)
        self.get_application().add_action(about_action)

        github_action = Gio.SimpleAction.new("github", None)
        github_action.connect("activate", self._open_github)
        self.get_application().add_action(github_action)

    def _show_about_dialog(self, action, param):
        about = Gtk.AboutDialog()
        about.set_transient_for(self)
        about.set_modal(True)
        about.set_program_name("AIRCTL")
        about.set_version("1.0.0")
        about.set_comments("A modern WiFi management tool for Linux")
        about.set_website("https://github.com/pshycodr/airctl")
        about.set_website_label("View on GitHub")
        about.set_authors(["pshycodr"])
        about.set_license_type(Gtk.License.MIT_X11)
        about.set_logo_icon_name("network-wireless-symbolic")

        about.set_copyright("© 2026 pshycodr")

        about.add_credit_section("Thanks to", [
            "nmcli team",
            "GTK developers",
            "Open source community"
        ])

        about.present()

    def _open_github(self, action, param):
        import subprocess
        try:
            subprocess.Popen(["xdg-open", "https://github.com/pshycodr/airctl"])
        except Exception as e:
            print(f"Failed to open GitHub link: {e}")

    def _check_wifi_status(self):
        current_status = NetworkManager.wifi_status()
        switch_status = self.toggle_switch.get_active()

        if current_status != switch_status:
            self.toggle_switch.handler_block_by_func(self._switch_active)
            self.toggle_switch.set_active(current_status)
            self.toggle_switch.handler_unblock_by_func(self._switch_active)
            self._update_wifi_state(current_status)

        return True

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
