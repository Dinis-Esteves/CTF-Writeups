"""
picoCTF - weirdSnake | Solver

The challenge gives a Python 3.12 dis listing of a repeating-key XOR.
This is the hand translation of that bytecode back to Python.

Usage
    python3 solve.py    # prints the flag

Author: Dinis Esteves
"""

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



