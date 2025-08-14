#******************************************************************************
# Copyright of this product 2013-2023,
# MACHBASE Corporation(or Inc.) or its subsidiaries.
# All Rights reserved.
#******************************************************************************

import os
import sys
from machbaseAPI.machbaseAPI import machbase

def connect(ip, port):
    db = machbase()
    if db.open(ip, 'SYS', 'MANAGER', port) == 0:
        return db.result()

    if db.execute('select count(*) from m$tables') == 0:
        return db.result()

    result = db.result()

    if db.close() == 0:
        return db.result()

    return result

def print_help():
    help_message = """
Usage: python script_name.py [IP] [PORT]

Options:
  IP     	Specify the IP address of the database server (default: 127.0.0.1)
  PORT   	Specify the port number of the database server (default: 5656)
"""
    print(help_message)

if __name__ == "__main__":
    # Default IP and port settings
    default_ip = "127.0.0.1"
    default_port = 5656

    # Always display help message
    print_help()

    # Parse command-line arguments for IP and port
    if len(sys.argv) > 1 and (sys.argv[1] in ["-h", "--help"]):
        sys.exit(0)

    ip = sys.argv[1] if len(sys.argv) > 1 else default_ip
    port = int(sys.argv[2]) if len(sys.argv) > 2 else default_port

    # Display connection information
    print(f"Connecting to database at IP: {ip}, Port: {port}")

    # Attempt to connect and display result
    print(connect(ip, port))
