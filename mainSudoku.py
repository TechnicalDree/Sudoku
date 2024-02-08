from cmu_graphics import *
from PIL import *
import math
import random
import copy
import os
import itertools

'''Extra features: Beautiful UI, Improved Hint Generator, Preferences file, Sudoku Variations, Shaded regions based on selected cell'''

# from https://www.cs.cmu.edu/~112-3/notes/term-project.html
def removeTempFiles(path, suffix='.DS_Store'): 
    if path.endswith(suffix):
        print(f'Removing file: {path}')
        os.remove(path)
    elif os.path.isdir(path):
        for filename in os.listdir(path):
            removeTempFiles(path + '/' + filename, suffix)

removeTempFiles('sampleFiles')

# from https://www.cs.cmu.edu/~112-3/notes/term-project.html
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

# from https://www.cs.cmu.edu/~112-3/notes/term-project.html
def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)

# from https://www.cs.cmu.edu/~112-3/notes/term-project.html (Same logic, but with different variables and contains a helper function)
def getSudokuFile(app):
    fileList = []
    for filename in os.listdir('Downloads\\15112 Sudoku Term Project\\tp-starter-files\\boards'):
        if filename.startswith(app.difficulty):
            fileList.append(filename)
    selectedFile = random.choice(fileList)
    pathToFile = f'Downloads\\15112 Sudoku Term Project\\tp-starter-files\\boards\\{selectedFile}'
    fileContents = readFile(pathToFile)
    return convertToList(fileContents)

def getManualFile(app):
    pathToFile = f'Downloads\\15112 Sudoku Term Project\\{app.inputFile}'
    if app.inputFile.endswith('Manual.txt'):
        fileContents = readFile(pathToFile)
        app.fileNotFound = False
        return convertToList(fileContents)
    else:
        app.fileNotFound = True

def getPrefFile(app):
    pathToFile = f'Downloads\\15112 Sudoku Term Project\\{app.inputFile}'
    if app.inputFile.endswith('Preferences.txt'):
        fileContents = readFile(pathToFile)
        app.fileNotFound = False
        return fileContents
    else:
        app.fileNotFound = True

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

#https://cs3-112-f22.academy.cs.cmu.edu/exercise/4965 (Looked at one of my tetris exercises, and that code was made by me. I'm reusing this to implement a board rotation)
def rotateBoard(app, board):
    oldRows, oldCols = len(board), len(board[0])
    newRows, newCols = len(board[0]), len(board)
    newBoard = [[None]*newCols for i in range(newRows)]
    
    for oldRow in range(oldRows):
        for oldCol in range(oldCols):
            for newRow in range(newRows):
                for newCol in range(newCols):
                    oldRow = newCol
                    oldCol = newRow
                    newBoard[newRow][newCol] = board[oldRow][oldCol]
                    
    for row in range(len(newBoard)):
        newBoard[row].reverse()
    return newBoard

def rotateCells(app, cellList):
    if cellList != None:
        oldRows, oldCols = app.rows, app.cols
        newRows, newCols = app.rows, app.cols
        oldCellList = copy.copy(cellList)
        for oldRow in range(oldRows):
            for oldCol in range(oldCols):
                newRow = oldCol
                newCol = (newCols - 1) - oldRow
                if (oldRow, oldCol) in oldCellList:
                    cellList.remove((oldRow, oldCol))
                    if isinstance(cellList, set):
                        cellList.add((newRow, newCol))
                    else:
                        cellList.append((newRow, newCol))
                elif (oldRow, oldCol) == oldCellList:
                    cellList = (newRow, newCol)
    return cellList

def rotateUndoRedo(app, cellList):
    if cellList != None:
        oldRows, oldCols = app.rows, app.cols
        newRows, newCols = app.rows, app.cols
        oldCellList = copy.copy(cellList)
        for oldRow in range(oldRows):
            for oldCol in range(oldCols):
                newRow = oldCol
                newCol = (newCols - 1) - oldRow
                for val in range(1, 10):
                    if (val, oldRow, oldCol) in oldCellList:
                        cellList.remove((val, oldRow, oldCol))
                        if isinstance(cellList, set):
                            cellList.add((val, newRow, newCol))
                        else:
                            cellList.append((val, newRow, newCol))
                    elif (val, oldRow, oldCol) == oldCellList:
                        cellList = (newRow, newCol)
    return cellList

#Used for tp0 and tp1 when backtracker hasn't been implemented yet
def getSudokuFileWithSolutions(app):
    fileList = []
    for filename in os.listdir('Downloads\\15112 Sudoku Term Project\\images-boards-and-solutions-for-1-thru-3'):
        if filename.endswith('txt') and filename.startswith(app.difficulty) and 'solution' not in filename:
            fileList.append(filename)
    selectedFile = random.choice(fileList)
    pathToFile = f'Downloads\\15112 Sudoku Term Project\\images-boards-and-solutions-for-1-thru-3\\{selectedFile}'
    fileContents = readFile(pathToFile)
    
    selectedFileList = selectedFile.split('.')
    for filename in os.listdir('Downloads\\15112 Sudoku Term Project\\images-boards-and-solutions-for-1-thru-3'):
        if filename.startswith(selectedFileList[0]) and filename.find('solution') != -1:
            solutionFile = filename
    pathToFile2 = f'Downloads\\15112 Sudoku Term Project\\images-boards-and-solutions-for-1-thru-3\\{solutionFile}'
    solutionContents = readFile(pathToFile2)
    app.solution = convertToList(solutionContents)
    return convertToList(fileContents)

#from https://www.cs.cmu.edu/~112-3/notes/term-project.html
def loadAnimatedGif(app, path):
    pilImages = Image.open(path)
    if pilImages.format != 'GIF':
        raise Exception(f'{path} is not an animated image!')
    if not pilImages.is_animated:
        raise Exception(f'{path} is not an animated image!')
    cmuImages = [ ]
    for frame in range(pilImages.n_frames):
        pilImages.seek(frame)
        pilImage = pilImages.copy()
        cmuImages.append(CMUImage(pilImage))
    return cmuImages

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

                        rowColList = makeRowColList(app, boardCopy, newLegals)
                        
                        #helper loops through board and return row, col
                        solution = solveSudokuHelper(app, boardCopy, rowColList, newLegals)
                        if solution != None:
                            return solution
                        
                        #backtrack
                        boardCopy[row][col] = 0
                        newLegals = allLegals
                break

def isLegalMove(boardCopy, n, row, col):
    boardCopy[row][col] = n
    if isLegalSudoku(boardCopy) == False:
        boardCopy[row][col] = 0
        return False
    return True

#https://cs3-112-f22.academy.cs.cmu.edu/exercise/4823
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

#https://cs3-112-f22.academy.cs.cmu.edu/exercise/4823
def isLegalRow(grid, row):
    return areLegalValues(grid[row])

#https://cs3-112-f22.academy.cs.cmu.edu/exercise/4823
def isLegalCol(grid, col):
    rows = len(grid)
    value = [grid[row][col] for row in range(rows)]
    return areLegalValues(value)

#https://cs3-112-f22.academy.cs.cmu.edu/exercise/4823
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

#https://cs3-112-f22.academy.cs.cmu.edu/exercise/4823
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

