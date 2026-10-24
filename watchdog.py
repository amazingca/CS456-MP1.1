import socket
import sys

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


