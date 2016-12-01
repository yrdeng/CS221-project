from game import Directions
import random
from vars import *
import math


def scoreEvaluationFunction(currentGameState, currentAction=None):
    enemyPos = currentGameState.getEnemyPositions()
    projPos = currentGameState.getProjPositions()
    pos = currentGameState.getPlayerPosition()
    missile = currentGameState.getLastMissile()
    enemies = currentGameState.getEnemies()
    
    # mislePos = currentGameState.getMissilePositions()
    
    def getManhattanDistance(pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def getSquaredDistance(pos1, pos2):
        return (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2

    def checkEMCollide(pos1, pos2):
        # pos1 is enemy, pos2 is missile
        if pos1[0] <= pos2[0]:
            xCollide = pos2[0] - pos1[0] < ENEMY_WIDTH
        else:
            xCollide = pos1[0] - pos2[0] < MISSILE_WIDTH
        if pos1[1] <= pos2[1]:
            yCollide = pos2[1] - pos1[1] < ENEMY_HEIGHT
        else:
            yCollide = pos1[1] - pos2[1] < MISSILE_HEIGHT
        return xCollide and yCollide

    enemyPosDiff = [getSquaredDistance(pos, enemy) for enemy in enemyPos if enemy[1] < pos[1] + PLAYER_SIZE]
    projPosDiff = [getSquaredDistance(pos, proj) for proj in projPos if proj[1] < pos[1] + PLAYER_SIZE]

    # penalty for firing missile
    missileScore = 0
    offset = (24, 2)
    if missile is not None and getManhattanDistance((missile.rect.x, missile.rect.y), pos) == sum(offset):
        missileScore = -2000
        m_x, m_y = missile.rect.x, missile.rect.y
        mv_x, mv_y = 0, missile.speed_y
        for enemy in enemies:
            e_x, e_y = enemy.rect.x, enemy.rect.y
            ev_x, ev_y = enemy.speed_x, enemy.speed_y
            print e_x, e_y, ev_x, ev_y
            for t in range(1, SCREEN_HEIGHT / mv_y):
                newEnemyPos = (e_x + ev_x * t, e_y + ev_y * t)
                newMislePos = (m_x, m_y - mv_y * t)
                if checkEMCollide(newEnemyPos, newMislePos):
                    missileScore = 5000
                    break
    # if missile is not None and abs(missile.rect.y - pos[1]) == 2:
    if missile is not None:
    	m_x, m_y = missile.rect.x, missile.rect.y
        print 'she la!!!', getManhattanDistance((m_x, m_y), pos)

    # calculate the number of threats in a range centered at player's position
    radius = 256
    closestEnemy = 0
    for diff in enemyPosDiff:
        if diff < (2 * radius) ** 2:
            closestEnemy += radius ** 2 / diff
    closestProj = 0
    for diff in projPosDiff:
        if diff < (2 * radius) ** 2:
            closestProj += radius ** 2 / diff
    threatDistScore = -50 * closestEnemy - 100 * closestProj

    # punish the score if flying too wide
    distToCenterScore = -abs(pos[0] - (SCREEN_WIDTH - PLAYER_SIZE) / 2) ** 2 / 32 - abs(
        int(0.5 * SCREEN_HEIGHT) - pos[1]) / 64

    # current game score
    gameScore = currentGameState.getScore()

    # horizontal distances to enemies
    horizontalDist = [abs(pos[0] - enemy[0]) for enemy in enemyPos if enemy[1] < pos[1] + PLAYER_SIZE]
    if len(horizontalDist) == 0:
        horizontalScore = SCREEN_WIDTH
    else:
        horizontalScore = sum(horizontalDist) / 4

    totalScore = [gameScore, threatDistScore, distToCenterScore, horizontalScore]
    # totalScore = [gameScore]
    # print totalScore
    return sum(totalScore)


class Agent:
    def __init__(self, depth='1'):
        self.index = 0
        self.evaluationFunction = scoreEvaluationFunction
        self.depth = int(depth)


class MinimaxAgent(Agent):
    def getAction(self, gameState):
        def recurse(state, index, depth):
            # check if it's the terminal state
            if state.isWin() or state.isLose():
                return state.getScore(), Directions.STOP
            if len(state.getLegalActions(index)) == 0 or depth == 0:
                return self.evaluationFunction(state), Directions.STOP

            nextIndex = (index + 1) % state.getNumAgents()
            nextDepth = depth - 1 if nextIndex == state.getNumAgents() - 1 else depth

            legalActions = state.getLegalActions(index)
            choices = []
            for legalAction in legalActions:
                choices.append(
                    (recurse(state.generateSuccessor(index, legalAction), nextIndex, nextDepth)[0], legalAction))
                # return max value if it's agent otherwise min if it's opponent
            chosenValue = max(choices) if index == 0 else min(choices)
            indices = [i for i in range(len(choices)) if choices[i][0] == chosenValue[0]]
            chosenIndex = random.choice(indices)  # Pick randomly among max
            action = legalActions[chosenIndex]
            return chosenValue[0], action

        value, action = recurse(gameState, self.index, self.depth)
        return action


class AlphaBetaAgent(Agent):
    def getAction(self, gameState):
        def recurse(state, index, depth, lowerBound, upperBound):
            # check if it's the terminal state
            if state.isWin() or state.isLose():
                return state.getScore(), Directions.STOP
            if len(state.getLegalActions(index)) == 0 or depth == 0:
                return self.evaluationFunction(state), Directions.STOP

            nextIndex = (index + 1) % state.getNumAgents()
            nextDepth = depth - 1 if nextIndex == state.getNumAgents() - 1 else depth

            legalActions = state.getLegalActions(index)
            choices = []
            for legalAction in legalActions:
                value, _ = recurse(state.generateSuccessor(index, legalAction), nextIndex, nextDepth, lowerBound,
                                   upperBound)
                choices.append((value, legalAction))
                if index == 0:
                    lowerBound = max(value, lowerBound)
                else:
                    upperBound = min(value, upperBound)
                if lowerBound > upperBound:
                    break
            # return max value if it's agent otherwise min if it's opponent
            chosenValue = max(choices) if index == 0 else min(choices)
            indices = [i for i in range(len(choices)) if choices[i][0] == chosenValue[0]]
            chosenIndex = random.choice(indices)  # Pick randomly among max
            action = legalActions[chosenIndex]
            return chosenValue[0], action

        value, action = recurse(gameState, self.index, self.depth, -INF, INF)
        return action


class ExpectimaxAgent(Agent):
    def getAction(self, gameState):
        def recurse(state, index, depth):
            # check if it's the terminal state
            if state.isWin() or state.isLose():
                return state.getScore(), Directions.STOP
            if len(state.getLegalActions(index)) == 0 or depth == 0:
                if index == 0:
                    return self.evaluationFunction(state), Directions.STOP
                else:
                    return state.getScore(), Directions.STOP

            nextIndex = (index + 1) % state.getNumAgents()
            nextDepth = depth - 1 if nextIndex == state.getNumAgents() - 1 else depth
            # compute the recursion
            values = []
            choices = []
            legalActions = state.getLegalActions(index)
            for legalAction in legalActions:
                value = recurse(state.generateSuccessor(index, legalAction), nextIndex, nextDepth)[0]
                choices.append((value, legalAction))
                values.append(value)
            maxValue = max(choices)[0]
            newChoices = [choice for choice in choices if choice[0] == maxValue]
            mean = sum(values) / len(values)
            return (mean, random.choice(legalActions)) if index != 0 else (maxValue, random.choice(newChoices)[1])

        value, action = recurse(gameState, self.index, self.depth)
        return action
