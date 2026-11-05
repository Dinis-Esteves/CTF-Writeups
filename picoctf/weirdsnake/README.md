# weirdSnake (picoCTF)

**Category:** Reverse Engineering

## Challenge

The challenge gives one file:

- `snake`: a Python bytecode listing.

## What is the file?

I opened `snake` and did not know what it was. I searched the web and found
that it was Python bytecode. My first idea was to use a Python bytecode
decompiler. I found uncompyle6, but it did not decompile the file.

Later, I learned that the file was not compiled bytecode. It was the
plain-text output of the Python `dis` module, a human-readable disassembly
listing. It was not a binary `.pyc` file.

Decompilers like uncompyle6 read the binary format. This format has a header
with a magic number that identifies the Python version. The marshalled code
object follows the header. uncompyle6 read the first two bytes of my file as
the magic number. These bytes were two space characters, `0x2020` (8224 in
decimal). Thus, uncompyle6 stopped with "Unknown magic number". The `file`
command confirmed that `snake` was only ASCII text.

A real `.pyc` file also would not work, because uncompyle6 supports Python
versions up to 3.8 only. I found that the listing came from Python 3.12:

- It starts with `RESUME`. This opcode exists from Python 3.11.
- `CALL` has no `PRECALL` before it. Python 3.12 removed `PRECALL`.
- `PUSH_NULL` comes before the function that the code calls. Python 3.13
  changed this order again.

Thus, there was no shortcut. The challenge makes you read the bytecode by
hand, and I did that.

## The data

The listing starts with a tuple of 40 numbers:

```
21, 60, 43, 11, 86, 25, 38, 49, 33, 3, 0, 0, 57, 32, 108, 23, 48, 4, 9, 70,
7, 110, 36, 8, 108, 7, 49, 10, 4, 86, 43, 104, 126, 13, 87, 67, 60, 43, 12, 78
```

First, I changed the numbers directly to ASCII characters. The result was
not readable. Thus, I knew that the program encoded the data.

## Learn the bytecode

To learn how `dis` shows simple code, I wrote a small program:

```python
data = [1, 2, 3]
key = 5
out = ""
for c in data:
    out += chr(c ^ key)
```

I used `dis` to get its bytecode. When I understood the basic opcodes, I
started on the real file.

## Translate the listing

The first lines were easy. Then I found opcodes that I did not know. I used
the `dis` documentation for Python 3.12 to learn what they do:

| Opcode | What it does |
|---|---|
| `LOAD_FAST_AND_CLEAR` | Saves the outer value of the loop variable of a comprehension. Python 3.12 inlines comprehensions, so it must restore that value after the loop. |
| `LIST_APPEND i` | Adds the top of the stack to the list at stack position `i`. Each comprehension result goes into the new list this way. |
| `LOAD_ATTR` (`NULL\|self + name`) | Loads a method for a call, for example `key_list.extend` or `''.join`. It puts the method and its object on the stack. |
| `PUSH_NULL` | Puts a NULL on the stack before a plain function, for example `len` or `zip`. `CALL` expects a NULL or `self` under the function. |
| `SWAP i` | Swaps the top of the stack with the item at position `i`. The comprehension uses it to keep the saved outer value under the iterator and the list. |

I translated the bytecode to Python one line at a time. After each step, I
compiled my Python with Compiler Explorer (godbolt) for Python 3.12. Then I
compared its bytecode with the listing.

## The trap

Lines 3 and 6 of the listing put a character at the start of `key_str`, not
at the end:

```
  3          14 LOAD_CONST               2 ('_')
             16 LOAD_NAME                1 (key_str)
             18 BINARY_OP                0 (+)
             22 STORE_NAME               1 (key_str)
```

The constant loads first. Thus, the code is `key_str = '_' + key_str`.
Lines 4 and 5 load `key_str` first, so they add `'o'` and `'3'` at the end.

My first translation used the usual order for all four lines, as
`key_str += '_'` and `key_str += 't'`. That gave the key `J_o3t` instead of
`t_Jo3`, and the output was wrong. The order of the operands on the stack is
the order of the operands in the expression. This was the most important
lesson of the challenge.

## What the program does

The program is a repeating-key XOR. It builds the key `t_Jo3` from
characters and changes each character to a number with `ord`. It doubles the
key list until the list is at least as long as the data. Then it XORs each
data number with the key number at the same position. `zip` stops at the
shorter list. At the end, `chr` changes the numbers back to characters.

## Final script

This is my translation of the full listing:

```python
#1:
input_list = [21, 60, 43, 11, 86, 25, 38, 49, 33, 3, 0, 0, 57, 32, 108, 23, 48, 4, 9, 70, 7, 110, 36, 8, 108, 7, 49, 10, 4, 86, 43, 104, 126, 13, 87, 67, 60, 43, 12, 78]

#2:
key_str = 'J'

#3:
key_str = '_' + key_str

#4:
key_str += 'o'

#5:
key_str += '3'

#6:
key_str = 't' + key_str

#9:
key_list = [ord(char) for char in key_str]

#11/12/11:
while len(key_list) < len(input_list):
    key_list.extend(key_list)

#15:
result = [a^b for a,b in zip(key_list, input_list)]

#18:
result_text = ''.join(map(chr, result))

print(result_text)
```

The comments are the line numbers in the listing. The original program does
not print `result_text`. I added `print` to see the result.

<details>
<summary>Full <code>snake</code> listing</summary>