def help_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill = 'lightgreen')
    drawImage(app.helpUrl, 0, 0, width=app.width, height=app.height)
    drawLabel('HOW TO PLAY', app.width/2, 60, size = 40, bold = True)
    drawLabel('BACK TO INTRO', 75, app.height - 25, size = 20, bold = True, fill = app.helpLabelColor)
    drawLabel('There are 3 ways to setup the initial board:', app.width/4, 120, size = 20, bold = True)
    drawLabel('- Select UI mode + Difficulty', app.width/6, 160, align = 'left', size = 17)
    drawLabel('- Manually setup the board graphically', app.width/6, 200, align = 'left', size = 17)
    drawLabel('- Enter a text file for the board to load', app.width/6, 240, align = 'left', size = 17)
    drawLabel("- When entering a file, make sure its path is 'Downloads\\15112 Sudoku Term Project\\{text file}'", app.width/5, 280, align = 'left', size = 15)
    drawLabel("- You may also enter a preferences file to change the board's colors with rgb values", app.width/5, 320, align = 'left', size = 17)
    drawLabel("- Example: emptyCell = 150,150,150", app.width/5, 360, align = 'left', size = 17)

    drawLabel("Key commands:", app.width/8, 420, size = 20, bold = True)
    drawLabel("Arrow keys = Move between Cells", app.width/6, 460, align = 'left', size = 17)
    drawLabel("'a' = Automatic legals", app.width/6, 490, align = 'left', size = 17)
    drawLabel("'m' = Manual legals", app.width/6, 520, align = 'left', size = 17)
    drawLabel("'s' = Singleton", app.width/6, 550, align = 'left', size = 17)
    drawLabel("'S' = All singletons", app.width/6, 580, align = 'left', size = 17)
    drawLabel("'u' = Undo move", app.width/6, 610, align = 'left', size = 17)
    drawLabel("'r' = Redo move", app.width/6, 640, align = 'left', size = 17)
    drawLabel("'h' = Basic Hint", app.width/6, 670, align = 'left', size = 17)
    drawLabel("'H' = Strong Hint", app.width/6, 700, align = 'left', size = 17)
    drawLabel("'t' = Rotate Board", app.width/6, 730, align = 'left', size = 17)
    drawLabel("'escape' = Help", app.width/6, 760, align = 'left', size = 17)

def help_onMouseMove(app, mouseX, mouseY):
    if (0 <= mouseX <= 125) and (app.height-50 <= mouseY <= app.height):
        app.helpLabelColor = 'red'
    else:
        app.helpLabelColor = 'black'

def help_onMousePress(app, mouseX, mouseY):
    if (0 <= mouseX <= 125) and (app.height-50 <= mouseY <= app.height):
        setActiveScreen('splash')

def splash_onAppStart(app):
    app.helpUrl = 'https://wallpapercave.com/wp/wp2261083.jpg' 
    app.rows = 9
    app.cols = 9
    
    app.selected = rgb(255, 128, 0) #orange
    app.selectedReg = rgb(153, 255, 255) #cyan

    app.selectedHint = rgb(153, 255, 153) #lightGreen
    app.hint = rgb(0, 255, 0) #green

    app.selectedWrong = rgb(255, 153, 153) #lightRed
    app.wrong = rgb(255, 0, 0) #red

    app.initialVal = rgb(169, 169, 169) #darkGrey
    app.selectedInitialVal = rgb(211, 211, 211) #lightGrey

    app.emptyCell = rgb(255, 255, 240) #lightyellow


    app.sprites = None
    app.spriteCounter = 0
    app.stepsPerSecond = 10

    app.splashScreen = True
    app.helpScreen = False
    app.playScreen = False
    
    app.mouseMode = False
    app.keyboardMode = False
    app.standardMode = False
    app.competitionMode = False

    app.difficulty = None
    app.difficulties = ['easy', 'medium', 'hard', 'expert', 'evil']

    app.rectColor = None
    app.rects = [(387, 239, 85, 24), (485, 239, 105, 24), (603, 239, 75, 24)]
    app.rects2 = [(365, 288, 45, 24), (427, 288, 62, 24), (520, 288, 40, 24), (582, 288, 50, 24), (653, 288, 50, 24)]
    app.rects3 = [(355, 339, 90, 24), (445, 339, 180, 24), (630, 339, 120, 24)]

    app.mouseRectColor = None
    app.keyboardRectColor = None
    app.standardRectColor = None
    app.easyRectColor = None
    app.mediumRectColor = None
    app.hardRectColor = None
    app.expertRectColor = None
    app.evilRectColor = None

    app.graphicRectColor = None
    app.fileRectColor = None
    app.prefRectColor = None

    app.clickLabelColor = 'black'
    app.helpLabelColor = 'black'
    app.cells = [str(i) for i in range(1, 10)] + ['X'] + ['Auto'] + ['Manual'] + ['Single'] + ['All single'] + ['Undo'] + ['Redo'] + ['Hint'] + ['HINT']
    resetVariables(app)

def resetVariables(app):
    app.values = [[0 for i in range(9)] for j in range(9)]
    app.mutatedValues = [[0 for i in range(9)] for j in range(9)]
    app.wrongValues = set()
    app.undoneWrong = set()

    app.manualBoard = None
    app.selectingVals = False
    app.preferences = None

    app.gameOver = False

    app.editLegals = [[set() for i in range(9)] for j in range(9)]
    app.allLegalsRemoved = [[set() for i in range(9)] for j in range(9)]
    app.legals = [{1, 2, 3}, {4, 5, 6}, {7, 8, 9}]
    app.allLegals = [[set() for i in range(9)] for j in range(9)]
    app.manualLegals = [[set() for i in range(9)] for j in range(9)]
    app.autoMode = False
    app.manualMode = False

    app.selection = None
    app.selectedRow, app.selectedCol, app.selectedBlock = None, None, None
    app.allSingletons = False
    app.noSingletons = False
    app.singletonLocations = set()
    app.removedSingletonLocations = set()
    app.singleRowCol = None
    app.aloneRowCol = None
    app.aloneLegal = None
    app.nakedTuple = set()
    app.tupleLocations = []
    app.tupleRows, app.tupleCols, app.tupleBlock = set(), set(), set()
    app.allTupleLocations = []
    app.allNakedTuples = []
    app.selectedNakedTuple = []
    app.selectedTupleLocations = []
    app.setMode = False

    app.fileNotFound = False

    app.movesBoard = [[0 for i in range(9)] for j in range(9)]
    app.seenMoves = []
    app.undoList = []
    app.undoLegalList = []
    app.redoList = []
    app.redoLegalList = []
    app.undoRedoLegals = [[set() for i in range(9)] for j in range(9)]
    app.undoneWrongLegals = set()
    app.moveIndex = 0

    app.manualLegals = [[set() for i in range(9)] for j in range(9)]

    app.regions, app.rowList, app.colList, app.blockList = [], [], [], []
    makeRegionList(app)

def splash_redrawAll(app):
    drawIntro(app)

#https://www.cs.cmu.edu/~112-3/notes/term-project.html (Image demo)
def splash_onStep(app):
    if app.sprites != None:
        app.spriteCounter = (1 + app.spriteCounter) % len(app.sprites)

def splash_onMouseMove(app, mouseX, mouseY):
    if (360 <= mouseX <= 540) and (380 <= mouseY <= 420):
        app.clickLabelColor = 'red'
    else:
        app.clickLabelColor = 'black'
    
    if (0 <= mouseX <= 100) and (app.height-50 <= mouseY <= app.height):
        app.helpLabelColor = 'red'
    else:
        app.helpLabelColor = 'black'

