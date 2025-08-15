# -*- coding: utf-8 -*-
import socket
import subprocess
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_port_available(port):
    """
    Check if a given port is available (not in use) on the local system.

    Args:
        port (int): The port number to check.

    Returns:
        bool: True if the port is available, False if it is in use.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("", port))
            # Port is available
            return True
        except OSError:
            # Port is in use
            return False


def sweep_port(port):
    """
    Sweep all processes found listening on a given port.

    Args:
        port (int): The port number.

    Returns:
        int: Number of processes swept (terminated).
    """
    try:
        # Use lsof to find the processes using the port
        result = subprocess.run(
            ["lsof", "-i", f":{port}"],
            capture_output=True,
            text=True,
            check=True,
        )

        # Parse the output
        lines = result.stdout.strip().split("\n")
        if len(lines) <= 1:
            # No process is using the port
            return 0

        # Iterate over each line (excluding the header) and kill each process
        killed_count = 0
        for line in lines[1:]:
            parts = line.split()
            if len(parts) > 1:
                pid = parts[1]

                # Kill the process using the PID
                subprocess.run(["kill", "-9", pid], check=False)
                killed_count += 1

        if not is_port_available(port):
            logger.warning(
                f"Port {port} is still in use after killing processes.",
            )

        return True

    except Exception as e:
        logger.error(
            f"An error occurred while killing processes on port {port}: {e}",
        )
        return False
