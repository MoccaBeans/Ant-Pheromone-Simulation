
from posixpath import split
import board
import colony
import numpy as np
import os
import time
import copy

np.set_printoptions(threshold=np.inf)
myboard = board.Board(size=32, arrayOfFood=[], hasUnlimitedFood=True)


mycolony = colony.Colony(128,100,myboard, None)
boards = ["testMovingUnlimited1_32_32","testMovingUnlimited2_32_32","testMovingUnlimited3_32_32","testMovingUnlimited4_32_32"]

for t in range(440):
    if t%110==0:
        myboard.loadBoard(boards.pop(0))
    mycolony.move()
    os.system("cls")
    mycolony.displayAntsOnBoard()
    time.sleep(0.3)
    print(" ")
print(myboard.getFoodPheromoneMatrix())
print(mycolony.getFoodCollected())