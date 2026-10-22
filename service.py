import sys

help = """--hash-file:      Location of the file that contains the keypairs for user credentials

--host-ip:        Bind IP for the service
--host-port:      Bind port for the service

--heartbeart-ip:  IP for the target heartbeat monitor
--heartbeat-port: Port for the target heartbeat monitor"""

hash_file = None

host_ip = None
host_port = None

heartbeat_ip = None
heartbeat_port = None

def port_within_range(port):
    return True if port > 1023 and port < 65536 else False

def environment_initialization():
    # Bring global variables into function scope
    global hash_file
    global host_ip
    global host_port
    global heartbeat_ip
    global heartbeat_port

    # Populate readable variables with parameters after performing basic verification
    valid_args = True # Return false if this flag turns to be False
    for arg in sys.argv[1:]:
        if "=" not in arg:
            print(f"Unrecognized runtime argument: {arg}")
            valid_args = False
        match (arg.split("=")):
            case ["--hash-file", hash_file_temp]:
                hash_file = hash_file_temp
            case ["--host-ip", host_ip_temp]:
                host_ip = host_ip_temp
            case ["--host-port", host_port_temp]:
                try:
                    if not port_within_range(int(host_port_temp)):
                        print("Host port not within the range 1024 through 65535.")
                        valid_args = False
                    host_port = int(host_port_temp)
                except ValueError:
                    print("Host port provided was not an integer.")
                    valid_args = False
            case ["--heartbeat-ip", heartbeat_ip_temp]:
                heartbeat_ip = heartbeat_ip_temp
            case ["--heartbeat-port", heartbeat_port_temp]:
                try:
                    if not port_within_range(int(heartbeat_port_temp)):
                        print("Heartbeat port not within the range 1024 through 65535.")
                        valid_args = False
                    heartbeat_port = int(heartbeat_port_temp)
                except ValueError:
                    print("Heartbeat port provided was not an integer.")
                    valid_args = False
            case [unknown, _]:
                print(f"Unrecognized runtime argument: {unknown}")
                valid_args = False
    return True if valid_args else False

def runtime_server():
    pass # TODO 

if __name__ == "__main__":
    # Handle argument count verification
    if len(sys.argv[1:]) == 1 and sys.argv[1] == "--help":
        print(help)
        sys.exit(0)
    if len(sys.argv[1:]) != 5:
        print(f"Not enough runtime arguments provided! The following are accepted:\n\n{help}")
        sys.exit(-1)

    if not environment_initialization():
        sys.exit(-2)

    runtime_server()
