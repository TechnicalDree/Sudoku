from mainSudoku import *

L = [[0, 0, 5, 0, 0, 0, 0, 7, 0], [7, 6, 3, 0, 1, 0, 4, 0, 0], [0, 2, 8, 4, 0, 0, 5, 6, 0], [1, 0, 7, 6, 0, 0, 8, 0, 2], [0, 8, 0, 3, 7, 0, 0, 0, 6], [0, 0, 6, 8, 2, 1, 0, 0, 5], [0, 7, 0, 0, 5, 3, 9, 0, 0], [0, 3, 0, 9, 6, 0, 0, 0, 0], [5, 4, 0, 7, 8, 0, 0, 0, 3]]

def main():
    print(solveSudoku(app, L))

if __name__=="__main__":
    main()