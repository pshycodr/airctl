import sys


CLI_COMMANDS = {
    "status",
    "list",
    "scan",
    "connect",
    "disconnect",
    "toggle",
    "forget",
    "info",
    "speedtest",
}


def run_cli(argv):
    from airctl.cli import AirctlCli
    cli = AirctlCli()
    return cli.run(argv)


def run_gui():
    from airctl.gui import run
    return run()


def main():
    argv = sys.argv[1:]

    if argv and (argv[0] in CLI_COMMANDS or argv[0].startswith("-")):
        return run_cli(argv)

    return run_gui()


if __name__ == "__main__":
    sys.exit(main())
