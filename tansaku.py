import random
from time import sleep

inf = float('Infinity')

num = ""

digit = 0

def isInf():
  return str(inf - eval(num + ".0")) == "inf"

def decreaseCurrentDigit():
  global num
  print(num)
  sleep(0.5)
  num = num[0:digit] + str(int(num[digit]) - 1) + num[(digit + 1):]

def increaseCurrentDigit():
  global num
  print(num)
  sleep(0.5)
  num = num[0:digit] + str(int(num[digit]) + 1) + num[(digit + 1):]

def setCurrentDigit(d):
  global num
  print(num)
  sleep(0.5)
  num = num[0:digit] + d + num[(digit + 1):]

while isInf():
  num += random.choice("0123456789")

while True:
  if digit == len(num):
    break
  
  while (not isInf()) and num[digit] != "0":
    decreaseCurrentDigit()
  
  while isInf() and num[digit] != "9":
    increaseCurrentDigit()
  
  if (not isInf()) and num[digit] == "0":
    digit -= 1
    decreaseCurrentDigit()
    digit += 1
    setCurrentDigit("9")
    continue
  
  if isInf() and num[digit] == "9":
    digit -= 1
    increaseCurrentDigit()
    digit += 1
    setCurrentDigit("0")
    continue
  
  print(num)
  sleep(0.5)
  digit += 1

