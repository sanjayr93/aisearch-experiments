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

try:
    import psutil  # for computing memory usage
except ImportError:  # try to install requests module if not present
    print ("Trying to Install required module: psutil\n")
    os.system('sudo python -m pip install psutil')
import psutil

#All variables are passed by reference in Python
class IDS:
	'This class contains an implementation of the Iterative Deepening Depth-first Search algorithm'
	
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

	def traceSolution(solution, tNode):
		'''
		A recursive method to trace the sequence of path from the goal to the root node
		This returns a solution array which is the action sequence
		'''
		if(tNode.parentNode):
			solution.append(tNode.actionTaken)
			IDS.traceSolution(solution, tNode.parentNode)

	def dls(node, goalNode, actions, limit, exploredNodes):
		'''
			The dls method takes the complete initial state of the puzzle board (the root) as the argument.
			Returns a solution array with the sequence of actions to go from the initial state to a goal state. 
		'''
		solution = []
		#goal test
		if(node == goalNode):
			print('Goal found')
			node.print()
			IDS.traceSolution(solution, node)
			return solution
		elif(limit == 0):
			#print('cutoff reached')
			return []
		else:
			exploredNodes.append(node) #add current node to explored set
			for action in actions:
				tNode = IDS.moveBlank(node, action) #move the blank to the next position
				if(tNode not in exploredNodes):
					exploredNodes.append(tNode)		#if its an unexplored node, then explore it and add it to the set.
					solution = IDS.dls(tNode, goalNode, actions, limit - 1, exploredNodes)  #call the dls method recursively with decremented depth limit
					if(len(solution) != 0):		#if solution is found then break from the loop
						break
		return solution

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
		self.solution = []

	def forwardSearch(self):
		'''
			This method calls the dls method and passes the current state of the puzzle board.
		'''
		depth = 0
		while(len(self.solution) == 0):
			try:
				time1 = time.time() #start time			
				self.solution = IDS.dls(self.puzzleBoardRoot, self.goalNode, self.actions, depth, [])
			except MemoryError:
				print('Failure - Ran out of memory!')
			else:
				time2 = time.time() #end time
				runningTime = (time2 - time1) #calculates the elapsed time
				process = psutil.Process(os.getpid())
				pMemoryUsed = process.memory_info().rss/1000000 #This retrieves the physical memory allocated
				vMemoryUsed = process.memory_info().vms/1000000 #This retrieves the virtual memory allocated
				#print the time taken and memory used for the above call for each depth
				print('For depth', depth)
				print('Elapsed Time - ', runningTime, 'seconds') #I think this already prints the time taken for each depth value - check once
				print('Physical Memory Used - ', pMemoryUsed, 'MB')
				print('Virtual Memory Used - ', vMemoryUsed, 'MB')
			depth += 1

		self.printSolution()

	def printSolution(self):
		'''
			In the array, 0 -> move blank left, 1 -> move blank right, 2 -> move blank up, 3 -> move blank down.
			If no failure and the solution array ends, then print goal state found else failure.
		'''
		
		if(len(self.solution) == 0):
			print('Failure - No Solution is available')
		else:
			print('Depth of the solution - ', len(self.solution))
			print('Sequence of actions to reach the goal state from root is :')
			self.solution.reverse()
			for action in self.solution:
				if(action == 0):
					print('Left')
				elif(action == 1):
					print('Right')
				elif(action == 2):
					print('Up')
				elif(action == 3):
					print('Down')

if (__name__ == '__main__'):
	print("Enter the 15-puzzle input as a space seperated values. For the blank, input either b or B. This char will be converted to -1 for solving")
	'''
	User must provide input in the format - 1 2 3 4 5 6 7 8 9 10 B 11 12 13 14 15
	'''
	
	initialState = []
	temp = []

	#Read the input from console
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
		#Action sequence - Up, Down, Left, Right
		actions = [2, 3, 0, 1]

		#Formulating the root and goal nodes
		root = PuzzleBoardNode(initialState, None, -1, xy)
		goal = PuzzleBoardNode(goalState, None, -1, XYPos(3, 3))

		print('Initial State')
		root.print()
		print('Goal State')
		goal.print()

		#Invoking the puzzle solver
		puzzleSolver = FifteenPuzzle(root, goal, actions)
		time1 = time.time()
		puzzleSolver.forwardSearch()
		time2 = time.time()
		print('Total Running Time of IDS', (time2 - time1))
		break