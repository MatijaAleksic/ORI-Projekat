# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from pacman_project2.captureAgents import CaptureAgent
import random, time
from pacman_project2 import util
from pacman_project2 import game
from pacman_project2.util import nearestPoint
from pacman_project2.game import Directions, Actions


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='OffensiveAgent', second='DefensiveAgent'):
    """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

    # The following line is an example only; feel free to change it.
    return [eval(first)(firstIndex), eval(second)(secondIndex)]


##########
# Agents #
##########

class OffensiveAgent(CaptureAgent):

    def registerInitialState(self, gameState):
        self.observationHistory = []
        self.start = gameState.getAgentPosition(self.index)
        CaptureAgent.registerInitialState(self, gameState)

    def getSuccessor(self, gameState, action):
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != util.nearestPoint(pos):
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def chooseAction(self, gameState):
        #self.score = self.getScore()
        actions = gameState.getLegalActions(self.index)
        values = [self.evaluate(gameState, a) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        return random.choice(bestActions)

    def evaluate(self, gameState, action):
        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)
        # print(features)
        # print(weights)
        #print(features * weights)
        return features * weights

    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        food = self.getFood(gameState)
        capsules = self.getCapsules(gameState)
        foodList = food.asList()
        walls = gameState.getWalls()
        x, y = gameState.getAgentState(self.index).getPosition()
        vx, vy = Actions.directionToVector(action)
        newx = int(x + vx)
        newy = int(y + vy)


        safeHouse = [(15, x) for x in range(0, 16)]
        wallsSafeHouse = walls[15]
        safeHouseNoWalls = []
        for i in range(len(wallsSafeHouse)):
            if not wallsSafeHouse[i]:
                safeHouseNoWalls.append(safeHouse[i])
        safeHouseDistances = [self.getMazeDistance((newx, newy), safe) for safe in safeHouseNoWalls]

        enemies = [gameState.getAgentState(a) for a in self.getOpponents(gameState)]
        defenders = [a for a in enemies if not a.isPacman and a.getPosition() != None]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]

        # ako stane
        if action == Directions.STOP:
            features['stop'] = 1

        # funkcija za invadere
        for ghost in invaders:
            ghostpos = ghost.getPosition()
            disInvador = self.getMazeDistance((newx, newy), ghost.getPosition())
            if (newx, newy) == ghostpos:
                if gameState.getAgentState(self.index).scaredTimer == 0:
                    features["eatEnemy"] = 2
                else:
                    features["run"] = 2
            elif disInvador < 3:
                if gameState.getAgentState(self.index).scaredTimer == 0:
                    features["eatEnemy"] = 1
                else:
                    features["run"] = 1

        # funkcija za defendere
        for ghost in defenders:
            ghostpos = ghost.getPosition()
            disInvador = self.getMazeDistance((newx, newy), ghost.getPosition())
            if (newx, newy) == ghostpos:
                if ghost.scaredTimer == 0:
                    dist = self.getMazeDistance((newx, newy), ghost.getPosition()) + 1
                    features["run"] = 75 / dist
                else:
                    features["eatEnemy"] = 2
            elif disInvador < 3:
                if ghost.scaredTimer == 0:
                    dist = self.getMazeDistance((newx, newy), ghost.getPosition()) + 1
                    features["run"] = 75 / dist
                else:
                    features["eatEnemy"] = 1

        # funkcija kapsula
        for cx, cy in capsules:
            mazedist = self.getMazeDistance((newx, newy), (cx, cy))
            walldimensions = walls.width * walls.height
            if int(mazedist) < 4:
                features["nearbyCapsules"] = float(mazedist) / walldimensions * 10
            if newx == cx and newy == cy and successor.getAgentState(self.index).isPacman:
                features["eatCapsule"] = 1

        #funkcija za hranu
        if food[newx][newy]:
            features["eatFood"] = 1
        if len(foodList) > 0:
            mazedist = [self.getMazeDistance((newx, newy), food) for food in foodList]
            if min(mazedist) is not None:
                walldimensions = walls.width * walls.height
                features["nearbyFood"] = float(min(mazedist)) / walldimensions

        # kada sakupi hranu da se vrati
        if food.count(True) + self.getScore(gameState) != 20 and food.count(True) + self.getScore(gameState) < 19:
            ghostdist = [self.getMazeDistance((newx, newy), ghost.getPosition()) for ghost in defenders]
            if(min(ghostdist) < 15):
                notZero = min(safeHouseDistances) + 1
                features["runHome"] = 100 / notZero

        return features

    def getWeights(self, gameState, action):
        return {'eatFood': 10, 'eatEnemy': 15, 'eatCapsule': 20,
                'nearbyFood': -1.0, "nearbyCapsules": 1.0,
                'run': -100, 'runHome': 80, 'stop' : -1000}


class DefensiveAgent(CaptureAgent):

    def registerInitialState(self, gameState):
        self.observationHistory = []
        self.start = gameState.getAgentPosition(self.index)
        CaptureAgent.registerInitialState(self, gameState)

    def getSuccessor(self, gameState, action):
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != util.nearestPoint(pos):
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def evaluate(self, gameState, action):
        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)
        return features * weights

    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        values = [self.evaluate(gameState, a) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        return random.choice(bestActions)

    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()
        walls = gameState.getWalls()
        food = self.getFood(gameState)
        foodList = food.asList()

        enemies = [gameState.getAgentState(a) for a in self.getOpponents(gameState)]
        defenders = [a for a in enemies if not a.isPacman and a.getPosition() != None]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]

        x, y = gameState.getAgentState(self.index).getPosition()
        vx, vy = Actions.directionToVector(action)
        newx = int(x + vx)
        newy = int(y + vy)
        teamNums = self.getTeam(gameState)

        features['numInvaders'] = len(invaders)

        #ako stane
        if action == Directions.STOP: features['stop'] = 1

        #ako ga tezine nameste da ide u korak u nazad
        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
        if action == rev: features['reverse'] = 1

        features['stayApart'] = self.getMazeDistance(gameState.getAgentPosition(teamNums[0]),
                                                     gameState.getAgentPosition(teamNums[1]))

        # ima invadera
        if len(invaders) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            features['invaderDistance'] = min(dists)
            if (successor.getAgentState(self.index).scaredTimer > 0):
                features['numInvaders'] = 0
                if (features['invaderDistance'] <= 3):
                    features['invaderDistance'] = 3

        #nema invadera
        if len(invaders) == 0:
            if successor.getScore() != 0:
                features['eatFood'] = min([self.getMazeDistance(myPos, food) for food in self.getFood(successor).asList()])


            if food[newx][newy]:
                features["eatFood"] = 1
            if len(foodList) > 0:
                mazedist = [self.getMazeDistance((newx, newy), food) for food in foodList]
                if min(mazedist) is not None:
                    walldimensions = walls.width * walls.height
                    features["nearbyFood"] = float(min(mazedist)) / walldimensions

            newLocation = (newx, newy)
            disInvador = min([self.getMazeDistance(newLocation, ghost.getPosition()) for ghost in defenders]) + 1
            if disInvador < 3:
                    features["run"] = 1/disInvador

        return features

    def getWeights(self, gameState, action):
        return {'numInvaders': -40000, 'invaderDistance': -1800, 'stop': -400, 'reverse': -250,
                'stayApart': 10, 'eatFood': 50, 'nearbyFood': -100, 'runHome': 80, 'run': 250}
