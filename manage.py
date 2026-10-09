#!/usr/bin/env python
"""Django command entry point for the local DATARA application."""
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "datara.settings")

from django.core.management import execute_from_command_line


def _local_single_process_argv(argv: list[str]) -> list[str]:
    """Constrain the supported local server to loopback and one process."""
    if len(argv) < 2 or argv[1] != "runserver":
        return argv

    if os.environ.get("DATARA_ENV", "milestone-a-local") != "milestone-a-local":
        raise SystemExit("The local runserver is available only in milestone-a-local mode.")

    args = list(argv)
    ipv6_requested = "--ipv6" in args or "-6" in args
    address_index = next(
        (index for index, value in enumerate(args[2:], start=2) if not value.startswith("-")),
        None,
    )
    if address_index is None:
        args.insert(2, "[::1]:8000" if ipv6_requested else "127.0.0.1:8000")
    else:
        address = args[address_index]
        if ":" in address:
            host = address.rsplit(":", 1)[0].strip("[]").lower()
        elif address.isdigit():
            host = "::1" if ipv6_requested else "127.0.0.1"
            args[address_index] = f"[{host}]:{address}" if ipv6_requested else address
        else:
            host = address.lower()
        if host not in {"127.0.0.1", "localhost", "::1"}:
            raise SystemExit("The supported DATARA local server must bind to loopback.")
        if ipv6_requested and host != "::1":
            raise SystemExit("The --ipv6 option requires the IPv6 loopback address.")
        if host == "::1" and "--ipv6" not in args:
            args.append("--ipv6")

    if "--nothreading" not in args:
        args.append("--nothreading")
    if "--noreload" not in args:
        args.append("--noreload")

    # This launch marker rejects ordinary direct WSGI starts. It is a local
    # launch convention, not a security boundary against a deliberate bypass.
    os.environ["DATARA_LOCAL_SINGLE_PROCESS_SERVER"] = "1"
    return args


if __name__ == "__main__":
    execute_from_command_line(_local_single_process_argv(sys.argv))
