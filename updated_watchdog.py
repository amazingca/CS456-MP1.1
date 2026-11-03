import datetime
import socket
import sys
import time
import argparse

# Assuming the default situation is a broadcast heartbeat, there is one watchdog-ip
# per user session, but they're all listening on the same heartbeat port.
help = """
--watchdog-ip:        Listening IP for the watchdog.
--watchdog-port:      Listening port for the watchdog. Same as heartbeat

--service-ip:  IP for the service
--service-port: Port for the service"""

watchdog_ip = None
watchdog_port = None

service_ip = None
service_port = None

sync_ip = None
sync_port = None

def port_within_range(port):
    return True if port > 1023 and port < 65536 else False

def environment_initialization():
    parser = argparse.ArgumentParser(
        description="Watchdog service for monitoring service heartbeats."
    )

    parser.add_argument(
        "--watchdog-ip",
        required=True,
        help="Listening IP for the watchdog."
    )

    parser.add_argument(
        "--watchdog-port",
        required=True,
        type=int,
        help="Listening port for the watchdog. Same as heartbeat."
    )

    parser.add_argument(
        "--service-ip",
        required=True,
        help="IP address for the service."
    )

    parser.add_argument(
        "--service-port",
        required=True,
        type=int,
        help="Port for the service."
    )

    parser.add_argument(
        "--sync-ip",
        required=True,
        help="IP address for the synchronization service."
    )

    parser.add_argument(
        "--sync-port",
        required=True,
        type=int,
        help="Port for the synchronization service."
    )

    args = parser.parse_args()

    # Validate port ranges
    ports = {
        "Watchdog": args.watchdog_port,
        "Service": args.service_port,
        "Sync": args.sync_port
    }

    for name, port in ports.items():
        if not port_within_range(port):
            parser.error(
                f"{name} port must be within the range 1024 through 65535."
            )

    return args



def log_crash(client, uptime):
    now = datetime.datetime.now()
    with open("crashlog.txt", 'a') as f:
        f.write(f"[str(now.time()] Client {client} timed out after {uptime}s uptime.\n")

if __name__ == "__main__":
    args = environment_initialization()

    watchdog_ip = args.watchdog_ip
    watchdog_port = args.watchdog_port

    service_ip = args.service_ip
    service_port = args.service_port

    sync_ip = args.sync_ip
    sync_port = args.sync_port

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((watchdog_ip, watchdog_port))

    print(f"Watchdog started listening on {watchdog_ip}:{watchdog_port}")
    sock.settimeout(5.5)  # 500 ms 'extra' time for latency

    client = None
    uptime = 0.0
    expected_services = {"Service A is up!", "Service B is up!"}
    last_seen = {}

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            service_message = data.decode("utf-8").strip()
            client = addr

            if service_message not in expected_services:
                print(f"Ignoring unexpected service")
                continue

            last_seen[service_message] = time.monotonic()
            print(f"Heartbeat received from {addr}: {data}")

            uptime += 5.0

        except socket.timeout:
            pass

        now = time.monotonic()

        missing_services = []

        for service in expected_services:
            if service in last_seen:
                time_elapsed = now - last_seen[service]
                if time_elapsed > 5.5:
                    missing_services.append(service)

        if len(missing_services) > 0:
            print("Crash detected!")
            log_crash(client, uptime)
            print("Failover triggered!")
            sock.sendto("Service down!".encode("utf-8"), (sync_ip, sync_port))
            data, addr = sock.recvfrom(1024)
            message_from_sync = data.decode("utf-8").strip()
            if (message_from_sync == "Restoring service!"):
                print("Service restored!")
                expected_services.remove("Service A is up!")
                continue
            else:
                print("Service unable to be restored!")
                break
    
    print("Watchdog ended. Ending client connection...")
