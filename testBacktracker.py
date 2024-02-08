import time, os
import copy

def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def convertToList(fileContents):
    values = []
    row = []
    count = 0
    for num in fileContents:
        if num == ' ' or num == '\n':
            continue
        if count != 0 and count % 9 == 0:
            values.append(row)
            row = []
        row.append(int(num))
        count += 1
    values.append(row)
    return values

def hasFilters(filename, filters=None):
    if filters == None: return True
    for filter in filters:
        if filter not in filename:
            return False
    return True

def loadBoardPaths(filters):
        boardPaths = [ ]
        for filename in os.listdir(f'Downloads\\15112 Sudoku Term Project\\tp-starter-files\\boards'):
            if filename.endswith('.txt'):
                if hasFilters(filename, filters):
                    boardPaths.append(f'Downloads\\15112 Sudoku Term Project\\tp-starter-files\\boards\\{filename}')
        return boardPaths

def loadBoard(boardPath):
    fileContents = readFile(boardPath)
    return convertToList(fileContents)

def makeLegals(app):
    for row in range(app.rows):
        for col in range(app.cols):
            if app.mutatedValues[row][col] == 0:
                block = findBlock(row, col)
                legalList = getBlock(app, block)
                for n in range(1, 10):
                    if ((app.manualMode == False) and (n not in legalList) and 
                        (n not in app.mutatedValues[row]) and (n not in [app.mutatedValues[row][col] for row in range(len(app.mutatedValues))]) and
                        (n not in app.allLegalsRemoved[row][col])):
                        app.allLegals[row][col].add(n)
                    elif app.manualMode == False and (n in app.allLegals[row][col]):
                        app.allLegals[row][col].remove(n)

                    if app.setMode == True: 
                        if (n in app.nakedTuple):
                            # if (row, col) in app.selectedTupleLocations:
                            #     app.allLegals[row][col].add(n)
                            if (row, col) not in app.tupleLocations and (row in app.tupleRows or col in app.tupleCols or block in app.tupleBlock):
                                if n in app.allLegals[row][col]:
                                    app.allLegals[row][col].remove(n)

                for m in app.editLegals[row][col]:
                    app.allLegals[row][col].add(m)
    return app.allLegals

def getBlockRowCol(app, block):
    n = len(app.mutatedValues)
    blockSize = int(n**0.5)
    startRow = block // blockSize * blockSize
    startCol = block % blockSize * blockSize
    return startRow, startCol

def changeLegals(app, board, row, col, legals):
    newValue = board[row][col]
    block = findBlock(row, col)
    startRow, startCol = getBlockRowCol(app, block)

    for colLegals in range(app.rows):
        if legals[row][colLegals] != set() and newValue in set(legals[row][colLegals]):
            legals[row][colLegals].remove(newValue)

    for rowLegals in range(app.cols):
        if legals[row][colLegals] != set() and newValue in set(legals[rowLegals][col]):
            legals[rowLegals][col].remove(newValue)
    
    for i in range(3):
        for j in range(3):
            blockRow, blockCol = startRow + i, startCol + j
            if legals[blockRow][blockCol] != set() and newValue in set(legals[blockRow][blockCol]):
                legals[blockRow][blockCol].remove(newValue)

def findBlock(row, col):
    if row in {0, 1, 2}:
        if col in {0, 1, 2}:
            block = 0
        elif col in {3, 4, 5}:
            block = 1
        elif col in {6, 7, 8}:
            block = 2
    elif row in {3, 4, 5}:
        if col in {0, 1, 2}:
            block = 3
        elif col in {3, 4, 5}:
            block = 4
        elif col in {6, 7, 8}:
            block = 5
    elif row in {6, 7, 8}:
        if col in {0, 1, 2}:
            block = 6
        elif col in {3, 4, 5}:
            block = 7
        elif col in {6, 7, 8}:
            block = 8
    return block

def getBlock(app, block):
    n = len(app.mutatedValues)
    blockSize = int(n**0.5)
    startRow = block // blockSize * blockSize
    startCol = block % blockSize * blockSize
    values = []
    for drow in range(blockSize):
        for dcol in range(blockSize):
            row, col = startRow + drow, startCol + dcol
            values.append(app.mutatedValues[row][col])
    return values

