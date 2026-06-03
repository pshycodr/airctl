import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from airctl.speedtest_manager import SpeedtestManager


class SpeedtestDialog(Gtk.Window):
    def __init__(self, parent):
        super().__init__()
        self.set_title("Speed Test")
        self.set_default_size(300, 200)
        self.set_transient_for(parent)
        self.set_modal(True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)

        nav_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        nav_box.set_margin_bottom(12)
        
        back_button = Gtk.Button()
        back_button.set_icon_name("go-previous-symbolic")
        back_button.set_halign(Gtk.Align.START)
        back_button.connect("clicked", lambda _: self.close())
        
        nav_box.append(back_button)
        box.append(nav_box)

        self.status_label = Gtk.Label(label="Ready to test")
        self.spinner = Gtk.Spinner()

        self.result_label = Gtk.Label(label="")
        self.result_label.set_use_markup(True)

        self.start_button = Gtk.Button(label="Start Test")
        self.start_button.connect("clicked", self.on_start)

        box.append(self.status_label)
        box.append(self.spinner)
        box.append(self.result_label)
        box.append(self.start_button)

        self.set_child(box)
        self._is_closed = False
        self.connect("close-request", self.on_close)

    def on_close(self, window):
        self._is_closed = True
        return False

    def on_start(self, button):
        self.start_button.set_sensitive(False)
        self.spinner.start()
        self.result_label.set_label("")
        SpeedtestManager.run_speedtest(
            progress_callback=lambda msg: GLib.idle_add(self.update_status, msg),
            result_callback=lambda p, d, u: GLib.idle_add(self.show_results, p, d, u),
            error_callback=lambda err: GLib.idle_add(self.show_error, err),
        )

    def update_status(self, msg):
        if getattr(self, '_is_closed', False): return False
        self.status_label.set_label(msg)
        return False

    def show_results(self, ping, download, upload):
        if getattr(self, '_is_closed', False): return False
        self.spinner.stop()
        self.status_label.set_label("Test Complete")
        res = f"Ping: <b>{ping:.2f} ms</b>\nDownload: <b>{download:.2f} Mbps</b>\nUpload: <b>{upload:.2f} Mbps</b>"
        self.result_label.set_markup(res)
        self.start_button.set_sensitive(True)
        self.start_button.set_label("Test Again")
        return False

    def show_error(self, err):
        if getattr(self, '_is_closed', False): return False
        self.spinner.stop()
        self.status_label.set_label("Error occurred")
        self.result_label.set_label(str(err))
        self.start_button.set_sensitive(True)
        self.start_button.set_label("Retry Test")
        return False
