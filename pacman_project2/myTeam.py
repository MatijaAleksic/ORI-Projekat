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

        enemies = [gameState.getAgentState(a) for a in self.getOpponents(gameState)]
        defenders = [a for a in enemies if not a.isPacman and a.getPosition() != None]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]

        safeHouse = [(15, x) for x in range(0, 16)]
        wallsSafeHouse = walls[15]
        safeHouseNoWalls = []
        for i in range(len(wallsSafeHouse)):
          if not wallsSafeHouse[i]:
            safeHouseNoWalls.append(safeHouse[i])

        safeHouseDistances = [self.getMazeDistance((newx, newy), safe) for safe in safeHouseNoWalls]

        if food.count(True) + self.getScore(gameState) != 20 and food.count(True) + self.getScore(gameState) < 19:
          notZero = min(safeHouseDistances)+1
          features["runHome"] = 100 / notZero


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
                    features["run"] = 2
                else:
                    features["eatEnemy"] = 2
            elif disInvador < 3:
                if ghost.scaredTimer == 0:
                    features["run"] = 1
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
            features["eatFood"] = 1.0
        if len(foodList) > 0:
            mazedist = [self.getMazeDistance((newx, newy), food) for food in foodList]
            if min(mazedist) is not None:
                walldimensions = walls.width * walls.height
                features["nearbyFood"] = float(min(mazedist)) / walldimensions

        print(features)
        return features

    def getWeights(self, gameState, action):
        return {'eatFood': 10, 'eatEnemy': 15, 'eatCapsule': 20,
                'nearbyFood': -1.0, "nearbyCapsules": 1.0,
                'run': -10, 'runHome': 100}


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
        util.raiseNotDefined()

    def getWeights(self, gameState, action):
        util.raiseNotDefined()