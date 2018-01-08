"""
Author - Sanjay Ramachandran

Readme:
- This Python script uses a OS agnostic library psutil to access the memory information.
- Please install psutil using "pip install psutil"
"""

#!/usr/bin/python3
import time
import os
import copy
from heapq import heappush, heappop

try:
    import psutil  # for computing memory usage
except ImportError:  # try to install requests module if not present
    print ("Trying to Install required module: psutil\n")
    os.system('sudo python -m pip install psutil')
import psutil

#All variables are passed by reference in Python
class AStar:
	'This class contains an implementation of the Breadth-First Search algorithm'
	
	def moveBlank(heuristic, node, action, goalTilePos):
		'''
		This function swaps the blank cell and the nearby cell based on the action given in input argument
		It also updates the heuristic function
		It returns a new child node with the new configuration
		'''
		#to retain the original reference to a node, this temporary node is created
		tNode = PuzzleBoardNode(copy.deepcopy(node.puzzleBoard), node, action, XYPos(node.blankPosition.x, node.blankPosition.y), node.moveCost, node.manhattanDistance)
		if(action == 0):
			#Left
			if(tNode.blankPosition.y > 0):				
				tNode.blankPosition.y -= 1
				tNode.moveCost += 1
		elif(action == 1):
			#Right
			if(tNode.blankPosition.y < (len(tNode.puzzleBoard[0]) - 1)):
				tNode.blankPosition.y += 1
				tNode.moveCost += 1
		elif(action == 2):
			#Up
			if(tNode.blankPosition.x > 0):
				tNode.blankPosition.x -= 1
				tNode.moveCost += 1
		elif(action == 3):
			#Down
			if(tNode.blankPosition.x < (len(tNode.puzzleBoard) - 1)):
				tNode.blankPosition.x += 1
				tNode.moveCost += 1

		#if the heuristic used is Manhattan, then update the distance value.
		if(heuristic == 'Manhattan'):
			AStar.updateManhattanDistance(tNode, tNode.puzzleBoard[tNode.blankPosition.x][tNode.blankPosition.y], goalTilePos,
									tNode.blankPosition.x, tNode.blankPosition.y, node.blankPosition.x, node.blankPosition.y )

		#swap the nearby value cell and the blank cell
		tNode.puzzleBoard[node.blankPosition.x][node.blankPosition.y] = tNode.puzzleBoard[tNode.blankPosition.x][tNode.blankPosition.y]
		tNode.puzzleBoard[tNode.blankPosition.x][tNode.blankPosition.y] = -1

		#if the heuristic used is Displaced Tiles, then update the number of tiles displaced.
		if(heuristic == 'DisplacedTiles'):
			AStar.updateDisplacedTiles(tNode, goalTilePos)

		return tNode

	def isNodeInFrontier(tNode, frontierList):
		'''
		This method returns if the given node is present or not in the frontier list
		'''
		return tNode in frontierList

	def traceSolution(solution, tNode):
		'''
		A recursive method to trace the sequence of path from the goal to the root node
		This returns a solution array which is the action sequence
		'''
		if(tNode.parentNode):
			solution.append(tNode.actionTaken)
			AStar.traceSolution(solution, tNode.parentNode)

	def updateDisplacedTiles(node, goalTilePos):
		'''
		This method counts the number of displaced tiles on the board and updates the count in the node
		'''
		for i in range(4):
			for j in range(4):
				if(node.puzzleBoard[i][j] != -1):
					if(goalTilePos[node.puzzleBoard[i][j]][0] != i or goalTilePos[node.puzzleBoard[i][j]][1] != j):
						node.numDisplacedTiles += 1

	def updateManhattanDistance(node, tile, goalTilePos, oldX, oldY, newX, newY):
		'''
		This method updates the Manhattan Distance after each move of a tile and updates the node
		'''
		if(tile != -1):
			oldMDist = abs(goalTilePos[tile][0] - oldX) + abs(goalTilePos[tile][1] - oldY)
			newMDist = abs(goalTilePos[tile][0] - newX) + abs(goalTilePos[tile][1] - newY)
			node.manhattanDistance += (newMDist - oldMDist)

	def calculateManhattanDistance(node, goalTilePos):
		'''
		This method calculates the manhattan distance of the initial configuration of the board
		'''
		for i in range(4):
			for j in range(4):
				if(node.puzzleBoard[i][j] != -1):
					x, y = goalTilePos[node.puzzleBoard[i][j]]
					node.manhattanDistance += abs(x - i) + abs(y - j)


	def aStarDisplTiles(puzzleBoardNode, goalNode, goalTilePos, actions):
		'''
			This method takes the complete initial state of the puzzle board (the root) as the argument. It uses the number of displaced tiles as the heuristics.
			Returns a tuple with the solution array with the sequence of actions to go from the initial state to a goal state and some time/memory statistics. 
		'''
		solution = []
		exploredNodesSet = [] #Explored node list
		frontierList = [] #this is to implement a priority Queue
		heappush(frontierList, (puzzleBoardNode.moveCost + puzzleBoardNode.numDisplacedTiles, puzzleBoardNode)) #Enqueue operation
		time1 = time.time() #start time
		try:
			while(len(frontierList) != 0):
				totalCost, node = heappop(frontierList) #this is the dequeue operation on the FIFO queue
				exploredNodesSet.append(node) #node to be explored now is added to the explored list

				#Goal test
				if(node == goalNode):
					print('Goal Found')
					node.print()
					AStar.traceSolution(solution, node)
					break

				flag = 0

				#Branching point
				for action in actions:
					tNode =  AStar.moveBlank('DisplacedTiles', node, action, goalTilePos) #since its pass by reference, need to maintain the ref to original node

					#Check to remove repeated states
					if((tNode not in exploredNodesSet) and (not AStar.isNodeInFrontier((tNode.moveCost + tNode.numDisplacedTiles, tNode), frontierList))):
						#Goal test
						if(tNode == goalNode):
							print('Goal Found')
							tNode.print()
							AStar.traceSolution(solution, tNode)
							flag = 1
							break
						else:
							heappush(frontierList, (tNode.moveCost + tNode.numDisplacedTiles, tNode)) #add the new node generated to the frontier if its not a list

				if(flag):
					break #exit the while loop if a solution is found

		except MemoryError:
			print('Failure - Ran out of memory!')
		else:
			time2 = time.time()
			runningTime = (time2 - time1) #calculates the elapsed time
			process = psutil.Process(os.getpid())
			pMemoryUsed = process.memory_info().rss/1000000 #This retrieves the physical memory allocated
			vMemoryUsed = process.memory_info().vms/1000000 #This retrieves the virtual memory allocated
			
		return (solution, runningTime, pMemoryUsed, vMemoryUsed)


	def aStarManhattan(puzzleBoardNode, goalNode, goalTilePos, actions):
		'''
			This method takes the complete initial state of the puzzle board (the root) as the argument. It uses the Manhattan Distance as the heuristics.
			Returns a tuple with the solution array with the sequence of actions to go from the initial state to a goal state and some time/memory statistics. 
		'''
		solution = []
		exploredNodesSet = [] #Explored node list
		frontierList = [] #this is to implement a priority Queue
		heappush(frontierList, (puzzleBoardNode.moveCost + puzzleBoardNode.manhattanDistance, puzzleBoardNode)) #Enqueue operation
		time1 = time.time() #start time
		try:
			while(len(frontierList) != 0):
				totalCost, node = heappop(frontierList) #this is the dequeue operation on the FIFO queue
				exploredNodesSet.append(node) #node to be explored now is added to the explored set

				#Goal test
				if(node == goalNode):
					print('Goal Found')
					node.print()
					AStar.traceSolution(solution, node)
					break

				flag = 0

				#Branching point
				for action in actions:
					tNode =  AStar.moveBlank('Manhattan', node, action, goalTilePos) #since its pass by reference, need to maintain the ref to original node
					
					#Check to remove repeated states
					if((tNode not in exploredNodesSet) and (not AStar.isNodeInFrontier((tNode.moveCost + tNode.manhattanDistance, tNode), frontierList))):
						#Goal test
						if(tNode == goalNode):
							print('Goal Found')
							tNode.print()
							AStar.traceSolution(solution, tNode)
							flag = 1
							break
						else:
							heappush(frontierList, (tNode.moveCost + tNode.manhattanDistance, tNode)) #add the new node generated to the frontier if its not a list

				if(flag):
					break #exit the while loop if a solution is found

		except MemoryError:
			print('Failure - Ran out of memory!')
		else:
			time2 = time.time()
			runningTime = (time2 - time1) #calculates the elapsed time
			process = psutil.Process(os.getpid())
			pMemoryUsed = process.memory_info().rss/1000000 #This retrieves the physical memory allocated
			vMemoryUsed = process.memory_info().vms/1000000 #This retrieves the virtual memory allocated
			
		return (solution, runningTime, pMemoryUsed, vMemoryUsed)

