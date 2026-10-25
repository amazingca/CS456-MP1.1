import socket
import time
import sys

heartbeat_interval = 5
heartbeat_message = "HEARTBEAT"

crash_threshold = 3.0

watchdog_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def detect_crash(response):
    last_response_time = None
    if response == b"ACK":
        last_response_time = time.monotonic()

    if last_response_time is None:
        return False

    return time.monotonic() - last_response_time >= crash_threshold

if __name__ == "__main__":

    watchdog_ip = sys.argv[0]
    watchdog_port = sys.argv[1]

    try:
        while True:
            watchdog_socket.sendto(heartbeat_message, (watchdog_ip, watchdog_port))

            # Gets response
            try:
                response, _ = watchdog_socket.recvfrom(1024)

            except socket.timeout:
                pass

            # Checks response
            if detect_crash(response):
                print("Crash suspected.")
                break

            time.sleep(heartbeat_interval)
    finally:
        watchdog_socket.close()
