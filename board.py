from utility import loopedCompass
import math
import random
import copy
import numpy as np


class Board():

    def __init__(self,path):
        print("Make file reader!")

    def __init__(self,size=16,arrayOfFood = [20, 20],hasUnlimitedFood = True):
        self.size = size

        self.board = self.makeBlankBoard()
        self.nest = self.addNest()
        if arrayOfFood:
            self.addFood(arrayOfFood)
        self.initialBoard = copy.deepcopy(self.board)
        self.foodPheromones = np.zeros((self.size+4, self.size+4))
        self.hasUnlimitedFood = hasUnlimitedFood
        

    def makeBlankBoard(self):
        board = {}
        for x in range(self.size):
            for y in range(self.size):
                board[(x,y)] = "."
        return board
    
    def addNest(self):
        nest = (math.floor((self.size-1)/2),math.floor((self.size-1)/2))
        self.board[nest] = "N"
        return nest
    
    def reset(self):
        self.board = copy.deepcopy(self.initialBoard)
        self.foodPheromones = np.zeros((self.size+4, self.size+4))
    
    def addFood(self, arrayOfFood):
        if not arrayOfFood:
            raise Exception("arrayOfFood is empty")
        for amountOfFood in arrayOfFood:
            foodSpawnCoord=self.getClearTile()
            self.setToFood(foodSpawnCoord)
            if amountOfFood-1 > 0:
                self.placeFood(self.addCoords(foodSpawnCoord,(-1,1)), amountOfFood-1)

    def placeFood(self, coord, numFood2Place):
        directionsIter = self.makeDirectionsIter()
        maxPlacementLength = 2
        currentLineLength = 0
        while numFood2Place > 0:
            if self.isInBoard(coord) and self.tileIsClear(coord):
                self.setToFood(coord)
                numFood2Place -= 1
            currentLineLength += 1
            coord = self.addCoords(coord, directionsIter.current())
            if currentLineLength == maxPlacementLength:
                currentLineLength = 0
                if directionsIter.isLast(): #move placment coord one layer outwards once all directions have been covered.
                    maxPlacementLength += 2
                    coord = self.addCoords(coord, (-1,1))
                directionsIter.next()
        
    def makeDirectionsIter(self):
        return loopedCompass.loopedCompass()

    def setUnlimitedFood(self, unlimtedFood):
        self.unlimitedFood = unlimtedFood

    def getClearTile(self):
        while True:
            clearTile = self.getRandomCoord()
            if self.tileIsClear(clearTile):
                return clearTile

    def isInBoard(self, coord):
        return coord[0] >= 0 and coord[0] < self.size and coord[1] >= 0 and coord[1] < self.size

    def isFood(self, coord):
        if self.isInBoard(coord):
            return self.board[coord] == "f" or self.board[coord] == "F"

    def isNest(self, coord):
        if self.isInBoard(coord):
            return self.board[coord] == "N" #change this is nest remains a single tile

    def tileIsClear(self, coord):
        return self.board[coord] == "."

    def setToFood(self, coord):
        if not self.tileIsClear(coord):
            raise Exception("Can't place food on non-empty tile")
        self.board[coord] = "f"
        return True
    
    def collectFood(self, pos):
        if self.board[pos] == "f":
            if not self.hasUnlimitedFood:
                self.board[pos] = "."
        elif self.board[pos] == "F":
            self.board[pos] = "f"
        else:
            raise Exception("There is no food to remove at this location")

    def clearAllFood(self):
        for x in range(self.size):
            for y in range(self.size):
                if self.board[(x,y)] == "f":
                    self.board[(x,y)] == "."

    def getRandomCoord(self):
        return (random.randint(0,self.size-1), random.randint(0,self.size-1))

    def getNestCoord(self):
        return self.nest

    def isWall(self, coord):
        return self.board[coord] == "X"
        
    def addCoords(self, coord1, coord2):
        return (coord1[0]+coord2[0],coord1[1]+coord2[1])

    def senseFood(self, pos, dir):
        for each in [loopedCompass.loopedCompass.left(loopedCompass.loopedCompass, dir),(0,0),loopedCompass.loopedCompass.right(loopedCompass.loopedCompass, dir)]:
            offset = self.addCoords(each, dir)
            coord = self.addCoords(offset, pos)
            if self.isFood(coord):
                return coord
        return None

    def canSenseNest(self, pos, dir):
        for each in [loopedCompass.loopedCompass.left(loopedCompass.loopedCompass, dir),(0,0),loopedCompass.loopedCompass.right(loopedCompass.loopedCompass, dir)]:
            offset = self.addCoords(each, dir)
            coord = self.addCoords(offset, pos)
            if self.isNest(coord):
                return True
        return False



    def sensePheromonesAndCoordsLMR(self, pos, dir): #Sense pheromones and coords Left Middle Right, returns (phermone, coord) tuple list
        pheromonesAndCoordsLeftMidRight = []
        for each in [loopedCompass.loopedCompass.left(loopedCompass.loopedCompass, dir),(0,0),loopedCompass.loopedCompass.right(loopedCompass.loopedCompass, dir)]:
            offset = self.addCoords(each, dir)
            coord = self.addCoords(offset, pos)
            pheromonesAndCoordsLeftMidRight.append((self.getFoodPheromone(coord),coord))
        return pheromonesAndCoordsLeftMidRight

    def getFoodPheromone(self,pos):
        if self.isInBoard(pos):
            return self.foodPheromones[pos[1]+2][pos[0]+2]
        return 0
    

    def updateFoodPheromones(self, pheromoneUpdate):
        for update in pheromoneUpdate:
            self.foodPheromones[update[0][1]+2][update[0][0]+2] += update[1]


    def updatePheromones(self, foodPheromoneUpdate):
        self.foodPheromones[2:self.size+2,2:self.size+2] += foodPheromoneUpdate
        self.convolveUpdateKernel()

    
    def convolveUpdateKernel(self):
        diffusedFoodPheromones= np.zeros((self.size+4,self.size+4))
        for x in range(1, self.size+1):
            for y in range(1, self.size+1):
                diffusedFoodPheromones[y][x] = self.updateKernelMul(self.foodPheromones,*(x,y))
        self.foodPheromones = diffusedFoodPheromones
    
    def updateKernelMul(self, pheromones ,rootX, rootY):
        M = pheromones[rootY-1:rootY+2,rootX-1:rootX+2]
        return np.sum(M*self.updateKernel)
    
    def makeUpdateKernel(self, diffusionSigma, evaporationRate): #make update kernel
        gaussFilter = self.GaussianFilter((3,3),diffusionSigma)
        if evaporationRate != 1:
            self.updateKernel = gaussFilter*(1-evaporationRate)
        else:
            self.updateKernel = np.zeros((3,3))

    def GaussianFilter(self, shape, sigma):
        if sigma == 0:
            gaussFilter = np.zeros(shape)
            gaussFilter[int((shape[0]-1)/2)][int((shape[1]-1)/2)] = 1
            return gaussFilter
        xmax,ymax = (shape[0]-1.)/2.,(shape[1]-1.)/2.
        y,x = np.ogrid[-xmax:xmax+1,-ymax:ymax+1]
        gaussFilter = np.exp(-(x**2 + y**2) / (2.*sigma**2))
        filterSum = gaussFilter.sum()
        if filterSum != 0:
            gaussFilter /= filterSum
        return gaussFilter


    def setFoodPheromone(self, coord, pheromoneLevel):
        self.foodPheromones[coord[1]+2][coord[0]+2] = pheromoneLevel

    def getFoodPheromoneMatrix(self):
        return self.foodPheromones

    def display(self, board = None):
        if not board:
            board = self.board
        for y in range(self.size):
            row = ""
            for x in range(self.size):
                row+= board[(x,y)]
            print(row)


    def displayWithAnts(self, antsCoordsAndDir):
        tempBoard = copy.deepcopy(self.board)
        arrowFormat={(0,1):"v",(0,-1):"^",(1,0):">",(-1,0):"<"}
        arrowFormatGreen={(0,1):"\033[1;32;40mv\033[1;37;40m",(0,-1):"\033[1;32;40m^\033[1;37;40m",(1,0):"\033[1;32;40m>\033[1;37;40m",(-1,0):"\033[1;32;40m<\033[1;37;40m"}
        for antCoordAndDir in antsCoordsAndDir:
            if tempBoard[antCoordAndDir[0]] != "N":
                if antCoordAndDir[2]:
                    tempBoard[antCoordAndDir[0]] = arrowFormatGreen[antCoordAndDir[1]]
                else:
                    tempBoard[antCoordAndDir[0]] = arrowFormat[antCoordAndDir[1]]
        self.display(tempBoard)

    def getBoardSize(self):
        return self.size

    def saveBoard(self, name):
        f = open(name+".txt", "w")
        for x in range(self.size):
            line = ""
            for y in range(self.size):
                line+= self.board[(x,y)]
            if x != self.size-1:
                f.write(line+"\n")
            else:
                f.write(line)
        f.close()

    def loadBoard(self, name):
        f = open(name+".txt", "r")
        if f.mode == "r":
            contents = f.read()
        contentLists=contents.split("\n")
        xLen = len(contentLists)
        yLen = len(contentLists[0])
        for y, list in enumerate(contentLists):
            for x, tile in enumerate(list):
                if tile == "N":
                    self.nest=(x,y)
                self.board[(x,y)]=tile
        if xLen != yLen:
            raise Exception("Board must be square, but has dimensions "+str(xLen)+" and "+str(yLen))
        self.size = xLen
        self.initialBoard = copy.deepcopy(self.board)