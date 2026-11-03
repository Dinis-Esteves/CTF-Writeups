# AutoRev (picoCTF)

**Category:** Reverse Engineering

## Challenge

The server streams 20 ELF binaries over a socket, each as a hex string. Every
binary hardcodes a secret constant and prompts for it, with 10 seconds to
answer each one. Answer all 20 and the server returns the flag.

## Vulnerability

Each binary loads the secret with the same instruction:

```asm
movl $<secret>,-0x4(%rbp)    ; opcode c7 45 fc <imm32>
```

The 32-bit immediate is the answer. No execution or decompilation needed: it
sits in the bytes.

## Exploit

Per round:

1. Receive the binary as hex, decode with `bytes.fromhex`, write to `./chal`.
2. Run `objdump -d chal` and regex the `movl $0x<imm>,-0x4(%rbp)` line.
3. Convert the immediate to decimal and send it back.

The socket uses a short recv timeout (0.3 s) to detect the end of each prompt,
since the server sends no length prefix.

## Usage

Requires Python 3 and `objdump` (binutils).

```sh
python3 solve.py
```

Set `SERVER` and `PORT` in `solve.py` to your challenge instance.
