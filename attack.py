import socket
import time
import sys

heartbeat_interval = 5
heartbeat_message = "HEARTBEAT"

watchdog_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def detect_crash():
    pass # TODO: set crash threshold well below watchdog crash threshold


if __name__ == "__main__":

    watchdog_ip = sys.argv[0]
    watchdog_port = sys.argv[1]

    try:
        while True:
            watchdog_socket.sendto(heartbeat_message, (watchdog_ip, watchdog_port))
            time.sleep(heartbeat_interval)
    finally:
        watchdog_socket.close()