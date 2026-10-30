import datetime
import socket
import sys
import time

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

def port_within_range(port):
    return True if port > 1023 and port < 65536 else False

def environment_initialization():
    # Bring global variables into function scope
    global watchdog_ip
    global watchdog_port
    global service_ip
    global service_port

    # Populate readable variables with parameters after performing basic verification
    valid_args = True # Stores overall success state for the argument parser
    for arg in sys.argv[1:]:
        if "=" not in arg:
            print(f"Unrecognized runtime argument: {arg}")
            valid_args = False
        match (arg.split("=")):
            case ["--watchdog-ip", watchdog_ip_temp]:
                watchdog_ip = watchdog_ip_temp
            case ["--watchdog-port", watchdog_port_temp]:
                try:
                    if not port_within_range(int(watchdog_port_temp)):
                        print("Watchdog port not within the range 1024 through 65535.")
                        valid_args = False
                    watchdog_port = int(watchdog_port_temp)
                except ValueError:
                    print("Watchdog port provided was not an integer.")
                    valid_args = False
            case ["--service-ip", service_ip_temp]:
                service_ip = service_ip_temp
            case ["--service-port", service_port_temp]:
                try:
                    if not port_within_range(int(service_port_temp)):
                        print("Service port not within the range 1024 through 65535.")
                        valid_args = False
                    service_port = int(service_port_temp)
                except ValueError:
                    print("Service port provided was not an integer.")
                    valid_args = False
            case [unknown, _]:
                print(f"Unrecognized runtime argument: {unknown}")
                valid_args = False
    return True if valid_args else False

def log_crash(client, uptime):
    now = datetime.datetime.now()
    with open("crashlog.txt", 'a') as f:
        f.write(f"[str(now.time()] Client {client} timed out after {uptime}s uptime.\n")

if __name__ == "__main__":
    # Handle argument count verification
    if len(sys.argv[1:]) == 1:
        if sys.argv[1] == "--help":
            print(help)
            sys.exit(0)
    if len(sys.argv[1:]) != 4:
        print(f"Not enough runtime arguments provided! The following are accepted:\n\n{help}")
        sys.exit(-1)

    if not environment_initialization():
        sys.exit(-2)


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
                    expected_services.remove(service)

        if len(missing_services) > 0:
            print("Crash detected!")
            log_crash(client, uptime)
            # print("Failover triggered!")
            # sock.sendto(bytes("Service down!", "utf-8"), (sync_ip, sync_port))
            # data, addr = sock.recvfrom(1024)
            # message_from_sync = data.decode("utf-8").strip()
            # if (message_from_sync == "Service restored!"):
            #   print("Service restored!")
            #   continue
            # else:
            #   print("Service unable to be restored!")
            #   break
    
    print("Watchdog ended. Ending client connection...")
