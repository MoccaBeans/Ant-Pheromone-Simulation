import random


class loopedCompass():

    directions = [(0,-1),(1,0),(0,1),(-1,0)]

    def __init__(self):
        self.index = 0

    def next(self):
        self.index += 1
        if self.index == len(self.directions):
            self.index = 0
        return self.directions[self.index]

    def prev(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.directions)-1
        return self.directions[self.index]


    def current(self):
        return self.directions[self.index]

    def isLast(self):
        return self.index == len(self.directions) - 1

    #might not be needed check if used
    def setTo(self, item):
        if item in self.directions:
            self.index = self.directions.index(item)
            return True
        return False

    @staticmethod
    def left(self, dir):
        index = self.directions.index(dir)
        if index == 0:
            return self.directions[len(self.directions)-1]
        return self.directions[index-1]

    @staticmethod   
    def right(self, dir):
        index = self.directions.index(dir)
        if index == len(self.directions) - 1:
            return self.directions[0] 
        return self.directions[index+1]

    @staticmethod
    def opposite(self, dir):
        index = self.directions.index(dir) 
        return self.directions[(index+2) % len(self.directions)]
    
    @staticmethod
    def getRandomDirection(self):
        return random.choice(self.directions)
        