def splash_onMousePress(app, mouseX, mouseY):
    for (x0, y0, x1, y1) in app.rects:
        if (x0 <= mouseX <= x1+x0) and (y0 <= mouseY <= y1+y0):
            if x0 == 387:
                if app.mouseMode == True:
                    app.mouseMode = False
                    app.mouseRectColor = None
                    app.sprites = None
                else:
                    app.mouseMode = True
                    app.keyboardMode = False
                    app.mouseRectColor = 'cyan'
                    app.keyboardRectColor = None
                    app.standardMode = False
                    app.standardRectColor = None
                    app.spriteCounter = 0
                    app.sprites = loadAnimatedGif(app, 'Downloads\\15112 Sudoku Term Project\\clicking.gif')
            elif x0 == 485:
                if app.keyboardMode == True:
                    app.keyboardMode = False
                    app.keyboardRectColor = None
                    app.sprites = None
                else:
                    app.keyboardMode = True
                    app.keyboardRectColor = 'cyan'
                    app.mouseMode = False
                    app.mouseRectColor = None
                    app.standardMode = False
                    app.standardRectColor = None
                    app.spriteCounter = 0
                    app.sprites = loadAnimatedGif(app, 'Downloads\\15112 Sudoku Term Project\\typing.gif')
            else:
                if app.standardMode == True:
                    app.standardMode = False
                    app.standardRectColor = None
                    app.sprites = None
                else:
                    app.standardMode = True
                    app.standardRectColor = 'cyan'
                    app.mouseMode = False
                    app.mouseRectColor = None
                    app.keyboardMode = False
                    app.keyboardRectColor = None
                    app.spriteCounter = 0
                    app.sprites = loadAnimatedGif(app, 'Downloads\\15112 Sudoku Term Project\\standard.gif')
    
    for (x0, y0, x1, y1) in app.rects2:
        if (x0 <= mouseX <= x1+x0) and (y0 <= mouseY <= y1+y0):
            app.fileNotFound = False
            resetVariables(app)
            if x0 == 365:
                if app.difficulty == 'easy':
                    app.difficulty = None
                    app.easyRectColor = None
                    app.manualMode = False
                    app.gameOver = False
                elif app.manualBoard == None:
                    app.difficulty = 'easy'
                    app.easyRectColor = 'green'
                    app.mediumRectColor = None
                    app.hardRectColor = None
                    app.expertRectColor = None
                    app.evilRectColor = None
                    app.values = getSudokuFile(app)
                    app.mutatedValues = copy.deepcopy(app.values)
                    app.autoMode = False
                    app.cells = [str(i) for i in range(1, 10)] + ['X'] + ['Auto'] + ['Manual'] + ['Undo'] + ['Redo'] + ['Hint'] + ['HINT'] + ['Rotate']
            elif x0 == 427:
                if app.difficulty == 'medium':
                    app.difficulty = None
                    app.mediumRectColor = None
                    app.gameOver = False
                elif app.manualBoard == None:
                    app.difficulty = 'medium'
                    app.mediumRectColor = 'yellow'
                    app.easyRectColor = None
                    app.hardRectColor = None
                    app.expertRectColor = None
                    app.evilRectColor = None
                    app.cells = [str(i) for i in range(1, 10)] + ['X'] + ['Auto'] + ['Manual'] + ['Single'] + ['All single'] + ['Undo'] + ['Redo'] + ['Hint'] + ['HINT'] + ['Rotate']
                    app.values = getSudokuFile(app)
                    app.mutatedValues = copy.deepcopy(app.values)
                    app.autoMode = True
            elif x0 == 520:
                if app.difficulty == 'hard':
                    app.difficulty = None
                    app.hardRectColor = None
                    app.gameOver = False
                elif app.manualBoard == None:
                    app.difficulty = 'hard'
                    app.hardRectColor = 'orange'
                    app.mediumRectColor = None
                    app.easyRectColor = None
                    app.expertRectColor = None
                    app.evilRectColor = None
                    app.values = getSudokuFile(app)
                    app.cells = [str(i) for i in range(1, 10)] + ['X'] + ['Auto'] + ['Manual'] + ['Single'] + ['All single'] + ['Undo'] + ['Redo'] + ['Hint'] + ['HINT'] + ['Rotate']
                    app.mutatedValues = copy.deepcopy(app.values)
                    app.autoMode = True
            elif x0 == 582:
                if app.difficulty == 'expert':
                    app.difficulty = None
                    app.expertRectColor = None
                    app.gameOver = False
                elif app.manualBoard == None:
                    app.difficulty = 'expert'
                    app.expertRectColor = 'red'
                    app.mediumRectColor = None
                    app.hardRectColor = None
                    app.easyRectColor = None
                    app.evilRectColor = None
                    app.cells = [str(i) for i in range(1, 10)] + ['X'] + ['Auto'] + ['Manual'] + ['Single'] + ['All single'] + ['Undo'] + ['Redo'] + ['Hint'] + ['HINT'] + ['Rotate']
                    app.values = getSudokuFile(app)
                    app.mutatedValues = copy.deepcopy(app.values)

                    app.autoMode = True
            elif x0 == 653:
                if app.difficulty == 'evil':
                    app.difficulty = None
                    app.evilRectColor = None
                    app.gameOver = False
                elif app.manualBoard == None:
                    app.difficulty = 'evil'
                    app.evilRectColor = 'gray'
                    app.mediumRectColor = None
                    app.hardRectColor = None
                    app.expertRectColor = None
                    app.easyRectColor = None
                    app.cells = [str(i) for i in range(1, 10)] + ['X'] + ['Auto'] + ['Manual'] + ['Single'] + ['All single'] + ['Undo'] + ['Redo'] + ['Hint'] + ['HINT'] + ['Rotate']
                    app.values = getSudokuFile(app)
                    app.mutatedValues = copy.deepcopy(app.values)
                    app.autoMode = True

    for (x0, y0, x1, y1) in app.rects3:
        if (x0 <= mouseX <= x1+x0) and (y0 <= mouseY <= y1+y0):
            if x0 == 355:
                if app.manualBoard == 'graphic':
                    app.manualBoard = None
                    app.graphicRectColor = None
                    app.selectingVals = False
                elif app.difficulty == None:
                    app.graphicRectColor = 'pink'
                    app.fileRectColor = None
                    app.manualBoard = 'graphic'
                    app.manualMode, app.autoMode = False, False
                    app.selectingVals = True
                    app.values = [ [0]*9 for i in range(9) ]
                    app.mutatedValues = copy.deepcopy(app.values)
            if x0 == 445:
                if app.manualBoard == 'manualFile':
                    app.manualBoard = None
                    app.fileRectColor = None
                elif app.difficulty == None:
                    app.inputFile = app.getTextInput("Enter text file (Include '.txt')")
                    app.values = getManualFile(app)
                    if app.fileNotFound == False:
                        app.graphicRectColor = None
                        app.selectingVals = False
                        app.fileRectColor = 'pink'
                        app.manualBoard = 'manualFile'
                        app.mutatedValues = copy.deepcopy(app.values)
            if x0 == 630:
                app.preferences = True
                app.inputFile = app.getTextInput("Enter preferences file (Include '.txt')")
                prefContents = getPrefFile(app)
                if app.fileNotFound == False:
                    app.prefRectColor = 'pink'
                    for line in prefContents.splitlines():
                        line = line.split(' ')
                        variable = line[0]

                        color = line[-1]
                        color = color.split(',')
                        red, blue, green = int(color[0]), int(color[1]), int(color[2])
                        rgbVal = rgb(red, blue, green)

                        if variable.startswith('selected'):
                            if variable.endswith('Reg'):
                                app.selectedReg = rgbVal
                            elif variable.endswith('Hint'):
                                app.selectedHint = rgbVal
                            elif variable.endswith('Wrong'):
                                app.selectedWrong = rgbVal
                            elif variable.endswith('InitialVal'):
                                app.selectedInitialVal = rgbVal
                            elif variable.endswith('d'):
                                app.selected = rgbVal
                        else:
                            if variable == 'hint':
                                app.hint = rgbVal
                            elif variable == 'wrong':
                                app.wrong = rgbVal
                            elif variable == 'initialVal':
                                app.initialVal = rgbVal
                            elif variable == 'emptyCell':
                                app.emptyCell = rgbVal
                else:
                    app.prefRectColor = None
            
    if (app.mouseMode == True and app.manualBoard != None) or (app.mouseMode == True and app.difficulty != None):
        if (360 <= mouseX <= 540) and (380 <= mouseY <= 420):
            if app.manualBoard != 'graphic':
                app.allLegals = [[set() for i in range(9)] for j in range(9)]
                makeLegals(app, app.values)
                app.solutionBoard = solveSudoku(app, app.values)
            setActiveScreen('playClickOnly')
    if (0 <= mouseX <= 100) and (app.height-50 <= mouseY <= app.height):
        setActiveScreen('help')

