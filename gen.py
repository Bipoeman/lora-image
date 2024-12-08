from random import choice
import string

def GenPasswd2(length=8, chars=string.ascii_letters + string.digits):
    return ''.join([choice(chars) for i in range(length)])

with open("data.txt","ab") as file:
    for i in range(5):
        file.write(GenPasswd2(100000,string.ascii_letters).encode())