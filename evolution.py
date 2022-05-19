import copy
import board
import colony

from deap import base, creator, tools
from deap.tools import mutation

import random
import numpy as np
import matplotlib.pyplot as plt
import multiprocessing as mp
from itertools import repeat




def evalColony(individual, board, mapNameList,timeToGather):
        foodCollected = []
        if type(mapNameList) == list:
            numberOfMaps = len(mapNameList)
        else:
            numberOfMaps = 1
        for i in range(numberOfRepeats):
            board.reset()
            mapNameListCopy = copy.deepcopy(mapNameList)
            evoColony = colony.Colony(numberOfAnts, timeToGather, board, individual)
            for time in range(timeToGather):
                if time % (timeToGather/numberOfMaps)==0:
                    if type(mapNameListCopy) == list:
                        board.loadBoard(mapNameListCopy.pop(0))
                    else:
                        board.loadBoard(mapNameListCopy)
                evoColony.move()
            foodCollected.append(evoColony.getFoodCollected())
        return sum(foodCollected)/len(foodCollected),

class evolution():

    def __init__(self):
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        self.toolbox = base.Toolbox()
        self.toolbox.register("attr_float", random.uniform, 0, 1.0)
        self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.attr_float, n=indivSize)               
        self.toolbox.register("evaluate", self.calculateFitnesses)
        self.toolbox.register("select", tools.selTournament, tournsize=tournamentSize)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", tools.mutGaussian, mu=0.0, sigma= mutationSigma, indpb=mutationProb)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        self.logbook = tools.Logbook()
        self.stats = self.makeStats()
        self.population = self.toolbox.population(n=populationSize)

    def makeStats(self):
        stats = tools.Statistics(key=lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("std", np.std)
        stats.register("min", np.min)
        stats.register("max", np.max)

        return stats
    
    def calculateFitnesses(self, pop, testBoard,enviromentNames,timeToGather):
        listpop = [list(x) for x in pop]
        pool = mp.Pool(mp.cpu_count()) #makes pool for parallelizing 
        #fitnesses = [self.toolbox.evaluate(indiv, board) for indiv in pop] #this
        #fitnesses = [pool.apply_async(evalColony2,  args = (indiv, copy.deepcopy(board),i)) for i, indiv in enumerate(pop)]
        fitnesses = pool.starmap(evalColony, zip(listpop,repeat(copy.deepcopy(testBoard)),repeat(enviromentNames),repeat(timeToGather)))
        #[pool.apply_async(howmany_within_range2, args=(i, row, 4, 8)) for i, row in enumerate(data)]
        pool.close()
        pool.join()
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit
        print(fitnesses)
        return pop

    def evolve(self, enviromentNames = "sparse_32_32", timeToGather = 100 ,hasUnlimitedFood = True):
        for g in range(numOfGenerations):
            print("-- Generation %i --" % g)

            offspring = self.toolbox.select(self.population, len(self.population))
            offspring = list(map(self.toolbox.clone, offspring))

            for mutant in offspring:
                self.toolbox.mutate(mutant)
                mutant[0] = max(mutant[0],0) #[1.0919493559443605, 0.8231135606996113, 0.15250243573833183, 1.4482476190189137]
                mutant[1] = min(max(mutant[1],0),1) #[0.4964808591660562, 0.9003805775389662, 0.16799955706322411, 0.7358200114550494]
                mutant[2] = mutant[2]
                del mutant.fitness.values

            testBoard = board.Board(32, [], hasUnlimitedFood)
            testBoard.loadBoard("open_32_32")
            offspring = self.calculateFitnesses(offspring,testBoard,enviromentNames,timeToGather)

            self.population[:] = offspring
            record = self.stats.compile(self.population)
            self.logbook.record(gen=g, **record)
    
    def drawFitnessGraph(self,fileName=None):
        if fileName:
            gen, mins, avgs, maxs = self.loadTrainingData(fileName)
        else:
            gen = self.logbook.select("gen")
            mins = self.logbook.select("min")
            maxs = self.logbook.select("max")
            avgs = self.logbook.select("avg")

        plt.rc('axes', labelsize=14)
        plt.rc('xtick', labelsize=14)
        plt.rc('ytick', labelsize=14) 
        plt.rc('legend', fontsize=14)

        fig, ax1 = plt.subplots()
        ax1.set_xlabel("Generation")
        ax1.set_ylabel("Fitness (Food collected)")

        line1 = ax1.plot(gen, mins, label = "minimum")
        line2 = ax1.plot(gen, avgs, label = "average")
        line3 = ax1.plot(gen, maxs, label = "maximum")
        plt.legend(loc="lower right")

        plt.show()

    def saveTrainingData(self, fileName):
        f = open(fileName+".txt", "w")
        f.write(str(self.logbook.select("gen"))+"\n")
        f.write(str(self.logbook.select("min"))+"\n")
        f.write(str(self.logbook.select("avg"))+"\n")
        f.write(str(self.logbook.select("max")))
        f.close()
        print("Saved training data to: "+fileName+".txt")
    
    def saveBestInd(self, fileName):
        f = open(fileName+".txt", "w")
        f.write(str(list(tools.selBest(self.population, 1)[0])))
        f.close()
        print("Saved best individual to: "+fileName+".txt")


    def loadTrainingData(self, fileName):
        f = open(fileName+".txt", "r")
        if f.mode == "r":
            contents = f.read()
        contents = contents.split("\n")
        contents = [results[1:-1].split(",") for results in contents]
        resultsArray = []
        for data in contents:
            resultsArray.append([float(x) for x in data])
        return resultsArray[0], resultsArray[1], resultsArray[2], resultsArray[3]




stationaryLimitedParameters = ("stationaryLimited_32_32", 100, False)
stationaryUnlimitedParameters = ("stationaryUnlimited_32_32", 100, True)
movingUnlimitedParameters = (["movingUnlimited1_32_32","movingUnlimited2_32_32","movingUnlimited3_32_32","movingUnlimited4_32_32"], 400, True)

numberOfAnts = 128
mapSize = 32


indivSize = 3
tournamentSize = 5
numberOfRepeats = 5
mutationProb = 0.3
mutationSigma = 0.2
populationSize = 50
numOfGenerations = 75

if __name__ == '__main__':
    antEvolution3 = evolution()
    print("stationaryUnlimited")
    antEvolution3.evolve(*stationaryUnlimitedParameters)
    antEvolution3.saveBestInd("stationaryUnlimitedBestAgent")
    antEvolution3.saveTrainingData("stationaryUnlimitedTrainingData")
    print(tools.selBest(antEvolution3.population, 1)[0])
    antEvolution4 = evolution()
    print("movingUnlimited")
    antEvolution4.evolve(*movingUnlimitedParameters)
    antEvolution4.saveBestInd("movingUnlimitedBestAgent")
    antEvolution4.saveTrainingData("movingUnlimitedTrainingData")
    print(tools.selBest(antEvolution4.population, 1)[0])
    antEvolution2 = evolution()
    print("stationaryLimited")
    antEvolution2.evolve(*stationaryLimitedParameters)
    antEvolution2.saveBestInd("stationaryLimitedBestAgent")
    antEvolution2.saveTrainingData("stationaryLimitedTrainingData")
    print(tools.selBest(antEvolution2.population, 1)[0])
    antEvolution3.drawFitnessGraph("stationaryUnlimitedTrainingData")
    antEvolution3.drawFitnessGraph("openUnlimitedTrainingData")
    antEvolution3.drawFitnessGraph("movingUnlimitedTrainingData")
