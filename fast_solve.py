import copy

def fast_solve(initialBoard):
    emptyLegals = [[set() for i in range(9)] for j in range(9)]
    boardLegals = makeLegals(emptyLegals, initialBoard)
    return solveSudoku(boardLegals, initialBoard)

def makeRowColList(boardCopy, allLegals):
    emptyCells = 0
    smallestCount = len(boardCopy)
    rowColList = []
    seen = set()
    for row in range(len(boardCopy)):
        emptyCells += boardCopy[row].count(0)

    while len(rowColList) < emptyCells:
        smallestCount = len(boardCopy)
        for row in range(9):
            for col in range(9):
                if boardCopy[row][col] == 0 and (row, col) not in seen and len(allLegals[row][col]) < smallestCount:
                    smallestCount = len(allLegals[row][col])
                    leastLegals = (row, col)
        rowColList.append(leastLegals)
        seen.add(leastLegals)
    return rowColList

def solveSudoku(boardLegals, board):
    boardCopy = copy.deepcopy(board)
    allLegals = copy.deepcopy(boardLegals)
    rowColList = makeRowColList(boardCopy, allLegals)
    return solveSudokuHelper(boardCopy, rowColList, allLegals)

def noZeros(boardCopy, rows, cols):
    for row in range(rows):
        for col in range(cols):
            if boardCopy[row][col] == 0:
                return False
    return True

def solveSudokuHelper(boardCopy, rowColList, allLegals):
    if noZeros(boardCopy, len(boardCopy), len(boardCopy[0])):
        return boardCopy
    else:
        for (row, col) in rowColList:     
            if boardCopy[row][col] == 0:  
                for n in allLegals[row][col]:
                    if isLegalMove(boardCopy, n, row, col):
                        newLegals = copy.deepcopy(allLegals)

                        changeLegals(boardCopy, row, col, newLegals)
                        originalRowColList = copy.copy(rowColList)
                        rowColList = makeRowColList(boardCopy, newLegals)

                        solution = solveSudokuHelper(boardCopy, rowColList, newLegals)
                        if solution != None:
                            return solution
                        
                        boardCopy[row][col] = 0
                        newLegals = allLegals
                        rowColList = originalRowColList
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

def makeLegals(allLegals, board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                block = findBlock(row, col)
                legalList = getBlock(board, block)
                for n in range(1, 10):
                    if ((n not in legalList) and 
                        (n not in board[row]) and (n not in [board[row][col] for row in range(len(board))])):
                        allLegals[row][col].add(n)
                    elif n in allLegals[row][col]:
                        allLegals[row][col].remove(n)
    return allLegals

def changeLegals(board, row, col, legals):
    newValue = board[row][col]
    block = findBlock(row, col)
    startRow, startCol = getBlockRowCol(board, block)
    for colLegals in range(9):
        if legals[row][colLegals] != set() and newValue in set(legals[row][colLegals]):
            legals[row][colLegals].remove(newValue)

    for rowLegals in range(9):
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

def getBlock(board, block):
    n = len(board)
    blockSize = int(n**0.5)
    startRow = block // blockSize * blockSize
    startCol = block % blockSize * blockSize
    values = []
    for drow in range(blockSize):
        for dcol in range(blockSize):
            row, col = startRow + drow, startCol + dcol
            values.append(board[row][col])
    return values

def getBlockRowCol(board, block):
    n = len(board)
    blockSize = int(n**0.5)
    startRow = block // blockSize * blockSize
    startCol = block % blockSize * blockSize
    return startRow, startCol