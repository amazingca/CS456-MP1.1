
import socket
import time
import sys

heartbeat_message = bytes("Service is up!", "utf-8")

def send(target_ip, target_port, interval, count):
    sent = 0

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            print(f"Heartbeat audit targeting {target_ip}:{target_port}")
            print("Press Ctrl+C to stop the audit.")

            while count == 0 or sent < count:
                sock.sendto(heartbeat_message, (target_ip, target_port))
                sent += 1

                print(f"[ATTACK] Forged heartbeat #{sent} sent")
                time.sleep(interval)

    except KeyboardInterrupt:
        print("Monitoring stopped")

    except OSError as e:
        print(f"Socket error: {e}")


if __name__ == "__main__":
    ## argv[0] will always be attack.py
    target_ip = sys.argv[1]
    target_port = int(sys.argv[2])

    ## Optional Arguments with defaults
    interval = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    count = int(sys.argv[4]) if len(sys.argv) > 4 else 0

    if not 1 <= target_port <= 65535 or interval < 0.1 or count < 0:
        sys.exit("invalid args")


    send(target_ip, target_port, interval, count)
