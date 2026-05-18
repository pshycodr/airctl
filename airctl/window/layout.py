from gi.repository import Gtk

from airctl.network_manager import NetworkManager

from airctl.ui.app_header import AppHeader
from airctl.ui.network_list import (
    NetworkListWidget,
)
from airctl.ui.wifi_off_widget import (
    WiFiOffWidget,
)


def build_main_layout(window):
    main_box = Gtk.Box(
        orientation=Gtk.Orientation.VERTICAL
    )

    main_box.set_spacing(0)

    window.set_child(main_box)

    header_bar = AppHeader()
    main_box.append(header_bar)

    wifi_toggle_box = Gtk.Box(
        orientation=Gtk.Orientation.HORIZONTAL
    )

    wifi_toggle_box.set_margin_top(16)
    wifi_toggle_box.set_margin_bottom(16)
    wifi_toggle_box.set_margin_start(16)
    wifi_toggle_box.set_margin_end(16)

    wifi_toggle_box.set_spacing(12)

    wifi_label = Gtk.Label(
        label="Use Wi-Fi"
    )

    wifi_label.set_halign(
        Gtk.Align.START
    )

    wifi_label.set_hexpand(True)

    wifi_label.add_css_class(
        "wifi-toggle-label"
    )

    window.toggle_switch = Gtk.Switch()

    window.toggle_switch.set_halign(
        Gtk.Align.END
    )

    window.toggle_switch.set_active(
        NetworkManager.wifi_status()
    )

    window.toggle_switch.connect(
        "notify::active",
        window._switch_active,
    )

    wifi_toggle_box.append(wifi_label)

    wifi_toggle_box.append(
        window.toggle_switch
    )

    main_box.append(wifi_toggle_box)

    separator = Gtk.Separator(
        orientation=Gtk.Orientation.HORIZONTAL
    )

    separator.set_margin_start(16)
    separator.set_margin_end(16)

    main_box.append(separator)

    window.widget_stack = Gtk.Stack()

    window.widget_stack.set_vexpand(True)

    main_box.append(window.widget_stack)

    window.listBox = NetworkListWidget(
        window,
        window.widget_stack,
    )

    window.wifi_off_widget = (
        WiFiOffWidget()
    )

    window.widget_stack.add_titled(
        window.listBox,
        "network_list",
        "",
    )

    window.widget_stack.add_titled(
        window.wifi_off_widget,
        "wifi_off",
        "",
    )
