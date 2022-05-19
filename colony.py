import enum
from logging import raiseExceptions
import random
import board
from utility import loopedCompass
import numpy as np
import math
import time 

 #make ants a dict with key as replacement for antId 
class Colony():

    def __init__(self, numOfAnts, duration , _board, genome):
        self.timer = 0
        self.numOfAnts = numOfAnts
        self.duration = duration
        self.board = _board
        self.boardSize = self.board.getBoardSize()
        self.ants = []
        self.percentageFirstWave = 0.25
        self.pheromoneDepositAmount = 0.01
        if not genome:
            self.diffusionSigma = 2.407371577842557
            self.evaporationRate = 0.45812730894560266
            self.wonderStrength = -0.5709714858628878
        else:
            self.diffusionSigma = genome[0] 
            self.evaporationRate = genome[1]
            self.wonderStrength = genome[2] 
        
        self.initialAntSpawnAmount = math.floor(self.numOfAnts * self.percentageFirstWave)
        self.timeForSecondSpawn = 20

        self.foodCollected = 0
        self.timer = 0

        self.board.makeUpdateKernel(self.diffusionSigma, self.evaporationRate)

    def spawnAnts(self, numOfAnts):
        nestCoord = self.board.getNestCoord()
        for ant in range(numOfAnts):

            self.ants.append([nestCoord,loopedCompass.loopedCompass.getRandomDirection(loopedCompass.loopedCompass),False,[],[]]) #postion, direction, isCarryingFood

    def move(self):
        self.resetPheromoneUpdate()
        if self.timer == 0:
            self.spawnAnts(self.initialAntSpawnAmount)
        if self.timer == self.timeForSecondSpawn:
            self.spawnAnts(self.numOfAnts-self.initialAntSpawnAmount)
        for antIndex, ant in enumerate(self.ants):
            self.getMove(antIndex, ant)
        self.updatePheromones()
        self.timer += 1
    
    def getMove(self, antIndex, ant):
        if ant[2]:
            return self.moveToNest(antIndex, ant)
        return self.moveToFood(antIndex, ant)

    def getFoodCollected(self):
        return self.foodCollected
    
    def moveToFood(self, antIndex, ant):
        foodCoord = self.board.senseFood(ant[0],ant[1])
        if foodCoord:
            self.pickUpFood(antIndex, foodCoord)
            self.setPosition(antIndex, foodCoord)
            self.flipAnt(antIndex)
        elif self.board.canSenseNest(ant[0],ant[1]):
                self.flipAnt(antIndex)
        else:
            pheromonesAndCoordsLMR = self.board.sensePheromonesAndCoordsLMR(ant[0],ant[1])
            newTile, turn = self.chooseMove(pheromonesAndCoordsLMR)
            if turn:
                self.turnAnt(antIndex, ant, turn)
            self.setPosition(antIndex,newTile)

    def moveToNest(self, antIndex, ant):
        if self.board.canSenseNest(ant[0],ant[1]) or self.isAdjacentToNest(ant):
            self.dropFood(antIndex)
            self.flipAnt(antIndex)
            self.resetHistory(antIndex, ant)
        else:
            newTile, dir = self.getMoveFromHistory(antIndex)
            self.setPosition(antIndex, newTile)
            self.ants[antIndex][1] = dir
            self.depositFoodPheromone(ant[0])

    def isAdjacentToNest(self, ant):
        return self.distance(ant[0], self.board.getNestCoord()) <= 1.5

    def distance(self, coord1, coord2):
        return ((coord1[0]-coord2[0])**2 + (coord1[1]-coord2[1])**2)**0.5

    def resetHistory(self, antIndex, ant):
        self.ants[antIndex][3] = [(ant[0],ant[1])]

    def getMoveFromHistory(self, antIndex):
        nextPos, wrongDir = self.popAntHistory(antIndex)
        nextDir = loopedCompass.loopedCompass.opposite(loopedCompass.loopedCompass, wrongDir)
        return nextPos, nextDir

    def popAntHistory(self, antIndex):
        posDir = self.ants[antIndex][3].pop()
        return posDir[0], posDir[1]

    def dropFood(self, antIndex):
        self.ants[antIndex][2] = False
        self.foodCollected += 1

    def turnAnt(self, antIndex, ant, turn):
        if turn=="right":
            self.turnRight(antIndex, ant)
        elif turn=="left":
            self.turnLeft(antIndex, ant)
        else:
            raise Exception("turn direction -"+turn+"- is not valid")

    def turnRight(self, antIndex, ant):
        self.ants[antIndex][1] = loopedCompass.loopedCompass.right(loopedCompass.loopedCompass, ant[1])

    def turnLeft(self, antIndex, ant):
        self.ants[antIndex][1] = loopedCompass.loopedCompass.left(loopedCompass.loopedCompass, ant[1])

    def resetPheromoneUpdate(self):
        self.pheromoneFoodUpdate = np.zeros((self.boardSize, self.boardSize))

    def updatePheromones(self):
        self.board.updatePheromones(self.pheromoneFoodUpdate)

    def depositFoodPheromone(self, coord):
        self.pheromoneFoodUpdate[coord[1],coord[0]] += self.pheromoneDepositAmount

    def setPosition(self, antIndex, coord):
        if self.board.isInBoard(coord) and not self.board.isWall(coord):
            self.ants[antIndex][0] = coord
            if not self.isCarryingFood(antIndex):
                self.addToHistory(antIndex, coord)
        else: 
            self.flipAnt(antIndex)

    def addToHistory(self, antIndex, coord):
        self.ants[antIndex][3].append((coord,self.ants[antIndex][1]))
        self.ants[antIndex][4].append((coord,self.ants[antIndex][1]))

    def isCarryingFood(self, antIndex):
        return self.ants[antIndex][2]
    
    def flipAnt(self, antIndex):
        self.ants[antIndex][1] = (self.ants[antIndex][1][0]*-1,self.ants[antIndex][1][1]*-1)

    def pickUpFood(self, antIndex, foodCoord):
        if self.ants[antIndex][2]:
            raise Exception("Ant is already carrying food!")
        self.board.collectFood(foodCoord)
        self.ants[antIndex][2] = True

    def chooseMove(self, pheromonesAndCoordsLMR):
        pheromones = [pheromonesAndCoordsLMR[x][0] for x in range(len(pheromonesAndCoordsLMR))]
        normPheromones = self.normalise(pheromones)
        moveProbs = self.normalise([normPheromones[i]*self.wonderStrength + [0.15,0.7,0.15][i] for i in range(3)])
        randomSpin = random.random()
        for moveIndex, move in enumerate(moveProbs):
            randomSpin -= move
            if randomSpin<=0:
                return pheromonesAndCoordsLMR[moveIndex][1], ["left",None,"right"][moveIndex]
        return pheromonesAndCoordsLMR[2][1], "right"

    def normalise(self, values):
        valuesSum = sum(values)
        if valuesSum != 0:
            return [x/sum(values) for x in values]
        return [1 for x in values]



    def displayAntsOnBoard(self):
        self.board.displayWithAnts([(ant[0],ant[1],ant[2]) for ant in self.ants])