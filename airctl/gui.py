import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")

from gi.repository import (
    Gdk,
    GLib,
    Gtk,
)

from importlib.resources import files

from airctl.network_manager import (
    NetworkManager,
)

from airctl.ui.nm_error_widget import (
    NetworkManagerErrorWidget,
)

from airctl.window.overlay import (
    setup_overlay_window,
)

from airctl.window.window_config import (
    add_escape_close,
)

from airctl.window.actions import (
    setup_actions,
    open_github,
    show_about_dialog,
)

from airctl.window.layout import (
    build_main_layout,
)


css_provider = Gtk.CssProvider()

css_data = files(
    "airctl.styles"
).joinpath(
    "style.css"
).read_bytes()

css_provider.load_from_data(css_data)

Gtk.StyleContext.add_provider_for_display(
    Gdk.Display.get_default(),
    css_provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
)


class AppWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)

        self.set_title(title="AIRCTL")
        self.set_default_size(450, 600)

        setup_overlay_window(self)

        add_escape_close(self)

        setup_actions(self)

        if not NetworkManager.is_networkmanager_running():
            self.set_child(
                NetworkManagerErrorWidget()
            )

            return

        build_main_layout(self)

        self._update_wifi_state(
            NetworkManager.wifi_status()
        )

        GLib.timeout_add(
            1000,
            self._check_wifi_status,
        )

    def show_about_dialog(
        self,
        action,
        param,
    ):
        show_about_dialog(
            self,
            action,
            param,
        )

    def open_github(
        self,
        action,
        param,
    ):
        open_github(
            self,
            action,
            param,
        )

    def _check_wifi_status(self):
        current_status = (
            NetworkManager.wifi_status()
        )

        switch_status = (
            self.toggle_switch.get_active()
        )

        if current_status != switch_status:
            self.toggle_switch.handler_block_by_func(
                self._switch_active
            )

            self.toggle_switch.set_active(
                current_status
            )

            self.toggle_switch.handler_unblock_by_func(
                self._switch_active
            )

            self._update_wifi_state(
                current_status
            )

        return True

    def _update_wifi_state(
        self,
        is_on,
    ):
        if is_on:
            self.widget_stack.set_visible_child_name(
                "network_list"
            )

            self.listBox.on_wifi_enabled()

        else:
            self.widget_stack.set_visible_child_name(
                "wifi_off"
            )

            self.listBox.on_wifi_disabled()

    def _switch_active(
        self,
        switch,
        param,
    ):
        is_active = switch.get_active()

        NetworkManager.toggle_wifi()

        GLib.timeout_add(
            500,
            lambda: self._update_wifi_state(
                is_active
            ),
        )


class MyApp(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="io.github.airctl"
        )

    def do_activate(self):
        win = AppWindow(self)
        win.present()


def run():
    app = MyApp()
    return app.run(sys.argv)
