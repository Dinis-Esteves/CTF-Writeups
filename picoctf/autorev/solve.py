"""
PicoCTF — AutoRev | Proof of Concept

The server streams 20 ELF binaries over a socket, each as a hex string.
Every binary hardcodes a secret constant and prompts for it. Solving all
20 within 10 seconds per challenge limit yields the flag.

Vulnerability
    The secret is loaded by a fixed instruction:
        movl $<secret>,-0x4(%rbp)   ->   opcode  c7 45 fc <imm32>
    The 32-bit immediate is the answer, readable straight from the bytes.

Exploit (per round)
    recv binary as hex -> bytes.fromhex -> write to ./chal
    objdump -d chal -> regex the movl $0x<imm>,-0x4(%rbp) line
    int(hex, 16) -> sendall the decimal

Usage
    requires: objdump (binutils)
    python3 autorev.py

Author: Dinis Esteves
Date:   2026-11-03
"""

import socket
import re
import socket
import subprocess

SERVER = "SERVER_NAME"
PORT = 12345

def get_chal_answer(data):
    # print(data.decode("utf-8"))
    hex_binary = re.search(r"bytes:\s*([0-9a-fA-F]+)",data.decode("utf-8")).group(1)

    with open("chal", "wb") as f:
        f.write(bytes.fromhex(hex_binary))

    result = subprocess.run(["objdump", "-d", "chal"], capture_output=True, text=True)
    dump = result.stdout

    flag = int(re.search(r"movl   \$0x*([0-9a-fA-F]+),-0x4\(%rbp\)", dump).group(1), 16)
    print(flag)
    return flag

def exploit(hostname, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostname, port))
    s.settimeout(0.3)

    chal = 1
    try:
        while True:
            data_sum = bytes()
            while True:
                try:
                    data = s.recv(2*1024)
                except socket.timeout:
                    break
                if not data:
                    print("Server closed the connection.")
                    return
                data_sum += data

                if chal == 21:
                    print(data_sum.decode("utf-8", errors="replace"), end="")

            print("challange", chal)
            answer = get_chal_answer(data_sum)
            chal += 1

            s.sendall((str(answer) + "\n").encode("utf-8"))
    finally:
        s.close()

if __name__ == "__main__":
    exploit(SERVER, PORT)
