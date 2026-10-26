import socket
import time
import sys

heartbeat_interval = 5
heartbeat_message = "HEARTBEAT"
crash_threshold = 3.0
watchdog_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def detect_crash(r):
    last_response_time = None
    if len(r) > 0:
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

            try:
                response, _ = watchdog_socket.recvfrom(1024)
                ## -1 = Error
                ## 0 = Connection is closed gracefully
                ## Else size of message sent (active port)

            ## Possible Errors from recv
            except ConnectionRefusedError:
                print("The client is down or unreachable")
            except socket.timeout:
                pass
            except socket.error as e:
                print(f"Socket error occurred: {e}")

            # Checks response
            if detect_crash(response):
                print("Crash suspected.")
                break

            time.sleep(heartbeat_interval)
    finally:
            watchdog_socket.close()

