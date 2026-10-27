from datetime import datetime
from flask import Flask, request, Response
from random import randint
from threading import Thread

app = Flask(__name__)

import base64
import bcrypt
import os
import signal
import socket
import sys

help = """--passhash:       Encrypt a passphrase

--hash-file:      Location of the file that contains the keypairs for user credentials

--host-ip:        Bind IP for the service
--host-port:      Bind port for the service

--heartbeart-ip:  IP for the target heartbeat monitor
--heartbeat-port: Port for the target heartbeat monitor"""

hash_file = None

host_ip = None
host_port = None

heartbeat_gap = 5
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
    valid_args = True # Stores overall success state for the argument parser
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

def heartbeat_sender():
    # Bring global variable into function scope
    global heartbeat_gap

    heartbeat = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    stochastic_crasher()
    
    previous_time = datetime.now()
    while True:
        current_time = datetime.now()
        if (current_time - previous_time).total_seconds() >= heartbeat_gap:
            heartbeat.sendto(bytes("Service is up!", "utf-8"), (heartbeat_ip, heartbeat_port))
            print("Sent heartbeat!")
            previous_time = current_time

@app.route("/login", methods=["GET"])
def runtime_server():
    
    # Header does not exist
    if not request.headers.get("Authorization"):
        resp = Response("Please provide your credentials!", status=401)
        resp.headers["WWW-Authenticate"] = "Basic realm=\"Login service\""
        return resp
    # Header without "Basic " beginning
    if not request.headers["Authorization"].startswith("Basic "):
        return "Authorization header does not match format!", 401
    
    credentials_bytes = request.headers["Authorization"].split(" ")[1]
    credentials_plaintext = base64.b64decode(credentials_bytes).decode("ascii")

    # Decoded base64 header does has incorrect number of colon (:) separators
    if credentials_plaintext.count(":") != 1:
        return "Incorrectly encoded Authorization header!", 401

    # Destructure username & password pair from plaintext
    username, password = credentials_plaintext.split(":")
    
    if verify_credentials(username, password):
        print(f"Successfully authenticated user `{username}`")
        
        return f"Successfully authenticated. Welcome, <strong>{username}</strong>!", 200
    else:
        print(f"Improper credentials for username `{username}`")
        return "Incorrect credentials. Please try again!", 401

def stochastic_crasher():
    if randint(0, 20) == 5:
        os.kill(os.getpid(), signal.SIGSEGV) # Simulate segmentation fault

def verify_credentials(username, password):
    with open(hash_file, "r") as credentials:
        # Read every line and try each credential pair until we get a match
        while line := credentials.readline():
            line_user, line_hash = line.split(",")
            if line_user != username:
                continue
            if bcrypt.checkpw(password.encode("utf-8"), line_hash.rstrip().encode("utf-8")):
                return True
    return False # We exhausted all credentials, still no match!

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
    
    # Start flask server with target variables
    app.run(host=host_ip, port=host_port)
