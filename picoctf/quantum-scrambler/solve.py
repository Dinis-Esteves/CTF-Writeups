"""
picoCTF - Quantum Scrambler | Solver

The server scrambles the flag: it merges the hex characters in pairs and
appends copies of the earlier groups as noise. The rev_ functions undo
scramble() and get_flag().

Usage
    python3 solve.py    # reads get_flag.txt (server output) and flag.txt, prints the flag

Author: Dinis Esteves
"""

import sys
import ast

def exit():
  sys.exit(0)

def scramble(L):
  A = L
  i = 2
  while (i < len(A)):
    if(i == 2):
#      print(len(A))
#      print("first: ", A)
      A[i-2] += A.pop(i-1)
#      print(len(A))
#      print("second: ", A)
      A[i-1].append(A[:i-2])
#      print(len(A))
#      print("third: ", A)
    i += 1
    
  return L

def rev_scramble():
  # cyphered output from server stored in a file
  secret = open('get_flag.txt', 'r').read()
  secret_list = ast.literal_eval(secret)
  i = len(secret_list) - 1
  original_list = secret_list

  while i != 2:
#    print("=================")
#    print(original_list)
    original_list[i-1].pop()
#    print("=================")
#    print(original_list)
    temp = original_list[i-2].pop()
    original_list.insert(i-1, [temp,])
    i -= 1

  original_list[1].pop() 
  temp = original_list[0].pop()
  original_list.insert(1, [temp,])

  return original_list


def get_flag():
  flag = open('flag.txt', 'r').read()
  flag = flag.strip()
  hex_flag = []
  for c in flag:
    hex_flag.append([str(hex(ord(c)))])

  return hex_flag

def rev_flag(my_list):
  original_flag = str()
  for c in my_list:
    original_flag += chr(int(c[0],16))
  return original_flag

def main():
  #flag = get_flag()
  #print(flag)
  #cypher = scramble(flag)
  #print(cypher)
  uncyphered = rev_scramble()
  original_flag = rev_flag(uncyphered)
  print(original_flag)

if __name__ == '__main__':
  main()
