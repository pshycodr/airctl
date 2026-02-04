import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk, Gtk


class NetworkManagerErrorWidget(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, vexpand=True, spacing=24)
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        self.set_margin_top(40)
        self.set_margin_bottom(40)
        self.set_margin_start(40)
        self.set_margin_end(40)

        icon = Gtk.Image()
        icon.set_from_icon_name("dialog-error-symbolic")
        icon.set_pixel_size(64)

        title = Gtk.Label(label="NetworkManager is not running")
        title.add_css_class("title-1")

        message = Gtk.Label(label="AIRCTL requires NetworkManager to manage WiFi connections.")
        message.set_wrap(True)
        message.set_max_width_chars(50)
        message.set_justify(Gtk.Justification.CENTER)

        inst_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        inst_box.set_margin_top(8)

        check_label = Gtk.Label(label="Please check:")
        check_label.set_halign(Gtk.Align.START)

        cmd_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        cmd_box.set_halign(Gtk.Align.START)

        check_entry = Gtk.Entry()
        check_entry.set_text("systemctl status NetworkManager")
        check_entry.set_editable(False)
        check_entry.set_width_chars(35)

        copy_button = Gtk.Button(label="Copy")
        copy_button.connect("clicked", lambda _: self._copy_to_clipboard("systemctl status NetworkManager"))

        cmd_box.append(check_entry)
        cmd_box.append(copy_button)

        inactive_label = Gtk.Label(label="If it's inactive, start and enable it with:")
        inactive_label.set_halign(Gtk.Align.START)
        inactive_label.set_margin_top(8)

        enable_cmd_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        enable_cmd_box.set_halign(Gtk.Align.START)

        enable_entry = Gtk.Entry()
        enable_entry.set_text("sudo systemctl enable --now NetworkManager")
        enable_entry.set_editable(False)
        enable_entry.set_width_chars(42)

        enable_copy_button = Gtk.Button(label="Copy")
        enable_copy_button.connect("clicked", lambda _: self._copy_to_clipboard("sudo systemctl enable --now NetworkManager"))

        enable_cmd_box.append(enable_entry)
        enable_cmd_box.append(enable_copy_button)

        retry_label = Gtk.Label(label="Then try running airctl again.")
        retry_label.set_halign(Gtk.Align.START)
        retry_label.set_margin_top(8)
        retry_label.set_opacity(0.7)

        inst_box.append(check_label)
        inst_box.append(cmd_box)
        inst_box.append(inactive_label)
        inst_box.append(enable_cmd_box)
        inst_box.append(retry_label)

        self.append(icon)
        self.append(title)
        self.append(message)
        self.append(inst_box)

    def _copy_to_clipboard(self, text):
        clipboard = Gdk.Display.get_default().get_clipboard()
        clipboard.set(text)
