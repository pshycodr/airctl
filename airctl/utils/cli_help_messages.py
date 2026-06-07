HelpMessages = {
            "status": {
                "desc": "Show current WiFi status",
                "usage": "airctl status",
                "examples": ["airctl status"]
            },
            "list": {
                "desc": "List available WiFi networks",
                "usage": "airctl list [--scan]",
                "options": ["--scan    Force rescan before listing"],
                "examples": ["airctl list", "airctl list --scan"]
            },
            "scan": {
                "desc": "Force WiFi network scan",
                "usage": "airctl scan [--delay SECONDS]",
                "options": ["--delay    Delay after scan (default: 2.0)"],
                "examples": ["airctl scan", "airctl scan --delay 3.0"]
            },
            "connect": {
                "desc": "Connect to a WiFi network",
                "usage": "airctl connect --ssid SSID [--password PASS] [--ifname IFACE]",
                "options": [
                    "--ssid        Network SSID/Name",
                    "--password    Network password (for new networks)",
                    "--ifname      Interface name (for new networks)"
                ],
                "examples": [
                    "airctl connect --ssid MyNetwork",
                    "airctl connect --ssid MyNetwork --password pass123 --ifname wlan0"
                ]
            },
            "disconnect": {
                "desc": "Disconnect from current network",
                "usage": "airctl disconnect",
                "examples": ["airctl disconnect"]
            },
            "toggle": {
                "desc": "Toggle WiFi on or off",
                "usage": "airctl toggle [on|off]",
                "examples": ["airctl toggle", "airctl toggle on", "airctl toggle off"]
            },
            "forget": {
                "desc": "Remove a saved network",
                "usage": "airctl forget [--ssid SSID]",
                "options": ["--ssid    Network SSID/Name (current if not specified)"],
                "examples": ["airctl forget", "airctl forget --ssid MyNetwork"]
            },
            "info": {
                "desc": "Show detailed network information",
                "usage": "airctl info [--ssid SSID]",
                "options": ["--ssid    Network SSID/Name (current if not specified)"],
                "examples": ["airctl info", "airctl info --ssid MyNetwork"]
            },
            "speedtest": {
                "desc": "Run a network speed test (ping, download, upload)",
                "usage": "airctl speedtest",
                "examples": ["airctl speedtest"]
            }
        }
