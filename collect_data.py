#!/usr/bin/python

'''
	Python file that loads the data containing time stamps of all commands 
	executing during booting time of a virtual machine and analyzes them to 
	get duration of each so it can provide the best part to be optimized 
	and reduced in a sense of time.
'''

import os
import numpy as numpy
import fnmatch
from operator import itemgetter


if ("ASH_SCORES" in os.environ):
	directoryScores = os.environ["ASH_SCORES"]
else:
	print("Chosen directory with data from BusyBox ash does not exist.")
	exit()
	
def loadScores():
	'''
		Method that loads all time stamps related to the specific commands, 
		removes duplicates and time stamps that were used just as an 
		orientation (e.g. -1).
		Result is written in a text file named "all".
	'''

	mergedFiles = directoryScores + "/all" 
	fAll = open(mergedFiles, "w")
	fAll.write("command!start!pid!end\n")
	allWrittenLines = []
	for scorePid in fnmatch.filter(os.listdir(directoryScores), 'scores.csv.*'):

		scoreFile = directoryScores + "/" + scorePid
		f = open(scoreFile, "r")
		lines = f.readlines()
		f.close()

		allShareLines = []
		sharePidLines = []
		listWritten = []
		for line in lines:
			flag = False
			if (line != "command!start!pid!end\n") :
				#set the flag if line contains -1 meaning it takes more time to execute complex commands
				for i in range ( len(line.split('!'))):
			 		item = line.split('!')[i]
			 		if ("-1" in item and (len(item) == 2 or item.endswith('\n'))):
			 			flag = True
			 	
			 	#list of repeating pids
			 	if (flag == False and findByPid(line, listWritten) == False and line not in allWrittenLines):
			 		fAll.write(line)			
			 		listWritten.append(line)

		for i in range(len(listWritten)):
			allWrittenLines.append(listWritten[i])



	fAll.close()


def findByPid(line, writtenLines):
	'''
		Method that returns true statement if there already exists a time stamp 
		related to the specific pid, i.e. if that command is already written 
		in a text file with results.
	'''

	for i in range(len(writtenLines)):
		if (len(line.split('!')) == len(writtenLines[i].split('!'))):
			countTheSame = 0
			for j in range(len(writtenLines[i].split('!'))):
				if (writtenLines[i].split('!')[j] == line.split('!')[j]):
					countTheSame += 1
			if (countTheSame == len(writtenLines[i].split('!'))-1):
				return True
	return False



def hasSamePid(first, second):
	'''
		Method that returns true statement if two lines containing the
		command, start time stamp and pid, i.e. end time stamp and pid have 
		the same pid so that duration can be calculated for that specific pid.
	'''

	first = first.split('!')[2]
	if first.endswith('\n'):
		first = first[:-1]

	if (first == second.split('!')[2]):
		return True
	return False



def calculateDuration():
	'''
		Given all scores from the file "all", this method needs to group lines 
		two by two based on its pid to calculate duraion of each process that 
		is executing. When duration is calculated, results are sorted based 
		on it value and saved to a new file named "sortedAll".
	'''

	mergedFiles = directoryScores + "/all" 
	newSorted = directoryScores + "/sortedAll"
	fAll = open(mergedFiles, "r")
	fSort = open(newSorted, "w")
	fSort.write("command ! total ! nbOfTimes ! avgDuration\n")
	lines = fAll.readlines()
	minStart = float("inf")
	maxEnd = 0

	for i in range(len(lines)):

		if (lines[i] != "command!start!pid!end\n"):

			if (len(lines[i].split("!")) == 3):
				firstTime = lines[i].split('!')[1]
				firstLine = [long(s) for s in firstTime.split() if s.isdigit()]
				if (firstLine[0] < minStart):

					minStart = firstLine[0]
			else:
				firstTime = lines[i].split('!')[3]
				firstLine = [long(s) for s in firstTime.split() if s.isdigit()]
				if (firstLine[0] > maxEnd):

					maxEnd = firstLine[0]


	duration = maxEnd- minStart
	writeLine = "total duration: " +  "%ld" % duration + "\n"
	fSort.write(writeLine)

	usedCommands=[]
	hashAll = {}
	for i in range(1, len(lines) - 1):
		if (lines[i] != "command!start!pid!end\n" and len(lines[i].split('!')) == 3):	
			j = i+1
			while (j < len(lines)):
				secondLine = lines[j]
			 	if (len(lines[i].split('!')) < len(secondLine.split('!'))):
			 		if (hasSamePid(lines[i],secondLine)):
				 		a = lines[i].split('!')[2]
			 			if a.endswith('\n'):
   							a = a[:-1]
		 				firstTime = lines[i].split('!')[1]		 				
						firstLine = [long(s) for s in firstTime.split() if s.isdigit()]							
						secondTime= secondLine.split('!')[3]
						secondLine = [long(s) for s in secondTime.split() if s.isdigit()]

		 				duration = secondLine[0] - firstLine[0]
		 				comLine = lines[i].split('!')[0]
		 				if (comLine not in usedCommands):
		 					usedCommands.append(comLine)
		 					hashAll[comLine] = [duration, 1, duration]
		 				else:
		 					hashAll[comLine][0] += duration
		 					hashAll[comLine][1] += 1
		 					hashAll[comLine][2] = hashAll[comLine][0]/hashAll[comLine][1]
						break
					else:					
						j += 1
						continue
				else:
					j += 1
					continue

 	hashAll=sorted(hashAll.items(), key=lambda e: e[1][2])
	for i in range(len(hashAll)):
		writeLine = "\n" + hashAll[i][0] + "!" + " %ld " % hashAll[i][1][0] + "!" + " %ld " % hashAll[i][1][1] + "!" + " %ld " % hashAll[i][1][2]
		fSort.write(writeLine) 
	fAll.close()
	fSort.close()

	