class XYPos:
	'(x, y) coordinate representation class'

	def __init__(self, x, y):
		self.x = x
		self.y = y

class PuzzleBoardNode:
	'This class is used to represent a particular state of the puzzle board'
	'''
	puzzleBoard - a 4 x 4 Matrix
	parentNode - object of type PuzzleBoardNode. Used to traceback the path to root. For root, this is None.
	actionTaken - The action taken to reach this node. -1 for root node
	blankPosition - a data object to track where the blank cell is in the board
	'''

	def __init__(self, puzzleBoard, parent, action, blankPosition, moveCost = 0, manhattanDistance = 0, numDisplacedTiles = 0):
		self.puzzleBoard = puzzleBoard
		self.parentNode = parent
		self.actionTaken = action
		self.blankPosition = blankPosition
		self.moveCost = moveCost
		self.manhattanDistance = manhattanDistance
		self.numDisplacedTiles = numDisplacedTiles

	def __eq__(self, puzzleBoardNode):
		#checks if two puzzle boards have the same configuration and can be used to check if a node is visited or not(just check if a node equals any in frontier or explored set)
		return not((self.puzzleBoard > puzzleBoardNode.puzzleBoard) - (self.puzzleBoard < puzzleBoardNode.puzzleBoard)) #python3 workaround for cmp()

	def __hash__(self): #this has to be implemented since __eq__ has been overridden
		return id(self)	

	def __lt__(self, puzzleBoardNode):
		#heappush requires overriding this for some reason.
		return (self.manhattanDistance < puzzleBoardNode.manhattanDistance) or ((self.moveCost + self.numDisplacedTiles) < (puzzleBoardNode.moveCost + puzzleBoardNode.numDisplacedTiles))
	
	def print(self):
		for row in self.puzzleBoard:
			for cell in row:
				print(cell, end = " ")
			print("\n")

