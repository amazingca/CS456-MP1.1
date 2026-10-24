import socket
import time

heartbeat_interval = 5
heartbeat_message = "HEARTBEAT"

watchdog_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def request_watchdog_info():
    print("Enter watchdog IP: ")
    watchdog_ip = input()
    print("Enter watchdog port: ")
    watchdog_port = input()
    return watchdog_ip, watchdog_port


def detect_crash():
    pass # TODO: set crash threshold well below watchdog crash threshold


if __name__ == "__main__":

    watchdog_ip, watchdog_port = request_watchdog_info()

    try:
        while True:
            watchdog_socket.sendto(heartbeat_message, (watchdog_ip, watchdog_port))
            time.sleep(heartbeat_interval)
    finally:
        watchdog_socket.close()