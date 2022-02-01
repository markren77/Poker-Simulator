# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 09:29:28 2021

@author: Mark
"""

import socket
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 1234))

print("Welcome to Poker Simulator, each player begins with 10000 chips")
print("\nDisclaimer:\nThe winner of each round will be determined by the dealer(server) MANUALLY")
print("The winner of each hand will get ALL the money in the Pot\n")
print("Please wait for the server to begin the game...")

while True:
    toPrint=s.recv(1024).decode("utf-8")
    if toPrint.endswith("input"):
        print(toPrint[:-5])
        toSend=input()
        s.send(toSend.encode())
    elif toPrint.endswith("exit"):
        print(toPrint[:-4])
        break
    else:
        print(toPrint)
        
s.close()