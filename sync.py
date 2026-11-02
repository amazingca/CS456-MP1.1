from datetime import datetime
from random import randint
from threading import Thread

from flask import Flask, Response, request

app = Flask(__name__)

import base64
import json
import os
import signal
import socket
import sys

help = """--host-ip: ip sync runs on
--host-port: port sync runs on
--primary-ip: ip of primary service
--primary-port: port to send on primary-ip and listen on sync-ip
--secondary-ip: ip of secondary service
--secondary-port: port to send on secondary-ip and listen on sync-ip
--monitor-port: listening port on sync-ip for monitor
"""
host_ip = None
host_port = None
primary_ip = None
primary_port = None
secondary_ip = None
secondary_port = None
monitor_port = None

def port_within_range(port):
    return True if port > 1023 and port < 65536 else False

def environment_initialization():
    # Bring global variables into function scope
    global host_ip
    global host_port
    global primary_ip
    global primary_port
    global secondary_ip
    global secondary_port
    global monitor_port

    # Populate readable variables with parameters after performing basic verification
    valid_args = True # Stores overall success state for the argument parser
    for arg in sys.argv[1:]:
        if "=" not in arg:
            print(f"Unrecognized runtime argument: {arg}")
            valid_args = False
        match (arg.split("=")):
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
            case ["--primary-ip", primary_ip_temp]:
                primary_ip = primary_ip_temp
            case ["--primary-port", primary_port_temp]:
                try:
                    if not port_within_range(int(primary_port_temp)):
                        print("Primary port not within the range 1024 through 65535.")
                        valid_args = False
                    primary_port = int(primary_port_temp)
                except ValueError:
                    print("Primary port provided was not an integer.")
                    valid_args = False
            case ["--secondary-ip", secondary_ip_temp]:
                secondary_ip = secondary_ip_temp
            case ["--secondary-port", secondary_port_temp]:
                try:
                    if not port_within_range(int(secondary_port_temp)):
                        print("Secondary port not within the range 1024 through 65535.")
                        valid_args = False
                    secondary_port = int(secondary_port_temp)
                except ValueError:
                    print("Secondary port provided was not an integer.")
                    valid_args = False
            case ["--monitor-port", monitor_port_temp]:
                try:
                    if not port_within_range(int(monitor_port_temp)):
                        print("Monitor port not within the range 1024 through 65535.")
                        valid_args = False
                    monitor_port = int(monitor_port_temp)
                except ValueError:
                    print("Monitor port provided was not an integer.")
                    valid_args = False
            case [unknown, _]:
                print(f"Unrecognized runtime argument: {unknown}")
                valid_args = False
    return True if valid_args else False

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

def verify_credentials(user, passwd):
    send_creds = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_creds.bind((primary_ip, primary_port))
    print("Sending credentials to primary service for verification.")
    credentials = {
        "username": user,
        "password": passwd
    }
    message = json.dumps(credentials).encode("utf-8")
    send_creds.sendto(message, (primary_ip, primary_port))

    listen_creds = socket.socket(socket.AF_INET, socket.SOCK_DRGRAM)
    listen_creds.bind((host_ip, primary_port))
    waiting = True
    while(waiting):
          response, addr = listen_creds.recvfrom(1024)
          print("Authentication response returned from service.")
          waiting = False

    status = int(response.decode())
    if status == 1:
        return True
    return False


def monitor_listener():
    # TODO: start on another thread before running webserver

if __name__ == "__main__":
    # Handle argument count verification
    if len(sys.argv[1:]) == 1:
        if sys.argv[1] == "--help":
            print(help)
            sys.exit(0)
    if len(sys.argv[1:]) != 5:
        print(f"Not enough runtime arguments provided! The following are accepted:\n\n{help}")
        sys.exit(-1)

    if not environment_initialization():
        sys.exit(-2)

    # Start flask server with target variables
    app.run(host=host_ip, port=host_port)
