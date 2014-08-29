'''halfmax.cells'''

def parser (patternFile, middlepos):
    mapFile = open(patternFile, 'r')
    content = mapFile.readlines() + ['\r\n']
    mapFile.close()

    maxLength = -1

    middleposx, middleposy = middlepos

    patternTextLines = [] # contains the lines for a single level's map.

    patternObj = set () # the map object made from the data in mapTextLines

    for lineNum in range (len(content)):
        # Process each line that was in the level file.
        line = content[lineNum].rstrip('\r\n')

        if '!' in line:
            continue
        else:
            patternTextLines.append(line)
    maxHeight = len(patternTextLines)
    for textLineNum in range (maxHeight):
	    if maxLength < len (patternTextLines [textLineNum]):
		    maxLength = len (patternTextLines [textLineNum])
		    
    for textLineNum in range (len(patternTextLines)):
        textLine = patternTextLines[textLineNum]
        for symbolNum in range (len(textLine)):
            if textLine[symbolNum] == 'O':
                patternObj.add ((((symbolNum + middleposx) - maxLength/2), ((textLineNum + middleposy) - maxHeight/2)))
    return patternObj

def writer (board, fileName):
    relativeBoard = []
    mapFile = open (fileName, 'a')
    minX = 0
    minY = 0
    minX, minY = findMin (board)
    for cell in board:
	x, y = cell
	cell = ((x - minX), (y - minY))
	relativeBoard.append (cell)

    patternList = []
    maxX, maxY = findMax (relativeBoard)
    for y in range (maxY + 1):
	patternList.append ([])
	for x in range (maxX + 1):
	    patternList[y].append ('.')
	    

    for cell in relativeBoard:
	x, y = cell
	patternList [y][x] = 'O'

    #patternList.reverse()

    for y in range (len(patternList)):
	if y != 0:
	    mapFile.write ('\n')
	for x in range (len(patternList[y])):
	    mapFile.write (patternList [y][x])
    mapFile.close ()

def findMax (board):
    maxX = 0
    maxY = 0
    for cell in board:
        x, y = cell
	if x > maxX:
	    maxX = x
	if y > maxY:
	    maxY = y
    return maxX, maxY

def findMin (board):
    xlist = []
    ylist = []
    for cell in board:
        x, y = cell
	xlist.append (x)
	ylist.append (y)


    minX = min (xlist)
    minY = min (ylist)

    return minX, minY

