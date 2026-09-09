#!/usr/bin/env python3
"""Minimal RCON client for the MC server console.

Usage: mc-rcon.py <command>   (e.g. mc-rcon.py "chunky status")

Reads RCON_PORT / RCON_PW from rcon.conf next to this script.
Password never appears on the command line.
"""
import os
import socket
import struct
import sys

CFG = {}
_conf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rcon.conf")
for line in open(_conf):
    line = line.strip()
    if "=" in line:
        k, v = line.split("=", 1)
        CFG[k.strip()] = v.strip()
HOST = "127.0.0.1"
PORT = int(CFG.get("RCON_PORT", "25575"))
PW = CFG["RCON_PW"]


def pkt(rid, ptype, body):
    data = struct.pack("<ii", rid, ptype) + body.encode() + b"\x00\x00"
    return struct.pack("<i", len(data)) + data


def recv_pkt(s):
    raw = b""
    while len(raw) < 4:
        chunk = s.recv(4 - len(raw))
        if not chunk:
            raise ConnectionError("closed")
        raw += chunk
    ln = struct.unpack("<i", raw)[0]
    data = b""
    while len(data) < ln:
        data += s.recv(ln - len(data))
    rid, ptype = struct.unpack("<ii", data[:8])
    return rid, ptype, data[8:-2].decode(errors="replace")


cmd = " ".join(sys.argv[1:]) or "list"
s = socket.create_connection((HOST, PORT), timeout=8)
s.sendall(pkt(1, 3, PW))
rid, _, _ = recv_pkt(s)
if rid == -1:
    sys.exit("RCON auth failed")
s.sendall(pkt(2, 2, cmd))
_, _, body = recv_pkt(s)
print(body)
s.close()
