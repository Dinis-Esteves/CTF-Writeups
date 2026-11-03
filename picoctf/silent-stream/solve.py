"""
picoCTF - Silent Stream | Decoder

The sender encodes each byte as (b + key) % 256, with key = 42.
This script reverses that operation on the file from the TCP stream.

Usage
    python3 solve.py    # reads transmitted.file, writes decoded_stream

Author: Dinis Esteves
"""


def decode_byte(byte, key=42):
    possible = [x for x in range(256) if (x + key) % 256 == byte]
    return possible[0]


def flag_decode(filename, key=42):
    with open(filename, "rb") as f:
        data = f.read()

    with open("decoded_stream", "wb") as f:
        for b in data:
            f.write(decode_byte(b, key).to_bytes())


if __name__ == "__main__":
    flag_decode("transmitted.file")