```
  0           0 RESUME                   0

  1           2 BUILD_LIST               0
              4 LOAD_CONST               0 ((21, 60, 43, 11, 86, 25, 38, 49, 33, 3, 0, 0, 57, 32, 108, 23, 48, 4, 9, 70, 7, 110, 36, 8, 108, 7, 49, 10, 4, 86, 43, 104, 126, 13, 87, 67, 60, 43, 12, 78))
              6 LIST_EXTEND              1
              8 STORE_NAME               0 (input_list)

  2          10 LOAD_CONST               1 ('J')
             12 STORE_NAME               1 (key_str)

  3          14 LOAD_CONST               2 ('_')
             16 LOAD_NAME                1 (key_str)
             18 BINARY_OP                0 (+)
             22 STORE_NAME               1 (key_str)

  4          24 LOAD_NAME                1 (key_str)
             26 LOAD_CONST               3 ('o')
             28 BINARY_OP                0 (+)
             32 STORE_NAME               1 (key_str)

  5          34 LOAD_NAME                1 (key_str)
             36 LOAD_CONST               4 ('3')
             38 BINARY_OP                0 (+)
             42 STORE_NAME               1 (key_str)

  6          44 LOAD_CONST               5 ('t')
             46 LOAD_NAME                1 (key_str)
             48 BINARY_OP                0 (+)
             52 STORE_NAME               1 (key_str)

  9          54 LOAD_NAME                1 (key_str)
             56 GET_ITER
             58 LOAD_FAST_AND_CLEAR      0 (char)
             60 SWAP                     2
             62 BUILD_LIST               0
             64 SWAP                     2
        >>   66 FOR_ITER                10 (to 90)
             70 STORE_FAST               0 (char)
             72 PUSH_NULL
             74 LOAD_NAME                2 (ord)
             76 LOAD_FAST                0 (char)
             78 CALL                     1
             86 LIST_APPEND              2
             88 JUMP_BACKWARD           12 (to 66)
        >>   90 END_FOR
             92 SWAP                     2
             94 STORE_FAST               0 (char)
             96 STORE_NAME               3 (key_list)

 11          98 PUSH_NULL
            100 LOAD_NAME                4 (len)
            102 LOAD_NAME                3 (key_list)
            104 CALL                     1
            112 PUSH_NULL
            114 LOAD_NAME                4 (len)
            116 LOAD_NAME                0 (input_list)
            118 CALL                     1
            126 COMPARE_OP               2 (<)
            130 POP_JUMP_IF_FALSE       35 (to 202)

 12     >>  132 LOAD_NAME                3 (key_list)
            134 LOAD_ATTR               11 (NULL|self + extend)
            154 LOAD_NAME                3 (key_list)
            156 CALL                     1
            164 POP_TOP

 11         166 PUSH_NULL
            168 LOAD_NAME                4 (len)
            170 LOAD_NAME                    3 (key_list)
            172 CALL                     1
            180 PUSH_NULL
            182 LOAD_NAME                4 (len)
            184 LOAD_NAME                0 (input_list)
            186 CALL                     1
            194 COMPARE_OP               2 (<)
            198 POP_JUMP_IF_FALSE        1 (to 202)
            200 JUMP_BACKWARD           35 (to 132)

 15     >>  202 PUSH_NULL
            204 LOAD_NAME                6 (zip)
            206 LOAD_NAME                0 (input_list)
            208 LOAD_NAME                3 (key_list)
            210 CALL                     2
            218 GET_ITER
            220 LOAD_FAST_AND_CLEAR      1 (a)
            222 LOAD_FAST_AND_CLEAR      2 (b)
            224 SWAP                     3
            226 BUILD_LIST               0
            228 SWAP                     2
        >>  230 FOR_ITER                10 (to 254)
            234 UNPACK_SEQUENCE          2
            238 STORE_FAST               1 (a)
            240 STORE_FAST               2 (b)
            242 LOAD_FAST                1 (a)
            244 LOAD_FAST                2 (b)
            246 BINARY_OP               12 (^)
            250 LIST_APPEND              2
            252 JUMP_BACKWARD           12 (to 230)
        >>  254 END_FOR
            256 SWAP                     3
            258 STORE_FAST               2 (b)
            260 STORE_FAST               1 (a)
            262 STORE_NAME               7 (result)

 18         264 LOAD_CONST               6 ('')
            266 LOAD_ATTR               17 (NULL|self + join)
            286 PUSH_NULL
            288 LOAD_NAME                9 (map)
            290 LOAD_NAME               10 (chr)
            292 LOAD_NAME                7 (result)
            294 CALL                     2
            302 CALL                     1
            310 STORE_NAME              11 (result_text)
            312 RETURN_CONST             7 (None)
        >>  314 SWAP                     2
            316 POP_TOP

  9         318 SWAP                     2
            320 STORE_FAST               0 (char)
            322 RERAISE                  0
        >>  324 SWAP                     2
            326 POP_TOP

 15         328 SWAP                     3
            330 STORE_FAST               2 (b)
            332 STORE_FAST               1 (a)
            334 RERAISE                  0
ExceptionTable:
  62 to 90 -> 314 [2]
  226 to 254 -> 324 [3]
```

</details>

## Result

I ran the final script. It printed the flag.

## Tools and resources

- [`dis` module](https://docs.python.org/3.12/library/dis.html): the Python
  disassembler. This page also lists all Python 3.12 opcodes.
- [Compiler Explorer (godbolt)](https://godbolt.org/): compiles Python and
  shows the bytecode. Set the language to Python and the version to 3.12.
- [uncompyle6](https://github.com/rocky/python-uncompyle6): the decompiler
  that did not work on this file.

## Usage

Do this command:

```sh
python3 solve.py
```

The script prints the flag. It does not read input files.
