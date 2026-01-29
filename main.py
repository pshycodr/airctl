import sys

import gi
from gi.repository import Gdk, Gtk

from core.ui.app_header import AppHeader
from core.ui.network_list import NetworkListWidget

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

        toggle_switch = Gtk.Switch()
        toggle_switch.set_css_classes(["switch-custom"])
        toggle_switch.props.halign = Gtk.Align.END

        hbox.append(toggle_switch)

        container.append(hbox)

        self.listBox = NetworkListWidget(self)
        self.listBox.props.selection_mode = Gtk.SelectionMode.NONE
        container.append(self.listBox)

    def _swtich_active(self, switch, param):
        print("switch actice")


class MyApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="io.github.airctl")

    def do_activate(self):
        win = AppWindow(self)
        win.present()


if __name__ == "__main__":
    app = MyApp()
    app.run(sys.argv)
