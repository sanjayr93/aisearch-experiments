"""
Author - Sanjay Ramachandran

Readme:
- This Python script uses a OS agnostic library psutil to access the memory information.
- Please install psutil using "pip install psutil"
"""

#!/usr/bin/python3
import time
import os
import psutil
import copy

#All variables are passed by reference in Python
class BFS:
	'This class contains an implementation of the Breadth-First Search algorithm'
	
	def moveBlank(node, action):
		'''
		This function swaps the blank cell and the nearby cell based on the action given in input argument
		It returns a new child node with the new configuration
		'''
		#to retain the original reference to a node, this temporary node is created
		tNode = PuzzleBoardNode(copy.deepcopy(node.puzzleBoard), node, action, XYPos(node.blankPosition.x, node.blankPosition.y))
		if(action == 0):
			#Left
			if(tNode.blankPosition.y > 0):				
				tNode.blankPosition.y -= 1
		elif(action == 1):
			#Right
			if(tNode.blankPosition.y < (len(tNode.puzzleBoard[0]) - 1)):
				tNode.blankPosition.y += 1
		elif(action == 2):
			#Up
			if(tNode.blankPosition.x > 0):
				tNode.blankPosition.x -= 1
		elif(action == 3):
			#Down
			if(tNode.blankPosition.x < (len(tNode.puzzleBoard) - 1)):
				tNode.blankPosition.x += 1

		#swap the nearby value cell and the blank cell
		tNode.puzzleBoard[node.blankPosition.x][node.blankPosition.y] = tNode.puzzleBoard[tNode.blankPosition.x][tNode.blankPosition.y]
		tNode.puzzleBoard[tNode.blankPosition.x][tNode.blankPosition.y] = -1

		return tNode

	def isNodeInFrontier(tNode, frontierList):
		'''
		This method iterates through the frontier list to find if the given node is present or not
		'''
		for node in frontierList:
			if(tNode == node):
				return 1
		return 0

	def traceSolution(solution, tNode):
		'''
		A recursive method to trace the sequence of path from the goal to the root node
		This returns a solution array which is the action sequence
		'''
		if(tNode.parentNode):
			solution.append(tNode.actionTaken)
			BFS.traceSolution(solution, tNode.parentNode)

	def bfs(puzzleBoardNode, goalNode, actions):
		'''
			The bfs method takes the complete initial state of the puzzle board (the root) as the argument.
			Returns a tuple with the solution array with the sequence of actions to go from the initial state to a goal state and some time/memory statistics. 
		'''
		solution = []
		exploredNodesSet = set() #unordered set
		frontierList = [] #this has to be ordered to implement a FIFO Queue - pop(0) to dequeue
		frontierList.append(puzzleBoardNode);
		time1 = time.time() #start time
		try:
			while(len(frontierList) != 0):
				node = frontierList.pop(0) #this is the dequeue operation on the FIFO queue
				exploredNodesSet.add(node) #node to be explored now is added to the explored set

				#Goal test
				if(node == goalNode):
					print('Goal Found')
					node.print()
					BFS.traceSolution(solution, node)
					break

				flag = 0

				#Branching point
				for action in actions:
					tNode =  BFS.moveBlank(node, action) #since its pass by reference, need to maintain the ref to original node
					
					#Check to remove repeated states
					if((tNode not in exploredNodesSet) and (BFS.isNodeInFrontier(tNode, frontierList) == 0)):
						#Goal test
						if(tNode == goalNode):
							print('Goal Found')
							tNode.print()
							BFS.traceSolution(solution, tNode)
							flag = 1
							break
						else:
							frontierList.append(tNode) #add the new node generated to the frontier if its not a list
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

	def __init__(self, puzzleBoard, parent, action, blankPosition):
		self.puzzleBoard = puzzleBoard
		self.parentNode = parent
		self.actionTaken = action
		self.blankPosition = blankPosition

	def __eq__(self, puzzleBoardNode):
		#checks if two puzzle boards have the same configuration and can be used to check if a node is visited or not(just check if a node equals any in frontier or explored set)
		return not((self.puzzleBoard > puzzleBoardNode.puzzleBoard) - (self.puzzleBoard < puzzleBoardNode.puzzleBoard)) #python3 workaround for cmp()

	def __hash__(self): #this has to be implemented since __eq__ has been overridden
		return id(self)	
	
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

	def __init__(self, puzzleBoardRoot, goalNode, actions):
		self.puzzleBoardRoot = puzzleBoardRoot
		self.goalNode = goalNode
		self.actions = actions

	def forwardSearch(self):
		'''
			This method calls the bfs method and passes the current state of the puzzle board.
		'''
		self.solution = BFS.bfs(self.puzzleBoardRoot, self.goalNode, self.actions)
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
		for i in range(4):
			temp = []
			for j in range(4):
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

		puzzleSolver = FifteenPuzzle(root, goal, actions)
		puzzleSolver.forwardSearch()
		break