def splash_onKeyPress(app, key):
    if key == 'c':
        if app.competitionMode == True:
            app.competitionMode = False
        else:
            app.competitionMode = True
        print(app.competitionMode)
    if app.manualBoard != None or app.difficulty != None:
        if app.keyboardMode == True:
            if key == 'space':
                setActiveScreen('playKeyOnly')
        elif app.standardMode == True:
            if key == 'enter':
                setActiveScreen('play')
        if key == 'space' or key == 'enter':
            if app.manualBoard != 'graphic':
                app.allLegals = [[set() for i in range(9)] for j in range(9)]
                makeLegals(app, app.values)
                app.solutionBoard = solveSudoku(app, app.values)

def drawIntro(app):
    drawRect(0, 0, app.width, app.height, fill = 'lightblue')
    drawLabel("Welcome to SUDOKU!", app.width//2, app.height//4, size = 30, fill = 'purple', bold = True)
    drawLabel("Select mode: ", 75 + app.width//4, 50 + app.height//4, size = 15, fill = 'blue', bold = True)
    drawRect(387, 239, 85, 24, fill = app.mouseRectColor)
    drawRect(487, 239, 105, 24, fill = app.keyboardRectColor)
    drawRect(603, 239, 75, 24, fill = app.standardRectColor)
    drawLabel("Mouse-only", 180 + app.width//4, 50 + app.height//4, size = 15)
    drawLabel("Keyboard-only", 290 + app.width//4, 50 + app.height//4, size = 15)
    drawLabel("Standard", 390 + app.width//4, 50 + app.height//4, size = 15)

    drawLabel("Select difficulty:", 42 + app.width//4, 100 + app.height//4, size = 15, bold = True)

    drawRect(365, 288, 45, 24, fill = app.easyRectColor)
    drawRect(427, 288, 62, 24, fill = app.mediumRectColor)
    drawRect(520, 288, 40, 24, fill = app.hardRectColor)
    drawRect(582, 288, 50, 24, fill = app.expertRectColor)
    drawRect(653, 288, 50, 24, fill = app.evilRectColor)

    drawLabel("Easy", 140 + app.width//4, 100 + app.height//4, size = 15)
    drawLabel("Medium", 210 + app.width//4, 100 + app.height//4, size = 15)
    drawLabel("Hard", 290 + app.width//4, 100 + app.height//4, size = 15)
    drawLabel("Expert", 360 + app.width//4, 100 + app.height//4, size = 15)
    drawLabel("Evil", 430 + app.width//4, 100 + app.height//4, size = 15)

    drawLabel('Enter a board (Optional):', 15 + app.width//4, 150 + app.height//4, size = 15, fill = 'red', bold = True)
    drawRect(355, 339, 90, 24, fill = app.graphicRectColor)
    drawRect(445, 339, 180, 24, fill = app.fileRectColor)
    drawRect(630, 339, 120, 24, fill = app.prefRectColor)
    drawLabel('Graphically', 150 + app.width//4, 150 + app.height//4, size = 15)
    drawLabel('File (Path shown in Help)', 285 + app.width//4, 150 + app.height//4, size = 15)
    drawLabel('Preferences File', 690, 150 + app.height//4, size = 15)
    drawLabel('HELP', 50, app.height - 25, size = 30, bold = True, fill = app.helpLabelColor)

    if app.fileNotFound == True:
        drawLabel("File not found", app.width/2, 400, size = 20, bold = True)

    if (app.manualBoard != None or app.difficulty != None) and (app.fileNotFound == False):
        if app.mouseMode == True:
            drawLabel("Click here to play", app.width/2, 400, size = 20, bold = True,
                    fill = app.clickLabelColor)
        elif app.keyboardMode == True:
            drawLabel("Press space to play", app.width/2, 400, size = 20, bold = True)
        elif app.standardMode == True:
            drawLabel("Press enter to play", app.width/2, 400, size = 20, bold = True)
    
    #https://www.cs.cmu.edu/~112-3/notes/term-project.html
    if app.sprites != None:
        sprite = app.sprites[app.spriteCounter]
        drawImage(sprite, app.width/2, 600, align='center')

def playClickOnly_onAppStart(app):
    app.width = 1000
    app.height = 800
    app.rows = 9
    app.cols = 9
    app.boardLeft = app.width//5
    app.boardTop = app.height//7
    app.boardWidth = 600
    app.boardHeight = 600
    app.cellBorderWidth = 2
    app.values = None
    app.mutatedValues = None
    app.selection = None

    app.cellIndex = None
    app.cellSize = 50
    app.selectedClickCell = None
    app.selectedColorClickCell = None
    app.clickHereColor = 'black'

def convertToString(app):
    for row in range(app.rows):
        for col in range(app.cols):
            app.stringSolution += (str(app.mutatedValues[row][col]) + ' ')
        app.stringSolution += '\n'

def playClickOnly_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill = 'tan')
    if app.gameOver == True:
        if app.mutatedValues == app.solutionBoard:
            drawLabel("Congrats! You solved the puzzle!", app.width/2, 60, size = 30, bold = True)
            drawRect(0, 0, app.width, app.height, fill = 'lightgreen')
            if app.competitionMode == True:
                writeFile('Downloads\\15112 Sudoku Term Project\\solvedBoard.txt', app.stringSolution)
        elif app.mutatedValues != app.solutionBoard:
            drawLabel("Game over :(", app.width/2, 60, size = 30, bold = True)
            drawRect(0, 0, app.width, app.height, fill = 'red')

    drawBoard(app)
    drawButtons(app)

    if app.difficulty != None or app.manualBoard != None:
        drawInitialValues(app)

    if app.selectingVals:
        drawLabel('Click here when ready', app.width/2, 85, bold = True, size = 17, fill = app.clickHereColor)
    if app.manualMode == True:
        drawLabel("Manual legals edit is on", app.width/2, app.boardTop - 20, size = 20)
    if app.noSingletons == True:
        drawLabel('No singletons found', app.width/2, app.boardTop - 30, size = 17, bold = True)
    
    if app.selectingVals == False and app.mutatedValues != None:
        makeLegals(app, app.mutatedValues)
        for row in range(app.rows):
            for col in range(app.cols):
                    if app.mutatedValues[row][col] == 0:
                        legalList = make2DLegalList(app, row, col)
                        drawLegals(app, row, col, legalList)

def getClickCell(app, mouseX, mouseY):
    for i in range(len(app.cells)):
        xLeft = 30 + app.cellSize*i
        xRight = (app.cellSize + 30) + app.cellSize*i
        yTop = 730
        yBottom = 780
        
        if (xLeft <= mouseX <= xRight) and (yTop <= mouseY <= yBottom):
            app.selectedClickCell = i
            return i

def playClickOnly_onMousePress(app, mouseX, mouseY):
    mousePress(app, mouseX, mouseY)
    if app.selection != None:
        row, col = app.selection
        app.selectedRow, app.selectedCol = row, col
        app.selectedBlock = findBlock(row, col)
    else:
        app.selectedRow, app.selectedCol, app.selectedBlock = None, None, None
    if app.cellIndex != None and app.gameOver != True:
        keyPress(app, app.cells[app.cellIndex])

def playClickOnly_onMouseMove(app, mouseX, mouseY):
    mouseMove(app, mouseX, mouseY)

def playKeyOnly_onAppStart(app):
    app.width = 1000
    app.height = 800
    app.rows = 9
    app.cols = 9
    app.boardLeft = app.width//5
    app.boardTop = app.height//7
    app.boardWidth = 600
    app.boardHeight = 600
    app.cellBorderWidth = 2
    app.stringSolution = ""

def playKeyOnly_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill = 'tan')
    if app.gameOver == True:
        if app.mutatedValues == app.solutionBoard:
            drawLabel("Congrats! You solved the puzzle!", app.width/2, 60, size = 30, bold = True)
            drawRect(0, 0, app.width, app.height, fill = 'lightgreen')
            if app.competitionMode == True:
                writeFile('Downloads\\15112 Sudoku Term Project\\solvedBoard.txt', app.stringSolution)
        elif app.mutatedValues != app.solutionBoard:
            drawLabel("Game over :(", app.width/2, 60, size = 30, bold = True)
            drawRect(0, 0, app.width, app.height, fill = 'red')
    drawBoard(app)
    if app.difficulty != None or app.manualBoard != None:
        drawInitialValues(app)
    if app.gameOver == True:
        if app.mutatedValues == app.solutionBoard:
            drawLabel("Congrats! You solved the puzzle!", app.width/2, 60, size = 30, bold = True)
            if app.competitionMode == True:
                writeFile('Downloads\\15112 Sudoku Term Project\\solvedBoard.txt', app.stringSolution)
        else:
            drawLabel("Game over :(", app.width/2, 60, size = 30, bold = True)
    if app.selectingVals:
        drawLabel('Press enter when ready', app.width/2, 85, bold = True, size = 17)
    if app.manualMode == True:
        drawLabel("Manual legals edit is on", app.width/2, app.boardTop - 20, size = 20)
    if app.noSingletons == True:
        drawLabel('No singletons found', app.width/2, app.boardTop - 30, size = 17, bold = True)
    
    if app.selectingVals == False and app.mutatedValues != None:
        makeLegals(app, app.mutatedValues)
        for row in range(app.rows):
            for col in range(app.cols):
                    if app.mutatedValues[row][col] == 0:
                        legalList = make2DLegalList(app, row, col)
                        drawLegals(app, row, col, legalList)

def playKeyOnly_onKeyPress(app, key):
    if not app.gameOver:
        keyPress(app, key)

def moveSelection(app, drow, dcol):
    if app.selection != None:
        selectedRow, selectedCol = app.selection
        newSelectedRow = (selectedRow + drow) % app.rows
        newSelectedCol = (selectedCol + dcol) % app.cols
        app.selection = (newSelectedRow, newSelectedCol)
    else:
        app.selection = (0, 0)

def play_onAppStart(app):
    app.width = 1000
    app.height = 800
    app.boardLeft = app.width//5
    app.boardTop = app.height//7
    app.boardWidth = 600
    app.boardHeight = 600
    app.cellBorderWidth = 2
    app.selection = None
    app.solutionBoard = None

def drawButtons(app):
    drawLabel('HELP', 50, 25, size = 30, bold = True, fill = app.helpLabelColor)
    x0 = 30
    for i in range(len(app.cells)):
        if app.difficulty == 'easy' and (app.cells[i] == 'Single' or app.cells[i] == 'All single'):
            continue
        if app.selectedClickCell != None and i == app.selectedClickCell:
            color = 'yellow'
        else:
            color = 'lightYellow'
        drawRect(x0, 730, app.cellSize, app.cellSize, border = 'salmon',
            fill = color)
        if (app.cells[i] == 'Auto' or app.cells[i] == 'Manual' or app.cells[i] == 'Single' 
            or app.cells[i] == 'Undo' or app.cells[i] == 'Redo' or app.cells[i] == 'Hint' or app.cells[i] == 'HINT'):
            labelSize = 12
        elif app.cells[i] == 'All single' or app.cells[i] == 'Rotate':
            labelSize = 11
        else:
            labelSize = 20
        drawLabel(app.cells[i], x0 + app.cellSize/2, 730 + app.cellSize/2, size = labelSize, bold = True)
        x0 += app.cellSize
    if app.difficulty != 'easy':
        drawRect(30, 730, 950, 50, fill = None, border = 'salmon', borderWidth = 4)
    else:
        drawRect(30, 730, 850, 50, fill = None, border = 'salmon', borderWidth = 4)
    
def play_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill = 'tan')
    if app.gameOver == True:
        if app.mutatedValues == app.solutionBoard:
            drawLabel("Congrats! You solved the puzzle!", app.width/2, 60, size = 30, bold = True)
            drawRect(0, 0, app.width, app.height, fill = 'lightgreen')
            if app.competitionMode == True:
                writeFile('Downloads\\15112 Sudoku Term Project\\solvedBoard.txt', app.stringSolution)
        elif app.mutatedValues != app.solutionBoard:
            drawLabel("Game over :(", app.width/2, 60, size = 30, bold = True)
            drawRect(0, 0, app.width, app.height, fill = 'red')
            
    drawBoard(app)
    drawButtons(app)

    if app.manualBoard != None or app.difficulty != None:
        drawInitialValues(app)
        if app.gameOver == True:
            if app.mutatedValues == app.solutionBoard:
                drawLabel("Congrats! You solved the puzzle!", app.width/2, 60, size = 30, bold = True)
                if app.competitionMode == True:
                    writeFile('Downloads\\15112 Sudoku Term Project\\solvedBoard.txt', app.stringSolution)
            else:
                drawLabel("Game over :(", app.width/2, 60, size = 30, bold = True)
    if app.selectingVals:
        drawLabel('Press enter when ready', app.width/2, 85, bold = True, size = 17)
    if app.manualMode == True:
        drawLabel("Manual legals edit is on", app.width/2, app.boardTop - 20, size = 20)
    if app.noSingletons == True:
        drawLabel('No singletons found', app.width/2, app.boardTop - 30, size = 17, bold = True)
    
    if app.selectingVals == False and app.mutatedValues != None:
        makeLegals(app, app.mutatedValues)
        for row in range(app.rows):
            for col in range(app.cols):
                    if app.mutatedValues[row][col] == 0:
                        legalList = make2DLegalList(app, row, col)
                        drawLegals(app, row, col, legalList)

def play_onMouseMove(app, mouseX, mouseY):
    mouseMove(app, mouseX, mouseY)

def mouseMove(app, mouseX, mouseY):       
    selectedCell = getClickCell(app, mouseX, mouseY)
    if selectedCell != None:
        if selectedCell == app.cellIndex:
            app.cellIndex = None
        else:
            app.cellIndex = selectedCell
    
    if (0 <= mouseX <= 100) and (0 <= mouseY <= 50):
        app.helpLabelColor = 'red'
    else:
        app.helpLabelColor = 'black'
    if (350 <= mouseX <= 550) and (60 <= mouseY <= 110):
        app.clickHereColor = 'red'
    else:
        app.clickHereColor = 'black'

def play_onMousePress(app, mouseX, mouseY):
    mousePress(app, mouseX, mouseY)
    if app.selection != None:
        row, col = app.selection
        app.selectedRow, app.selectedCol = row, col
        app.selectedBlock = findBlock(row, col)
    else:
        app.selectedRow, app.selectedCol, app.selectedBlock = None, None, None
    if app.cellIndex != None and app.gameOver != True:
        keyPress(app, app.cells[app.cellIndex])

def mousePress(app, mouseX, mouseY):
    if (0 <= mouseX <= 125) and (0 <= mouseY <= 50):
        setActiveScreen('help')
    selectedCell = getCell(app, mouseX, mouseY)
    if selectedCell != None:
        if selectedCell == app.selection:
            app.selection = None
        else:
            app.selection = selectedCell

    app.cellIndex = getClickCell(app, mouseX, mouseY)

    if (350 <= mouseX <= 550) and (60 <= mouseY <= 110):
            app.selectingVals = False

def play_onKeyPress(app, key):
    if not app.gameOver:
        keyPress(app, key)

def keyPress(app, num):
    app.noSingletons = False
    if num == 'left':    
        moveSelection(app, 0, -1)
    elif num == 'right': 
        moveSelection(app, 0, +1)
    elif num == 'up':    
        moveSelection(app ,-1, 0)
    elif num == 'down':  
        moveSelection(app, +1, 0)
    if num == 'a' or num == 'Auto':
        if app.autoMode == True:
            app.autoMode = False
        else:
            app.autoMode = True
    elif num == 'm' or num == 'Manual':
        if app.manualMode == True:
            app.manualMode = False
        else:
            app.manualMode = True
    elif (num == 't' or num == 'Rotate') and app.manualMode == False and app.solutionBoard != None:
        app.mutatedValues = rotateBoard(app, app.mutatedValues)
        app.values = rotateBoard(app, app.values)
        app.allLegals = rotateBoard(app, app.allLegals)
        app.manualLegals = rotateBoard(app, app.manualLegals)
        app.solutionBoard = rotateBoard(app, app.solutionBoard)

        app.undoList = rotateUndoRedo(app, app.undoList)
        app.undoLegalList = rotateUndoRedo(app, app.undoLegalList)
        app.undoneWrong = rotateUndoRedo(app, app.undoneWrong)
        app.redoList = rotateUndoRedo(app, app.redoList)

        app.seenMoves = rotateCells(app, app.seenMoves)
        app.tupleLocations = rotateCells(app, app.tupleLocations)
        app.singletonLocations = rotateCells(app, app.singletonLocations)
        app.removedSingletonLocations = rotateCells(app, app.removedSingletonLocations)
        app.singleRowCol = rotateCells(app, app.singleRowCol)
        app.wrongValues = rotateCells(app, app.wrongValues)
        app.selection = rotateCells(app, app.selection)

    elif (num == 'u' or num == 'Undo') and app.manualMode == False:
        if app.undoList != []:
            val, undoRow, undoCol = app.undoList.pop()
            app.selection = (undoRow, undoCol)
            app.redoList.append((val, undoRow, undoCol))
            if app.seenMoves.count((undoRow, undoCol)) == 1:
                app.mutatedValues[undoRow][undoCol] = 0
            else:
                app.mutatedValues[undoRow][undoCol] = val

            if app.solutionBoard != None and val == app.solutionBoard[undoRow][undoCol] and (undoRow, undoCol) in app.wrongValues:
                app.wrongValues.remove((undoRow, undoCol))
                app.undoneWrong.add((undoRow, undoCol)) 
            elif val != app.solutionBoard[undoRow][undoCol] and (undoRow, undoCol) not in app.wrongValues:
                app.wrongValues.add((undoRow, undoCol))
            
            if (undoRow, undoCol) in app.wrongValues and app.seenMoves.count((undoRow, undoCol)) == 1:
                app.wrongValues.remove((undoRow, undoCol))
                app.undoneWrong.add((undoRow, undoCol)) 

            if app.seenMoves != []:
                app.seenMoves.pop()    

    elif (num == 'r' or num == 'Redo') and app.manualMode == False:
        if app.redoList != []:
            val, redoRow, redoCol = app.redoList.pop()
            app.selection = (redoRow, redoCol)
            app.undoList.append((val, redoRow, redoCol))
            app.mutatedValues[redoRow][redoCol] = val
            app.seenMoves.append((redoRow, redoCol))
            if (redoRow, redoCol) in app.undoneWrong:
                app.wrongValues.add((redoRow, redoCol))

    elif app.difficulty != 'easy' and app.competitionMode != True and (num == 's' or num == 'Single'):
        getSingletons(app)
    elif app.difficulty != 'easy' and app.competitionMode != True and (num == 'S' or num == 'All single'):
        app.allSingletons = True
        getSingletons(app)
        app.allSingletons = False
    elif (num == 'h' or num == 'Hint') and app.competitionMode == False:
        app.setMode = False
        generateHint(app)

    elif (num == 'H'or num == 'HINT') and app.competitionMode == False:
        app.setMode = True
        generateHint(app)

    elif num == 'escape':
        setActiveScreen('help')

    if app.selection != None:
        row, col = app.selection
        app.selectedRow, app.selectedCol = row, col
        app.selectedBlock = findBlock(row, col)
        if app.selectingVals:
            if num == '1' or num == '2' or num == '3' or num == '4' or num == '5' or num == '6' or num == '7' or num == '8' or num == '9':
                app.values[row][col] = int(num)
            elif num == 'backspace':
                app.values[row][col] = 0
            app.mutatedValues = copy.deepcopy(app.values)
            if num == 'enter':
                app.selectingVals = False
                makeLegals(app, app.mutatedValues)
                app.solutionBoard = solveSudoku(app, app.values)
                if app.solutionBoard == None:
                    app.cantSolveBoard = True

        elif app.values[row][col] == 0 and app.manualMode == False:
            if num == '1' or num == '2' or num == '3' or num == '4' or num == '5' or num == '6' or num == '7' or num == '8' or num == '9':
                app.redoList = []
                if (int(num), row, col) not in app.undoList:
                    app.seenMoves.append((row, col))
                    app.undoList.append((int(num), row, col))

                if (row, col) in app.undoneWrong:
                    app.undoneWrong.remove((row, col))
                app.movesBoard[row][col] = int(num)

                block = findBlock(row, col)
                legalList = getBlock(app, block)
                app.mutatedValues[row][col] = int(num)
                if (row, col) == app.singleRowCol:
                    app.singleRowCol = None
                    app.singletonLocations = set()
                app.editLegals = [[set() for i in range(9)] for j in range(9)]


                if app.selection == app.singleRowCol:
                    app.singleRowCol = None

                if app.solutionBoard != None:
                    if app.mutatedValues[row][col] != app.solutionBoard[row][col]:
                        if app.competitionMode == True:
                            app.gameOver = True
                        else:
                            app.wrongValues.add((row, col))
                    elif (row, col) in app.wrongValues:
                        app.wrongValues.remove((row, col))

            elif num == 'backspace' or num == 'X':
                val = app.mutatedValues[row][col]
                app.mutatedValues[row][col] = 0
                if (row, col) in app.wrongValues:
                    app.wrongValues.remove((row, col))
                if (val, row, col) in app.undoList:
                    app.undoList.remove((val, row, col))
                if (val, row, col) in app.redoList:
                    app.redoList.remove((val, row, col))

        elif app.manualMode == True:
            if num == '1' or num == '2' or num == '3' or num == '4' or num == '5' or num == '6' or num == '7' or num == '8' or num == '9':
                app.redoLegalList = []
                if app.autoMode == True:
                    if int(num) in app.allLegals[row][col]:
                        app.allLegals[row][col].remove(int(num))
                        app.allLegalsRemoved[row][col].add(int(num))
                        if int(num) == app.solutionBoard[row][col]:
                            app.wrongValues.add((row, col))
                    else:
                        app.allLegals[row][col].add(int(num))
                        if int(num) in app.allLegalsRemoved[row][col]:
                            app.allLegalsRemoved[row][col].remove(int(num))
                        if (row, col) in app.wrongValues:
                            app.wrongValues.remove((row, col))
                    

                    if int(num) in app.editLegals[row][col]:
                        app.editLegals[row][col].remove(int(num))
                    else:
                        app.editLegals[row][col].add(int(num))
                else:
                    if int(num) in app.manualLegals[row][col]:
                        app.manualLegals[row][col].remove(int(num))
                    else:
                        app.manualLegals[row][col].add(int(num))

                app.undoRedoLegals[row][col].add(int(num))
                app.undoLegalList.append((int(num), row, col))

            elif num == 'u' or num == 'Undo':
                if app.undoLegalList != []:
                    val, undoRow, undoCol = app.undoLegalList.pop()
                    app.redoLegalList.append((val, undoRow, undoCol))
                    if app.autoMode == True:
                        if val in app.allLegals[undoRow][undoCol]:
                            app.allLegals[undoRow][undoCol].remove(val)
                            if val in app.editLegals[undoRow][undoCol]:
                                app.editLegals[undoRow][undoCol].remove(val)
                        else:
                            app.allLegals[undoRow][undoCol].add(val)
                            app.editLegals[undoRow][undoCol].add(val)
                        for m in app.editLegals[undoRow][undoCol]:
                            app.allLegals[undoRow][undoCol].add(m)

                        if val == app.solutionBoard and (undoRow, undoCol) in app.wrongValues:
                            app.wrongValues.add((undoRow, undoCol))
                        elif val != app.solutionBoard and (undoRow, undoCol) in app.wrongValues:
                            app.wrongValues.remove((undoRow, undoCol))
                        app.selection = (undoRow, undoCol)
                    else:
                        if val in app.manualLegals[undoRow][undoCol]:
                            app.manualLegals[undoRow][undoCol].remove(val)    
                        else:
                            app.manualLegals[undoRow][undoCol].add(val)
                        app.selection = (undoRow, undoCol)
                        if (undoRow, undoCol) in app.wrongValues:
                            app.wrongValues.remove((undoRow, undoCol))
                            app.undoneWrongLegals.add((undoRow, undoCol))             

            elif num == 'r' or num == 'Redo':
                if app.redoLegalList != []:
                    val, redoRow, redoCol = app.redoLegalList.pop()
                    app.undoLegalList.append((val, redoRow, redoCol))
                    if app.autoMode == True:
                        if val in app.allLegals[redoRow][redoCol]:
                            app.allLegals[redoRow][redoCol].remove(val)
                            app.editLegals[redoRow][redoCol].remove(val)
                        else:
                            app.allLegals[redoRow][redoCol].add(val)
                            app.editLegals[redoRow][redoCol].add(val)
                        for m in app.editLegals[row][col]:
                            app.allLegals[row][col].add(m)
                        app.selection = (redoRow, redoCol)
                    else:
                        if val in app.manualLegals[redoRow][redoCol]:
                            app.manualLegals[redoRow][redoCol].remove(val)
                        else:
                            app.manualLegals[redoRow][redoCol].add(val)
                            app.allLegals[redoRow][redoCol].add(val)
                        app.selection = (redoRow, redoCol)
                        if (redoRow, redoCol) in app.undoneWrongLegals:
                            app.wrongValues.add((redoRow, redoCol))

    if app.manualBoard == None:
        rows, cols = len(app.mutatedValues), len(app.mutatedValues[0])
        if noZeros(app.mutatedValues, rows, cols) and app.wrongValues == set():
            app.gameOver = True
            convertToString(app)

def drawInitialValues(app):
    rows, cols = len(app.mutatedValues), len(app.mutatedValues[0])
    cellWidth, cellHeight = getCellSize(app)
    numLeft = app.boardLeft + cellWidth/2
    numTop = app.boardTop + cellHeight/2
    for row in range(rows):
        for col in range(cols):
            if col == 0:
                cx = numLeft
                cy = numTop
            else:
                cx = numLeft + cellWidth
                cy = numTop
                numLeft += cellWidth
            initialValue = app.mutatedValues[row][col]
            if initialValue == 0:
                continue
            drawLabel(initialValue, cx, cy, size = 35, bold = True)
        numLeft = app.boardLeft + cellWidth/2
        numTop += cellHeight
    return

#from https://cs3-112-f22.academy.cs.cmu.edu/notes/4187
def drawBoard(app):
    for row in range(app.rows):
        for col in range(app.cols):
            drawCell(app, row, col)
    drawBoardBorder(app)
    drawBlock(app)

#from https://cs3-112-f22.academy.cs.cmu.edu/notes/4187
def drawBlock(app):
    blockTop, blockLeft = app.boardTop, app.boardLeft
    newBlockRow = 0
    for block in range(9):
        if block != 0 and block % 3 == 0:
            blockTop += app.boardHeight//3
            newBlockRow = blockTop
        elif block < 3:
            blockTop = app.boardTop 
        else:
            blockTop = newBlockRow

        if block % 3 == 0:          
            blockLeft = app.boardLeft
        else:
            blockLeft += app.boardWidth//3

        drawRect(blockLeft, blockTop, app.boardWidth//3, app.boardHeight//3,
                 fill = None, border = 'brown', borderWidth = 2.5*app.cellBorderWidth)

#from https://cs3-112-f22.academy.cs.cmu.edu/notes/4187
def drawBoardBorder(app):
    drawRect(app.boardLeft, app.boardTop, app.boardWidth, app.boardHeight,
             fill = None, border = 'brown', borderWidth = 5*app.cellBorderWidth)

#from https://cs3-112-f22.academy.cs.cmu.edu/notes/4187
def drawCell(app, row, col):
    cellLeft, cellTop = getCellLeftTop(app, row, col)
    cellWidth, cellHeight = getCellSize(app)
    block = findBlock(row, col)
    if (row == app.selectedRow or col == app.selectedCol or block == app.selectedBlock):
        color = rgb(153, 255, 255) #'cyan'
    else:
        color = app.emptyCell
    if (row, col) == app.selection:
        if app.selection == app.singleRowCol or app.selection in app.tupleLocations:
            color = app.selectedHint #'lightGreen'
        else:
            color = app.selected #'orange'
        if (row, col) in app.wrongValues:
            color = app.selectedWrong #lightRed
        elif app.values[row][col] != 0:
            color = app.selectedInitialVal #lightGrey
    elif (row, col) in app.wrongValues:
        color = app.wrong #'red'
    elif app.values != None and app.values[row][col] != 0:
        color = app.initialVal #darkGrey
    elif (row, col) == app.aloneRowCol or (row, col) == app.singleRowCol or (row, col) in app.tupleLocations:
        color = app.hint #green

    drawRect(cellLeft, cellTop, cellWidth, cellHeight, border = 'brown',
             fill = color, borderWidth = app.cellBorderWidth)

def getSingletons(app):
    singletonList = []
    rows, cols = len(app.allLegals), len(app.allLegals[0])
    for row in range(rows):
        for col in range(cols):
            if len(app.allLegals[row][col]) == 1:
                singleton = app.allLegals[row][col].pop()
                singletonList.append(singleton)
                app.mutatedValues[row][col] = singleton
                app.undoList.append((singleton, row, col))
                app.seenMoves.append((row, col))
                if app.allSingletons == False:
                    return
    if singletonList == []:
        app.noSingletons = True

def generateHint(app):
    app.allNakedTuples, app.allNakedTupleLocations = [], []
    tupleRows, tupleCols, tupleBlocks = set(), set(), set()
    app.tupleRows, app.tupleCols, app.tupleBlock = set(), set(), set()

    if app.setMode == True:
        app.aloneRowCol = getAloneLegal(app)
        if app.aloneRowCol == None:
            app.singleRowCol = getNakedSingle(app)
            if app.singleRowCol == None:
                getNakedTuple(app)
            else:
                singleRow, singleCol = app.singleRowCol
                if app.allLegals[singleRow][singleCol] != set() and (singleRow, singleCol) not in app.removedSingletonLocations:
                    singleton = app.allLegals[singleRow][singleCol].pop()
                    app.mutatedValues[singleRow][singleCol] = singleton
                if (singleRow, singleCol) in app.singletonLocations:
                    app.singletonLocations.remove((singleRow, singleCol))
        else:
            aloneRow, aloneCol = app.aloneRowCol
            app.mutatedValues[aloneRow][aloneCol] = app.aloneLegal
    else:
        app.singleRowCol = getNakedSingle(app)
        if app.singleRowCol == None:
            getNakedTuple(app)
    
    if app.singleRowCol == None:
        for cell in app.tupleLocations:
            row, col = cell
            tupleRows.add(row)
            tupleCols.add(col)
            tupleBlocks.add(findBlock(row, col))
            block = findBlock(row, col)

            if len(tupleRows) == 1:
                app.tupleRows.add(row)
            else:
                app.tupleRows = set()
            if len(tupleCols) == 1:
                app.tupleCols.add(col)
            else:
                app.tupleCols = set()
            if len(tupleBlocks) == 1:
                app.tupleBlock.add(block)
            else:
                app.tupleBlock = set()
            if app.tupleRows == set() and app.tupleCols == set() and app.tupleBlock == set():
                generateHint(app)

def getAloneLegal(app):
    rows, cols = len(app.allLegals), len(app.allLegals[0])
    allLegals = copy.deepcopy(app.allLegals)
    seen = set()
    for row in range(rows):
        seen = set()
        for col in range(cols):
            for legal in range(1, 10):
                if legal in allLegals[row][col]:
                    if legal not in seen:
                        seen.add(legal)
                    else:
                        allLegals[row][col].remove(legal)
        if allLegals[row][col] != set() and app.mutatedValues[row][col] == 0 and len(app.allLegals[row][col]) != 1:
            app.aloneLegal = allLegals[row][col].pop()
            app.aloneRowCol = (row, col)
            return app.aloneRowCol
    return None

def getNakedSingle(app):
    rows, cols = len(app.allLegals), len(app.allLegals[0])
    for row in range(rows):
        for col in range(cols):
            if ((row, col) not in app.removedSingletonLocations) and app.mutatedValues[row][col] == 0 and len(app.allLegals[row][col]) == 1:
                app.singletonLocations.add((row, col))

            elif (row, col) in app.singletonLocations:
                app.singletonLocations.remove((row, col))
    if app.singletonLocations != set():
        return random.choice(list(app.singletonLocations))
    return None

def getNakedTuple(app):
    hasValue = False
    for N in range(2, 6):
        for region in app.regions:
            for targetCells in itertools.combinations(region, N):
                for (row, col) in targetCells:
                    if app.mutatedValues[row][col] != 0:
                        hasValue = True

                if hasValue != True:
                    app.nakedTuple = set()
                    app.tupleLocations = []
                    
                    for i in range(len(targetCells)):
                        targetRow, targetCol = targetCells[i]
                        for legal in app.allLegals[targetRow][targetCol]:
                            app.nakedTuple.add(legal)

                    if len(app.nakedTuple) == N and len(targetCells) == N:
                        app.tupleLocations = list(targetCells)
                        return
                app.nakedTuple = set()
                app.tupleLocations = []
                hasValue = False

def makeRegionList(app):
    for row in range(app.rows):
        for col in range(app.cols):
            app.rowList.append((row, col))
            if col == 8:
                app.regions.append(app.rowList)
                app.rowList = []
    
    for col in range(app.cols):
        for row in range(app.rows):
            app.colList.append((row, col))
            if row == 8:
                app.regions.append(app.colList)
                app.colList = []
    
    
    for startRow in range(0, 7, 3):
        for startCol in range(0, 7, 3):
            for i in range(3):
                for j in range(3):
                    blockRow, blockCol = startRow + i, startCol + j
                    app.blockList.append((blockRow, blockCol))
            app.regions.append(app.blockList)
            app.blockList = []
    return app.regions

def makeLegals(app, boardValues):
    for row in range(app.rows):
        for col in range(app.cols):
            if boardValues[row][col] == 0:
                block = findBlock(row, col)
                legalList = getBlock(app, block)
                for n in range(1, 10):
                    if ((app.manualMode == False) and (n not in legalList) and 
                        (n not in boardValues[row]) and (n not in [boardValues[row][col] for row in range(len(boardValues))]) and
                        (n not in app.allLegalsRemoved[row][col])):
                        app.allLegals[row][col].add(n)
                    elif app.manualMode == False and (n in app.allLegals[row][col]):
                        app.allLegals[row][col].remove(n)

                    if app.setMode == True: 
                        removedLegals = set()
                        if (n in app.nakedTuple):
                            if (row, col) not in app.tupleLocations and (row in app.tupleRows or col in app.tupleCols or block in app.tupleBlock):
                                if n in app.allLegals[row][col]:
                                    app.allLegals[row][col].remove(n)
                                    removedLegals.add(n)

                for m in app.editLegals[row][col]:
                    app.allLegals[row][col].add(m)
    return app.allLegals

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

def make2DLegalList(app, row, col):
    allLegals = [[set() for i in range(9)] for j in range(9)]
    legalList = [0 for i in range(9)]
    legal2DList = []
    rowList = []

    if app.autoMode == True:
        for n in range(1, 10):
            if n in app.allLegalsRemoved[row][col] and n in app.allLegals[row][col]:
                app.allLegals[row][col].remove(n)
            allLegals[row][col] = app.allLegals[row][col]
    else:
        allLegals = app.manualLegals

    for legal in allLegals[row][col]:
        legalList[legal-1] = legal
    
    for i in range(len(legalList)):
        if i != 0 and i % 3 == 0:
            legal2DList.append(rowList)
            rowList = []
        rowList.append(legalList[i])
    legal2DList.append(rowList)
    return legal2DList

def drawLegals(app, row, col, legal2DList):
    cellWidth, cellHeight = getCellSize(app)
    cellLeft, cellTop = getCellLeftTop(app, row, col)
    numLeft = cellLeft + cellWidth/4
    numTop = cellTop + cellHeight/4.5
    rows, cols = len(legal2DList), len(legal2DList[0])
    for row1 in range(rows):
        for col1 in range(cols):
            if col1 == 0:
                cx = numLeft
                cy = numTop
            else:
                cx = numLeft + cellWidth/4
                cy = numTop
                numLeft += cellWidth/4
            if legal2DList[row1][col1] != 0:
                drawLabel(f'{legal2DList[row1][col1]}', cx, cy+2, size = 12, fill = 'gray', bold = True)
        numLeft = cellLeft + cellWidth/4
        numTop += cellHeight/4.5

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

def getTupleBlock(app, grid, block):
    n = len(grid)
    blockSize = int(n**0.5)
    startRow = block // blockSize * blockSize
    startCol = block % blockSize * blockSize
    values = []
    for drow in range(blockSize):
        for dcol in range(blockSize):
            row, col = startRow + drow, startCol + dcol
            app.tupleBlock.add((row, col))

#from https://cs3-112-f22.academy.cs.cmu.edu/notes/4187
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

#from https://cs3-112-f22.academy.cs.cmu.edu/notes/4187
def getBlockRowCol(app, block):
    n = len(app.mutatedValues)
    blockSize = int(n**0.5)
    startRow = block // blockSize * blockSize
    startCol = block % blockSize * blockSize
    return startRow, startCol

#from https://cs3-112-f22.academy.cs.cmu.edu/notes/4187
def getCell(app, x, y):
    dx = x - app.boardLeft
    dy = y - app.boardTop
    cellWidth, cellHeight = getCellSize(app)
    row = math.floor(dy / cellHeight)
    col = math.floor(dx / cellWidth)
    if (0 <= row < app.rows) and (0 <= col < app.cols):
        return (row, col)
    else:
        return None

#from https://cs3-112-f22.academy.cs.cmu.edu/notes/4187
def getCellLeftTop(app, row, col):
    cellWidth, cellHeight = getCellSize(app)
    cellLeft = app.boardLeft + col*cellWidth
    cellTop = app.boardTop + row*cellHeight
    return (cellLeft, cellTop)

#from https://cs3-112-f22.academy.cs.cmu.edu/notes/4187
def getCellSize(app):
    cellWidth = app.boardWidth / app.cols
    cellHeight = app.boardHeight / app.rows
    return (cellWidth, cellHeight)
    
def main():
    runAppWithScreens(initialScreen = 'splash')
main()