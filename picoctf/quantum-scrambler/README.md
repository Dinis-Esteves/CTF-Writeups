# Quantum Scrambler (picoCTF)

**Category:** Reverse Engineering

## Challenge

The challenge gives one file and a server:

- `quantum_scrambler.py`: the script that scrambles the flag.
- A server and a port. The server runs the script on the flag and sends the
  scrambled output.

I connected to the server and saved its output to `get_flag.txt`. My task was
to study the script and write functions that reverse it.

## The script

The script does two operations on the flag. First, `get_flag` changes each
character to a hex string in its own list:

```python
def get_flag():
  flag = open('flag.txt', 'r').read()
  flag = flag.strip()
  hex_flag = []
  for c in flag:
    hex_flag.append([str(hex(ord(c)))])

  return hex_flag
```

Then `scramble` changes the structure of the list:

```python
def scramble(L):
  A = L
  i = 2
  while (i < len(A)):
    A[i-2] += A.pop(i-1)
    A[i-1].append(A[:i-2])
    i += 1
  return L
```

## Read the server output

My first problem was the server output. It was a list of lists, but as text
in the terminal. I had to change this text into a real Python list. I
searched the web and found the `ast` module. Its function `ast.literal_eval`
does exactly that:

```python
secret_list = ast.literal_eval(secret)
```

## Study the algorithm

The code is short, but the list changes length in the loop. Thus, it was
difficult to follow in my head. I used a 5-character string, `abcde`, and ran
the script on it. Then I followed the algorithm step by step on paper to
reverse the output.

This is the output for `abcde`:

```python
[['0x61', '0x62'], ['0x63', [], '0x64'], ['0x65', [['0x61', '0x62']]]]
```

In each step, the loop does two operations:

1. `A[i-2] += A.pop(i-1)` removes the next group and adds its characters to
   the group before it. Thus, the characters go into pairs.
2. `A[i-1].append(A[:i-2])` appends a copy of all earlier groups to the next
   group. This copy is noise. It does not hide the characters, it only
   makes the output long and difficult to read.

The result is a list of groups. The first group is `[c0, c1]`. Each other
group is `[c2k, noise, c2k+1]`. The characters stay in their initial order.

## Reverse the scramble

I wrote `rev_scramble` to undo the loop. It reads the server output from
`get_flag.txt` and works from the last group to the first:

```python
def rev_scramble():
  # cyphered output from server stored in a file
  secret = open('get_flag.txt', 'r').read()
  secret_list = ast.literal_eval(secret)
  i = len(secret_list) - 1
  original_list = secret_list

  while i != 2:
    original_list[i-1].pop()
    temp = original_list[i-2].pop()
    original_list.insert(i-1, [temp,])
    i -= 1

  original_list[1].pop()
  temp = original_list[0].pop()
  original_list.insert(1, [temp,])

  return original_list
```

In each step, it removes the noise from a group. Then it takes the second
character from the group before it and puts that character back in its own
list.

Then I wrote `rev_flag` to undo `get_flag`. It changes each hex string back
to a character:

```python
def rev_flag(my_list):
  original_flag = str()
  for c in my_list:
    original_flag += chr(int(c[0],16))
  return original_flag
```

`rev_scramble` gives the correct result when the flag has an even number of
characters. The flag has 32 characters, thus the method was sufficient. With
an odd length, such as `abcde`, it loses one character. In that case, the
last group has only one character before the noise.

## Result

I ran `rev_scramble` on the server output and then `rev_flag`. The script
printed the flag.

## Usage

Put the server output in `get_flag.txt`, in the same directory as
`solve.py`. `main` also scrambles a local `flag.txt`, thus put a test flag in
`flag.txt`. Then do this command:

```sh
python3 solve.py
```

The script prints the flag from `get_flag.txt`.
