# Silent Stream (picoCTF)

**Category:** Reverse Engineering

## Challenge

> We recovered a suspicious packet capture file that seems to contain a
> transferred file. The sender was kind enough to also share the script they
> used to encode and send it. Can you reconstruct the original file?

The challenge gives two files:

- `packets.pcap`: the packet capture.
- `encrypt.py`: the encoder script of the sender.

## Encoder

This is the encoder script of the sender:

```python
import socket

def encode_byte(b, key):

    return (b + key) % 256

def simulate_flag_transfer(filename, key=42):
    print(f"[!] flag transfer for '{filename}' using encoding key = {key}")

    with open(filename, "rb") as f:
        data = f.read()

    print(f"[+] Encoding and sending {len(data)} bytes...")

    for b in data:
        encoded = encode_byte(b, key)
        pass

    print("Transfer complete")

if __name__ == "__main__":
    simulate_flag_transfer("flag.txt")
```

The script adds the key `42` to each byte. Then it applies modulo 256.

## Get the file from the capture

I opened `packets.pcap` in Wireshark. The capture had one TCP stream. I
followed the stream with **Follow > TCP Stream** and set **Show data as** to
**Raw**. Then I saved the transmitted data to a file.

## Decoder

To get the original file, I had to reverse the modulo operation. This was the
difficult part of the challenge.

I wrote a decoder that examines all 256 possible byte values. It keeps each
value `x` where `(x + key) % 256` is equal to the encoded byte:

```python
def decode_byte(byte, key=42):
    possible = [x for x in range(256) if (x + key) % 256 == byte]
    return possible[0]

def flag_decode(filename, key=42):
    with open(filename, "rb") as f:
        data = f.read()

    with open("decoded_stream", "wb") as f:
        for b in data:
            f.write(decode_byte(b, key).to_bytes())
```

I found that the first possible value is sufficient to decode the file.
Addition modulo 256 gives a different result for each byte value. Thus, the
list always has only one value. The function `(byte - key) % 256` gives the
same result.

## Test the decoder

Before I decoded the capture, I made sure that the decoder was correct. I
encoded a known string with the encoder of the sender:

```
abcdefghijklmnoqrstuvwxyz1234567890-{}_#!$
```

Most bytes of the encoded output were not printable, thus the terminal showed
`�` for them. The printable part was `[\]^_`abcZW` and `MKN`. As hex:

```
8b 8c 8d 8e 8f 90 91 92 93 94 95 96 97 98 99 9b 9c 9d 9e 9f a0 a1 a2
a3 a4 5b 5c 5d 5e 5f 60 61 62 63 5a 57 a5 a7 89 4d 4b 4e
```

Then I decoded this output with `decode_byte`. The result was equal to the
initial string. Thus, the decoder was correct.

## Result

I decoded the file from the capture. The output was a JPEG image, and the
image showed the flag.

## Usage

Put `transmitted.file` in the same directory as `solve.py`. Then do this
command:

```sh
python3 solve.py
```

The script writes the decoded image to `decoded_stream`.
