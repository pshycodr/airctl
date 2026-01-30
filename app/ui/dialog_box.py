import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk



class DialogBox:
    def __init__(self, parent, ssid: str, callback):
        self.parent = parent
        self.ssid = ssid
        self.callback = callback
        self._shown = False
        self._build_base()

    def _build_base(self):
        self.dialog_window = Gtk.Window(
            title="",
            modal=True,
            transient_for=self.parent,
            default_width=400,
            # default_height=200,
        )

        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.content_box.set_margin_top(24)
        self.content_box.set_margin_bottom(24)
        self.content_box.set_margin_start(24)
        self.content_box.set_margin_end(24)

        self.dialog_window.set_child(self.content_box)

    def password(self):
        if self._shown:
            return
        self._shown = True

        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        title_label = Gtk.Label(label=f"Connect to {self.ssid}")
        title_label.set_halign(Gtk.Align.START)

        # subtitle_label = Gtk.Label(label="Enter the network password")
        # subtitle_label.set_halign(Gtk.Align.START)

        header_box.append(title_label)
        # header_box.append(subtitle_label)

        entry_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        entry_box.set_margin_top(8)

        entry_label = Gtk.Label(label="Password")
        entry_label.set_halign(Gtk.Align.START)

        entry = Gtk.PasswordEntry()
        entry.set_show_peek_icon(True)

        entry_box.append(entry_label)
        entry_box.append(entry)

        buttons = Gtk.Box(spacing=12)
        buttons.set_halign(Gtk.Align.END)
        buttons.set_margin_top(16)

        finished = False

        def finish(value):
            nonlocal finished
            if finished:
                return
            finished = True
            self.dialog_window.destroy()
            self.callback(value)

        cancel = Gtk.Button(label="Cancel")
        cancel.set_size_request(100, -1)
        cancel.connect("clicked", lambda *_: finish(None))

        connect = Gtk.Button(label="Connect")
        connect.set_size_request(100, -1)
        connect.connect("clicked", lambda *_: finish(entry.get_text()))

        entry.connect("activate", lambda *_: finish(entry.get_text()))

        self.dialog_window.connect("close-request", lambda *_: finish(None))

        buttons.append(cancel)
        buttons.append(connect)

        self.content_box.append(header_box)
        self.content_box.append(entry_box)
        self.content_box.append(buttons)

        self.dialog_window.present()
        entry.grab_focus()

    def confirmation(self, message: str = "Are you sure?"):
        if self._shown:
            return
        self._shown = True

        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        title_label = Gtk.Label(label=message)
        title_label.set_halign(Gtk.Align.START)
        title_label.set_wrap(True)
        title_label.set_max_width_chars(40)

        header_box.append(title_label)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(16)

        finished = False

        def finish(value):
            nonlocal finished
            if finished:
                return
            finished = True
            self.dialog_window.destroy()
            self.callback(value)

        no_button = Gtk.Button(label="No")
        no_button.set_size_request(100, -1)
        no_button.connect("clicked", lambda *_: finish(False))

        yes_button = Gtk.Button(label="Yes")
        yes_button.set_size_request(100, -1)
        yes_button.connect("clicked", lambda *_: finish(True))

        self.dialog_window.connect("close-request", lambda *_: finish(False))

        button_box.append(no_button)
        button_box.append(yes_button)

        self.content_box.append(header_box)
        self.content_box.append(button_box)

        self.dialog_window.present()
        yes_button.grab_focus()

    def error(self, message: str = "An error occurred"):
        if self._shown:
            return
        self._shown = True

        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        icon = Gtk.Image()
        icon.set_from_icon_name("dialog-error-symbolic")
        icon.set_pixel_size(48)
        icon.set_margin_bottom(8)

        title_label = Gtk.Label(label="Error")
        title_label.set_halign(Gtk.Align.START)

        message_label = Gtk.Label(label=message)
        message_label.set_halign(Gtk.Align.START)
        message_label.set_wrap(True)
        message_label.set_max_width_chars(40)

        header_box.append(icon)
        header_box.append(title_label)
        header_box.append(message_label)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(16)

        finished = False

        def finish():
            nonlocal finished
            if finished:
                return
            finished = True
            self.dialog_window.destroy()
            if self.callback:
                self.callback(None)

        ok_button = Gtk.Button(label="OK")
        ok_button.set_size_request(100, -1)
        ok_button.connect("clicked", lambda *_: finish())

        self.dialog_window.connect("close-request", lambda *_: finish())

        button_box.append(ok_button)

        self.content_box.append(header_box)
        self.content_box.append(button_box)

        self.dialog_window.present()
        ok_button.grab_focus()

    def info(self, message: str = "Information"):
        if self._shown:
            return
        self._shown = True

        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        icon = Gtk.Image()
        icon.set_from_icon_name("dialog-information-symbolic")
        icon.set_pixel_size(48)
        icon.set_margin_bottom(8)

        title_label = Gtk.Label(label="Information")
        title_label.set_halign(Gtk.Align.START)

        message_label = Gtk.Label(label=message)
        message_label.set_halign(Gtk.Align.START)
        message_label.set_wrap(True)
        message_label.set_max_width_chars(40)

        header_box.append(icon)
        header_box.append(title_label)
        header_box.append(message_label)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(16)

        finished = False

        def finish():
            nonlocal finished
            if finished:
                return
            finished = True
            self.dialog_window.destroy()
            if self.callback:
                self.callback(None)

        ok_button = Gtk.Button(label="OK")
        ok_button.set_size_request(100, -1)
        ok_button.connect("clicked", lambda *_: finish())

        self.dialog_window.connect("close-request", lambda *_: finish())

        button_box.append(ok_button)

        self.content_box.append(header_box)
        self.content_box.append(button_box)

        self.dialog_window.present()
        ok_button.grab_focus()