def makeRowColList(app, boardCopy, allLegals):
    emptyCells = 0
    smallestCount = len(boardCopy)
    rowColList = []
    seen = set()
    for row in range(len(boardCopy)):
        emptyCells += boardCopy[row].count(0)

    while len(rowColList) < emptyCells:
        smallestCount = len(boardCopy)
        for row in range(app.rows):
            for col in range(app.cols):
                if boardCopy[row][col] == 0 and (row, col) not in seen and len(allLegals[row][col]) < smallestCount:
                    smallestCount = len(allLegals[row][col])
                    leastLegals = (row, col)
        rowColList.append(leastLegals)
        seen.add(leastLegals)
    return rowColList

def solveSudoku(app, board):
    boardCopy = copy.deepcopy(board)
    allLegals = copy.deepcopy(app.allLegals)
    rowColList = makeRowColList(app, boardCopy, allLegals)

    return solveSudokuHelper(app, boardCopy, rowColList, allLegals)

def noZeros(boardCopy, rows, cols):
    for row in range(rows):
        for col in range(cols):
            if boardCopy[row][col] == 0:
                return False
    return True

def solveSudokuHelper(app, boardCopy, rowColList, allLegals):
    if noZeros(boardCopy, len(boardCopy), len(boardCopy[0])):
        return boardCopy
    else:
        for (row, col) in rowColList:     
            if boardCopy[row][col] == 0:  
                for n in allLegals[row][col]:
                    if isLegalMove(boardCopy, n, row, col): #check if next move is legal
                        newLegals = copy.deepcopy(allLegals)
                        #remove legals based on new value and update rowColList
                        changeLegals(app, boardCopy, row, col, newLegals)
                        #originalRowColList = copy.copy(rowColList)
                        rowColList = makeRowColList(app, boardCopy, newLegals)
                        
                        #helper loops through board and return row, col
                        solution = solveSudokuHelper(app, boardCopy, rowColList, newLegals)
                        if solution != None:
                            return solution
                        
                        #backtrack
                        boardCopy[row][col] = 0
                        newLegals = allLegals
                        #rowColList = originalRowColList
                break

def isLegalMove(boardCopy, n, row, col):
    boardCopy[row][col] = n
    if isLegalSudoku(boardCopy) == False:
        boardCopy[row][col] = 0
        return False
    return True

def areLegalValues(L):
    n = len(L)
    seen = set()
    
    for value in L:
        if (type(value) != int):
            return False
        if value < 0 or value > n:
            return False
        if value != 0 and value in seen:
            return False
        seen.add(value)
    return True

def isLegalRow(grid, row):
    return areLegalValues(grid[row])

def isLegalCol(grid, col):
    rows = len(grid)
    value = [grid[row][col] for row in range(rows)]
    return areLegalValues(value)

def isLegalBlock(grid, block):
    n = len(grid)
    blockSize = int(n**0.5)
    startRow = block // blockSize * blockSize
    startCol = block % blockSize * blockSize
    values = []
    for drow in range(blockSize):
        for dcol in range(blockSize):
            row, col = startRow + drow, startCol + dcol
            values.append(grid[row][col])
    return areLegalValues(values)

def isLegalSudoku(grid):
    rows, cols = len(grid), len(grid[0])
    if (rows != 9):
        return False
    if (rows != cols):
        return False
    
    for row in range(rows):
        if not isLegalRow(grid, row):
            return False
    for col in range(cols):
        if not isLegalCol(grid, col):
            return False
    blocks = rows
    for block in range(blocks):
        if not isLegalBlock(grid, block):
            return False
    return True

def testBacktracker(app, filters):
    time0 = time.time()
    boardPaths = sorted(loadBoardPaths(filters))
    failedPaths = [ ]
    for boardPath in boardPaths:
        app.mutatedValues = loadBoard(boardPath)
        app.allLegals = makeLegals(app)
        print(boardPath)
        solution = solveSudoku(app, app.mutatedValues)
        if not solution:
            failedPaths.append(boardPath)
    print()
    totalCount = len(boardPaths)
    failedCount = len(failedPaths)
    okCount = totalCount - failedCount
    time1 = time.time()
    if len(failedPaths) > 0:
        print('Failed boards:')
        for path in failedPaths:
            print(f'    {path}')
    percent = 100 * okCount/totalCount
    print(f'Success rate: {okCount}/{totalCount} = {percent}%')
    print(f'Total time: {(time1-time0, 1)} seconds')