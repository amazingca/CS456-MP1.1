import json
import os
import signal
import socket
import sys
from datetime import datetime
from random import randint
from threading import Thread

import bcrypt

help = """--passhash:       Encrypt a passphrase

--hash-file:      Location of the file that contains the keypairs for user credentials

--service-ip:        Bind IP for the service
--service-port:      Bind port for the service. Also used as send port for sync-ip

--sync-ip: Send IP for sync

--heartbeart-ip:  IP for the target heartbeat monitor
--heartbeat-port: Port for the target heartbeat monitor"""

hash_file = None

service_ip = None
service_port = None
sync_ip = None

heartbeat_gap = 5
heartbeat_ip = None
heartbeat_port = None

def port_within_range(port):
    return True if port > 1023 and port < 65536 else False

def environment_initialization():
    # Bring global variables into function scope
    global hash_file
    global service_ip
    global service_port
    global sync_ip
    global heartbeat_ip
    global heartbeat_port

    # Populate readable variables with parameters after performing basic verification
    valid_args = True # Stores overall success state for the argument parser
    for arg in sys.argv[1:]:
        if "=" not in arg:
            print(f"Unrecognized runtime argument: {arg}")
            valid_args = False
        match (arg.split("=")):
            case ["--hash-file", hash_file_temp]:
                hash_file = hash_file_temp
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
            case ["--sync-ip", sync_ip_temp]:
                sync_ip = sync_ip_temp
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

def heartbeat_sender():
    # Bring global variable into function scope
    global heartbeat_gap

    heartbeat = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    previous_time = datetime.now()
    while True:
        current_time = datetime.now()
        if (current_time - previous_time).total_seconds() >= heartbeat_gap:
            heartbeat.sendto(bytes("Service A is up!", "utf-8"), (heartbeat_ip, heartbeat_port))
            print("Sent heartbeat!")
            previous_time = current_time

def verify_credentials(username, password):
    stochastic_crasher()
    with open(hash_file, "r") as credentials:
        # Read every line and try each credential pair until we get a match
        while line := credentials.readline():
            line_user, line_hash = line.split(",")
            if line_user != username:
                continue
            if bcrypt.checkpw(password.encode("utf-8"), line_hash.rstrip().encode("utf-8")):
                return b"1"
    return b"0" # We exhausted all credentials, still no match!

def stochastic_crasher():
    if randint(0, 10) == 5:
        os.kill(os.getpid(), signal.SIGSEGV) # Simulate segmentation fault

def generate_credentials(passphrase):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(passphrase.encode("utf-8"), salt)

if __name__ == "__main__":
    # Handle argument count verification
    if len(sys.argv[1:]) == 1:
        if sys.argv[1] == "--help":
            print(help)
            sys.exit(0)
        elif sys.argv[1].startswith("--passhash="):
            print(f'Here is your hashed passphrase: {generate_credentials(sys.argv[1].split("=")[1])}')
            sys.exit(0)
    if len(sys.argv[1:]) != 5:
        print(f"Not enough runtime arguments provided! The following are accepted:\n\n{help}")
        sys.exit(-1)

    if not environment_initialization():
        sys.exit(-2)

    # Start thread for the heartbeat sender
    heartbeat= Thread(target = heartbeat_sender)
    heartbeat.daemon = True # This allows for succinct exiting when the main thread has exited
    heartbeat.start()

    # Listen and respond for auth requests
    listen_sync = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen_sync.bind((service_ip, service_port))
    send_sync = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sync.bind((sync_ip, service_port))
    while True:
        data, addr = listen_sync.recvfrom(1024)
        print(f"Received auth request from {addr}")

        credentials = json.loads(data.decode("utf-8"))
        username = credentials["username"]
        password = credentials["password"]
        response =  verify_credentials(username, password)

        send_sync.sendto(response, addr)
