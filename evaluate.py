from posixpath import split
import board
import colony
import numpy as np
import os
import time
import copy


# np.set_printoptions(threshold=np.inf)
# myboard = board.Board(size=32, arrayOfFood=[3,3])
# myboard.loadBoard("sparse_32_32")
#myboard.display()
# mycolony = colony.Colony(64,100,myboard, None)
#mycolony.setPosition(1, (0,0))
#mycolony.showAntsOnBoard()


# mapNameList = ["movingSource1_32_32","movingSource2_32_32","movingSource3_32_32","movingSource4_32_32"]
# numberOfMaps = len(mapNameList)
# for t in range(100):
#     if t % (100/numberOfMaps)==0:
#         popped = mapNameList.pop(0)
#         print(popped)
#         myboard.loadBoard(popped)
#     mycolony.move()
#     os.system("cls")
#     mycolony.displayAntsOnBoard()
#     time.sleep(0.3)
#     print(" ")
# print(myboard.getFoodPheromoneMatrix())
# print(mycolony.getFoodCollected())

numberOfAnts = 128


class testPheromone():

    def __init__(self, fileName):
        self.properties = self.loadProperties(fileName)
        self.stationaryLimitedResults = self.testPheromones(["testStationaryLimited_32_32"], 120, False, 50)
        self.stationaryUnlimitedResults = self.testPheromones(["testStationaryUnlimited_32_32"], 80, True, 50)
        self.movingUnlimitedResults = self.testPheromones(["movingUnlimited1_32_32","movingUnlimited2_32_32","movingUnlimited3_32_32","movingUnlimited4_32_32"], 440, True, 50)
        
    def testPheromones(self, mapNameList, timeToGather, hasUnlimitedFood, numberOfRepeats):
        testBoard = board.Board(32, [], hasUnlimitedFood)
        foodCollected = []
        if type(mapNameList) == list:
            numberOfMaps = len(mapNameList)
        else:
            numberOfMaps = 1
        for i in range(numberOfRepeats):
            testBoard.reset()
            mapNameListCopy = copy.deepcopy(mapNameList)
            evoColony = colony.Colony(numberOfAnts, timeToGather, testBoard, self.properties)
            for time in range(timeToGather):
                if time % (timeToGather/numberOfMaps)==0:
                    testBoard.loadBoard(mapNameListCopy.pop(0))
                evoColony.move()
            foodCollected.append(evoColony.getFoodCollected())
        print(foodCollected)
        return foodCollected

    def saveTestData(self, fileName):
        f = open(fileName+".txt", "w")
        f.write("stationaryLimitedTest: "+"\n"+str(self.stationaryLimitedResults)+"\n"+self.getAvgsAndStds(self.stationaryLimitedResults)+"\n")
        f.write("stationaryUnlimitedTest: "+"\n"+str(self.stationaryUnlimitedResults)+"\n"+self.getAvgsAndStds(self.stationaryUnlimitedResults)+"\n")
        f.write("movingUnlimitedTest: "+"\n"+str(self.movingUnlimitedResults)+"\n"+self.getAvgsAndStds(self.movingUnlimitedResults))
        f.close()
        print("Saved training data to: "+fileName+".txt")
    
    def loadProperties(self, fileName):
        f = open(fileName+".txt", "r")
        if f.mode == "r":
            contents = f.read()
        splitContent = contents[1:-1].split(",")
        print([float(x) for x in splitContent])
        return [float(x) for x in splitContent]

    def getAvgsAndStds(self, data):
        return str(sum(data)/len(data))+","+str(np.std(data))



for pheromoneFileName in ["stationaryLimitedBestAgent","stationaryUnlimitedBestAgent","movingUnlimitedBestAgent"]:
    pheromoneTest = testPheromone(pheromoneFileName)
    pheromoneTest.saveTestData(pheromoneFileName[:-9]+"TestData")