class FifteenPuzzle:
	'This class will contain the current state of the FifteenPuzzle property and contain the forwardSearch function'
	'''
	puzzleBoardRoot - object of type PuzzleBoardNode
	solution - array of integers denoting the actions left, right, up and down.
	goalNode - the representation of the goal node
	actions - the possible list of actions
	'''

	def __init__(self, puzzleBoardRoot, goalNode, goalTilePos, actions):
		self.puzzleBoardRoot = puzzleBoardRoot
		self.goalNode = goalNode
		self.actions = actions
		self.goalTilePos = goalTilePos

	def forwardSearch(self):
		'''
			This method calls the A8 method that uses the manhattan and displaced tiles heuristics and passes the current state of the puzzle board.
		'''
		AStar.calculateManhattanDistance(self.puzzleBoardRoot, self.goalTilePos)
		self.solution = AStar.aStarManhattan(self.puzzleBoardRoot, self.goalNode, self.goalTilePos, self.actions)
		print('A* Algorithm using Manhattan Distance as the heuristic function - ')
		self.printSolution()

		self.puzzleBoardRoot.manhattanDistance = 0
		self.solution = AStar.aStarDisplTiles(self.puzzleBoardRoot, self.goalNode, self.goalTilePos, self.actions)
		print('A* Algorithm using Displaced Tiles as the heuristic function - ')
		self.printSolution()

	def printSolution(self):
		'''
			In the array, 0 -> move blank left, 1 -> move blank right, 2 -> move blank up, 3 -> move blank down.
			If no failure and the solution array ends, then print goal state found else failure.
		'''
		
		if(len(self.solution[0]) == 0):
			print('Failure - No Solution is available')
		else:
			print('Depth of the solution - ', len(self.solution[0]))
			print('Sequence of actions to reach the goal state from root is :')
			self.solution[0].reverse()
			for action in self.solution[0]:
				if(action == 0):
					print('Left')
				elif(action == 1):
					print('Right')
				elif(action == 2):
					print('Up')
				elif(action == 3):
					print('Down')

		print('Elapsed Time - ', self.solution[1], 'seconds')
		print('Physical Memory Used - ', self.solution[2], 'MB')
		print('Virtual Memory Used - ', self.solution[3], 'MB')

if (__name__ == '__main__'):
	print("Enter the 15-puzzle input as a space seperated values. For the blank, input either b or B. This char will be converted to -1 for solving")
	'''
	User must provide input in the format - 1 2 3 4 5 6 7 8 9 10 B 11 12 13 14 15
	'''
	
	initialState = []
	temp = []

	while(True):
		rawInput = input('Enter input here : ').split(' ')

		if(len(rawInput) != 16):
			print('Insufficient elements for a 15-Puzzle. Re-enter input!')
			continue

		rawInputIndex = 0
		counter = 1
		goalTilePos = {} #Caching the goal position of each tile for constant time lookups
		for i in range(4):
			temp = []
			for j in range(4):
				goalTilePos[counter] = (i, j)
				counter += 1

				if(rawInput[rawInputIndex] == 'b' or rawInput[rawInputIndex] == 'B'):
					temp.append(-1)
					xy = XYPos(i, j)
				else:
					temp.append(int(rawInput[rawInputIndex]))
				rawInputIndex += 1
			initialState.append(temp)
		
		goalState = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, -1]]
		actions = [2, 3, 0, 1]

		root = PuzzleBoardNode(initialState, None, -1, xy)
		goal = PuzzleBoardNode(goalState, None, -1, XYPos(3, 3))

		print('Initial State')
		root.print()
		print('Goal State')
		goal.print()

		puzzleSolver = FifteenPuzzle(root, goal, goalTilePos, actions)
		puzzleSolver.forwardSearch()
		break