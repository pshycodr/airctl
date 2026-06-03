import speedtest
import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from airctl.network_manager import NetworkManager
from airctl.utils.cli_help_messages import HelpMessages


class AirctlCli:
    def __init__(self):
        self.console = Console()
        self.parser = self._create_arg_parser()

    def _create_arg_parser(self):
        parser = argparse.ArgumentParser(
            description="AIRCTL - a modern WiFi management tool for Linux",
            add_help=False
        )
        parser.add_argument("-h", "--help", action="store_true")

        subparsers = parser.add_subparsers(dest="command")

        disconnect_parser = subparsers.add_parser("disconnect", add_help=False)
        disconnect_parser.add_argument("-h", "--help", action="store_true")
        disconnect_parser.set_defaults(func=self._disconnect_network)

        status_parser = subparsers.add_parser("status", add_help=False)
        status_parser.add_argument("-h", "--help", action="store_true")
        status_parser.set_defaults(func=self._network_status)

        list_parser = subparsers.add_parser("list", add_help=False)
        list_parser.add_argument("--scan", action="store_true")
        list_parser.add_argument("-h", "--help", action="store_true")
        list_parser.set_defaults(func=self._list_network)

        scan_parser = subparsers.add_parser("scan", add_help=False)
        scan_parser.add_argument("--delay", type=float, default=2.0)
        scan_parser.add_argument("-h", "--help", action="store_true")
        scan_parser.set_defaults(func=self._scan_network)

        connect_parser = subparsers.add_parser("connect", add_help=False)
        connect_parser.add_argument("--ssid")
        connect_parser.add_argument("--password", "-p")
        connect_parser.add_argument("--ifname", "-ifn")
        connect_parser.add_argument("-h", "--help", action="store_true")
        connect_parser.set_defaults(func=self._connect_network)

        toggle_parser = subparsers.add_parser("toggle", add_help=False)
        toggle_parser.add_argument("state", nargs="?", choices=["on", "off"])
        toggle_parser.add_argument("-h", "--help", action="store_true")
        toggle_parser.set_defaults(func=self._toogle_wifi)

        forget_parser = subparsers.add_parser("forget", add_help=False)
        forget_parser.add_argument("--ssid")
        forget_parser.add_argument("-h", "--help", action="store_true")
        forget_parser.set_defaults(func=self._forget_network)

        info_parser = subparsers.add_parser("info", add_help=False)
        info_parser.add_argument("--ssid")
        info_parser.add_argument("-h", "--help", action="store_true")
        info_parser.set_defaults(func=self._network_info)

        speedtest_parser = subparsers.add_parser("speedtest", add_help=False)
        speedtest_parser.add_argument("-h", "--help", action="store_true")
        speedtest_parser.set_defaults(func=self._speedtest_network)

        return parser

    def _show_help(self):
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column(style="cyan")
        table.add_column(style="white")

        table.add_row("status", "Show WiFi status")
        table.add_row("list", "List available networks")
        table.add_row("scan", "Scan for networks")
        table.add_row("connect", "Connect to network")
        table.add_row("disconnect", "Disconnect from network")
        table.add_row("toggle", "Toggle WiFi on/off")
        table.add_row("forget", "Remove saved network")
        table.add_row("info", "Show network details")

        self.console.print("\n[bold cyan]AIRCTL[/] - a modern WiFi management tool for Linux\n")
        self.console.print(table)
        self.console.print("\n[yellow]Usage:[/] airctl <command> [options]")
        self.console.print("[yellow]Help:[/]  airctl <command> -h\n")

    def _show_command_help(self, command):
        if command not in HelpMessages:
            return

        h = HelpMessages[command]
        self.console.print(f"\n[bold]{command}[/] - {h['desc']}\n")
        self.console.print(f"[yellow]Usage:[/]\n  {h['usage']}\n")

        if "options" in h:
            self.console.print("[yellow]Options:[/]")
            for opt in h["options"]:
                self.console.print(f"  {opt}")
            self.console.print()

        self.console.print("[yellow]Examples:[/]")
        for ex in h["examples"]:
            self.console.print(f"  {ex}")
        self.console.print()

    def run(self, argv=None):
        args = self.parser.parse_args(argv)

        if args.help:
            if args.command:
                self._show_command_help(args.command)
            else:
                self._show_help()
            return 0

        if not args.command:
            self._show_help()
            return 0

        return args.func(args)

    def _success(self, message):
        self.console.print(f"[bold green]{message}[/]")

    def _error(self, message):
        self.console.print(f"[bold red]{message}[/]")

    def _warning(self, message):
        self.console.print(f"[bold yellow]{message}[/]")

    def _network_status(self, args=None):
        if hasattr(args, 'help') and args.help:
            self._show_command_help("status")
            return 0

        wifi_on = NetworkManager.wifi_status()
        status_text = "[bold green]ON[/]" if wifi_on else "[bold red]OFF[/]"

        networks = NetworkManager.scan_networks() if wifi_on else []
        active = next((n for n in networks if n["active"]), None)

        if active:
            body = (
                f"WiFi: {status_text}\n"
                f"Connected to: [bold cyan]{active['ssid']}[/]\n"
                f"Signal: {active['signal']}%\n"
                f"Band: {active['freq'] or 'Unknown'}\n"
                f"Security: {active['security'] or 'OPEN'}"
            )
        else:
            body = f"WiFi: {status_text}\n[bold yellow]Not connected[/]"

        self.console.print(Panel(body, title="WiFi Status", expand=False))
        return 0

    def _connect_network(self, args):
        if hasattr(args, 'help') and args.help:
            self._show_command_help("connect")
            return 0

        if not args.ssid:
            self._warning(
                "missing parameter 'ssid'.\nrun 'airctl connect -h' for more info"
            )
            return

        if NetworkManager._check_known_network(ssid=args.ssid):
            result = NetworkManager.connect_network(ssid=args.ssid)
        else:
            missing = [
                name for name, value in (
                    ("password", args.password),
                    ("ifname", args.ifname),
                )
                if not value
            ]
            if missing:
                return self._error(f"missing parameter(s): {', '.join(missing)}\nrun 'airctl connect -h' for more info")

            result = NetworkManager.connect_network(ssid=args.ssid, password=args.password, ifname=args.ifname)

        if result["success"]:
            self._success(result["message"])
            self._network_status()
            return 0

        self._error(result["message"])
        return 1

    def _scan_network(self, args):
        if hasattr(args, 'help') and args.help:
            self._show_command_help("scan")
            return 0

        result = NetworkManager.force_rescan(delay=args.delay)
        if not result["success"]:
            self._error(result["message"])
            return 1
        networks = NetworkManager.scan_networks()
        self._print_network_table(networks)
        return 0

    def _disconnect_network(self, args):
        if hasattr(args, 'help') and args.help:
            self._show_command_help("disconnect")
            return 0

        result = NetworkManager.disconnect_network()
        if result["success"]:
            self._success(result["message"])
            self._network_status()
            return 0
        self._error(result["message"])
        return 1

    def _forget_network(self, args):
        if hasattr(args, 'help') and args.help:
            self._show_command_help("forget")
            return 0

        if not args.ssid:
            args.ssid = NetworkManager.get_active_network_info().connection
        result = NetworkManager.forget_network(args.ssid)
        if result["success"]:
            self._success(result["message"])
            return 0
        self._error(result["message"])
        return 1

    def _toogle_wifi(self, args):
        if hasattr(args, 'help') and args.help:
            self._show_command_help("toggle")
            return 0

        if args.state:
            current = NetworkManager.wifi_status()
            if args.state == "on" and not current:
                NetworkManager.toggle_wifi()
            elif args.state == "off" and current:
                NetworkManager.toggle_wifi()
        else:
            NetworkManager.toggle_wifi()

        self._network_status()
        return 0

    def _network_info(self, args):
        if hasattr(args, 'help') and args.help:
            self._show_command_help("info")
            return 0

        if not args.ssid:
            args.ssid = NetworkManager.get_active_network_info().connection

        info = NetworkManager.get_network_info(args.ssid)
        if info is None:
            self._error(f"No information found for {args.ssid}")
            return 1

        rows = []
        for key, value in vars(info).items():
            if value is None or value == "":
                continue
            rows.append(f"[bold cyan]{key}[/]: {value}")

        body = "\n".join(rows) if rows else "No details available"
        self.console.print(Panel(body, title=f"Network Info: {args.ssid}", expand=False))
        return 0

    def _list_network(self, args=None):
        if hasattr(args, 'help') and args.help:
            self._show_command_help("list")
            return 0

        networks = NetworkManager.scan_networks()
        self._print_network_table(networks)
        return 0

    def _print_network_table(self, networks):
        if not networks:
            self._warning("No networks found")
            return

        table = Table(title="Available WiFi Networks", expand=False)

        table.add_column("SSID", style="bold cyan", width=28, overflow="ellipsis")
        table.add_column("Signal", justify="right", width=8)
        table.add_column("Security", width=12)
        table.add_column("Band", width=8)
        table.add_column("Status", justify="center", width=14)

        for net in networks:
            signal = net["signal"]

            if signal >= 75:
                signal_style = "green"
            elif signal >= 40:
                signal_style = "yellow"
            else:
                signal_style = "red"

            signal_text = f"[{signal_style}]{signal}%[/]"

            if net["active"]:
                ssid = f"[bold green]{net['ssid']}[/]"
                status = "[bold green]CONNECTED[/]"
            else:
                ssid = net["ssid"]
                status = ""

            security = net["security"] or "OPEN"
            band = net["freq"] or "-"

            table.add_row(ssid, signal_text, security, band, status)

        self.console.print(table)
    
    def _speedtest_network(self, args):
        if hasattr(args, 'help') and args.help:
            self._show_command_help("speedtest")
            return 0

        from airctl.speedtest_manager import SpeedtestManager
        from rich.status import Status
        import threading

        event = threading.Event()
        result_data = {}

        def on_result(ping, download, upload):
            result_data['ping'] = ping
            result_data['download'] = download
            result_data['upload'] = upload
            event.set()

        def on_error(err):
            result_data['error'] = err
            event.set()

        with Status("[bold cyan]Starting speed test...[/]", console=self.console) as status:
            def on_progress(msg):
                status.update(f"[bold cyano]{msg}[/]")

            SpeedtestManager.run_speedtest(on_progress, on_result, on_error)
            event.wait()
        
        if 'error' in result_data:
            self._error(f"Speedtest failed: {result_data['error']}")
            return 1

        self.console.print(f"Ping: [bold yellow] {result_data['ping']:.2f} ms[/]")
        self.console.print(f"Download: [bold green] {result_data['download']:.2f} Mbps[/]")
        self.console.print(f"Upload: [bold blue] {result_data['upload']:.2f} Mbps[/]")

        return 0