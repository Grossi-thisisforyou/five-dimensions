#!/usr/bin/env python3
"""Send cues from the Raspberry Pi to Isadora on the Mac, over Wi-Fi, as OSC.

First step of the Pi <-> Mac link. Standard library only: nothing to install.

    python3 hello_isadora.py MAC_ADDRESS          # sends cue 1, 2, 3, 4, ... every 2 s
    python3 hello_isadora.py MAC_ADDRESS --port 1234

MAC_ADDRESS is the Mac's IP (e.g. 192.168.1.20) or its name (e.g. my-mac.local).
In Isadora, an OSC Listener on the same port receives /fivedim/cue with one number.
Stop with Ctrl+C.
"""
import argparse
import socket
import struct
import time


def osc_pad(b: bytes) -> bytes:
    """OSC strings end with a null byte and are padded to a multiple of 4."""
    b += b"\0"
    return b + b"\0" * (-len(b) % 4)


def osc_message(address: str, value: int) -> bytes:
    """One OSC message carrying a single 32-bit integer."""
    return osc_pad(address.encode()) + osc_pad(b",i") + struct.pack(">i", value)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("host", help="the Mac's IP address or name.local")
    ap.add_argument("--port", type=int, default=1234, help="Isadora's OSC port (default 1234)")
    ap.add_argument("--address", default="/fivedim/cue", help="OSC address (default /fivedim/cue)")
    ap.add_argument("--every", type=float, default=2.0, help="seconds between cues (default 2)")
    ap.add_argument("--channels", type=int, default=4, help="cycle through this many cues (default 4)")
    args = ap.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Sending {args.address} to {args.host}:{args.port}. Ctrl+C to stop.")
    cue = 0
    try:
        while True:
            cue = cue % args.channels + 1
            sock.sendto(osc_message(args.address, cue), (args.host, args.port))
            print(f"sent cue {cue}")
            time.sleep(args.every)
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
