#!/usr/bin/env python
import struct, string, math, copy
import time

class SudokuBoard:
    """This will be the sudoku board game object your player will manipulate."""
  
    def __init__(self, size, board, forward_checking_board=[]):
      """the constructor for the SudokuBoard"""
      self.BoardSize = size #the size of the board
      self.CurrentGameBoard= board #the current state of the game board
      self.ForwardingCheckingBoard = forward_checking_board
  

    def set_value(self, row, col, value):
        """This function will create a new sudoku board object with the input
        value placed on the GameBoard row and col are both zero-indexed"""

        #add the value to the appropriate position on the board
        self.CurrentGameBoard[row][col]=value
        #return a new board of the same size with the value added
        return SudokuBoard(self.BoardSize, self.CurrentGameBoard, self.ForwardingCheckingBoard)
                                                                  
                                                                  
    def print_board(self):
        """Prints the current game board. Leaves unassigned spots blank."""
        div = int(math.sqrt(self.BoardSize))
        dash = ""
        space = ""
        line = "+"
        sep = "|"
        for i in range(div):
            dash += "----"
            space += "    "
        for i in range(div):
            line += dash + "+"
            sep += space + "|"
        for i in range(-1, self.BoardSize):
            if i != -1:
                print "|",
                for j in range(self.BoardSize):
                    if self.CurrentGameBoard[i][j] > 9:
                        print self.CurrentGameBoard[i][j],
                    elif self.CurrentGameBoard[i][j] > 0:
                        print "", self.CurrentGameBoard[i][j],
                    else:
                        print "  ",
                    if (j+1 != self.BoardSize):
                        if ((j+1)//div != j/div):
                            print "|",
                        else:
                            print "",
                    else:
                        print "|"
            if ((i+1)//div != i/div):
                print line
            else:
                print sep

def parse_file(filename):
    """Parses a sudoku text file into a BoardSize, and a 2d array which holds
    the value of each cell. Array elements holding a 0 are considered to be
    empty."""

    f = open(filename, 'r')
    BoardSize = int( f.readline())
    NumVals = int(f.readline())

    #initialize a blank board
    board= [ [ 0 for i in range(BoardSize) ] for j in range(BoardSize) ]

    #populate the board with initial values
    for i in range(NumVals):
        line = f.readline()
        chars = line.split()
        row = int(chars[0])
        col = int(chars[1])
        val = int(chars[2])
        board[row-1][col-1]=val
    
    return board
    
def is_complete(sudoku_board):
    """Takes in a sudoku board and tests to see if it has been filled in
    correctly."""
    BoardArray = sudoku_board.CurrentGameBoard
    size = len(BoardArray)
    subsquare = int(math.sqrt(size))

    #check each cell on the board for a 0, or if the value of the cell
    #is present elsewhere within the same row, column, or square
    for row in range(size):
        for col in range(size):
            if BoardArray[row][col]==0:
                return False
            for i in range(size):
                if ((BoardArray[row][i] == BoardArray[row][col]) and i != col):
                    return False
                if ((BoardArray[i][col] == BoardArray[row][col]) and i != row):
                    return False
            #determine which square the cell is in
            SquareRow = row // subsquare
            SquareCol = col // subsquare
            for i in range(subsquare):
                for j in range(subsquare):
                    if((BoardArray[SquareRow*subsquare+i][SquareCol*subsquare+j]
                            == BoardArray[row][col])
                        and (SquareRow*subsquare + i != row)
                        and (SquareCol*subsquare + j != col)):
                            return False
    return True

def init_board(file_name):
    """Creates a SudokuBoard object initialized with values from a text file"""
    board = parse_file(file_name)

    return SudokuBoard(len(board), board)


def solve(initial_board, forward_checking = False, MRV = False, MCV = False,
    LCV = False):
    """Takes an initial SudokuBoard and solves it using back tracking, and zero
    or more of the heuristics and constraint propagation methods (determined by
    arguments). Returns the resulting board solution. """

    start = time.time()
    if forward_checking == True:
      initial_board.ForwardingCheckingBoard = initForwardChecking(initial_board)
    else:
      initial_board.ForwardingCheckingBoard = []
    result_board, result = backtrack(initial_board, forward_checking ,MRV,  MCV, LCV)
    print "Using time: ", time.time() - start
    return result_board


def backtrack(board, forward_checking ,MRV, MCV, LCV):
  if is_complete(board) == True:

    return board, True
  #if forward_checking == True:
    
    #board.print_board()
  next_row, next_col = nextEmptyPosition(board, forward_checking, MRV, MCV)
  value_list = possible_value(next_row, next_col, board, forward_checking ,LCV)
  print value_list
  for value in value_list:

    new_board = deepcopy(board)
    new_board.set_value(next_row, next_col, value)
    #board1 = copy.deepcopy(new_board)
    #board2 = copy.copy(new_board)
    #print "-----------------------"
    #print "board = ", board
    #print "new_board = ", new_board
    #print "board1 = ", board1
    #print "board2 = ", board2
    #print "-----------------------"


    if forward_checking == True:
      #checkingBoard(board)
      new_board.ForwardingCheckingBoard = manipulateBoard(new_board.ForwardingCheckingBoard, next_row, next_col, value)
      checkingBoard(new_board)
    temp_board, result = backtrack(new_board, forward_checking, MRV,  MCV, LCV)
    #print "temp_board:", temp_board.print_board
    if result == True:
      print "Success!!!"
      return temp_board, True

  print "fail!!!!!"
  return board, False

def nextEmptyPosition(board, forward_checking, MRV, MCV):
  BoardArray = board.CurrentGameBoard
  size = len(BoardArray)
  subsquare = int(math.sqrt(size))

  min_remain = 10
  prev_min = min_remain
  if(MCV==False and MRV == False):
    for row in range(size):
      for col in range(size):
        if BoardArray[row][col]==0:
          return row, col

  elif MRV == True:
    row = 0
    col = 0
    for i in range(size):
      for j in range(size):
        if BoardArray[i][j] == 0:
          
          value_list = possible_value(i, j, board, False, False)
          if len(value_list) < min_remain:
            row = i
            col = j
            prev_min = min_remain
            min_remain = len(value_list)

  if prev_min == min_remain:
    if MCV == True:
      row = 0
      col = 0
      maxDegree = -1
      for i in range(size):
        for j in range(size):
          if BoardArray[i][j] == 0:
            if forward_checking == True:
              new_degree = board.BoardSize- len(validNumber(board.ForwardingCheckingBoard, i, j))
            else:
              new_degree = degree(i, j, board) 
            if(new_degree > maxDegree):
              row = i
              col = j
              maxDegree = new_degree

  return row, col

def degree(row, col, board):
  BoardArray = board.CurrentGameBoard
  size = len(BoardArray)
  subsquare = int(math.sqrt(size))

  count = 0
  for i in range(size):
    if (BoardArray[row][i] != 0): 
      count += 1
    if (BoardArray[i][col] != 0):
      count += 1


  SquareRow = row // subsquare
  SquareCol = col // subsquare
  for i in range(subsquare):
    for j in range(subsquare):
      if(BoardArray[SquareRow*subsquare+i][SquareCol*subsquare+j]
          != 0):
        count += 1

  return count



def possible_value(row, col, board, forward_checking = False, LCV = False):
  BoardArray = board.CurrentGameBoard
  size = len(BoardArray)
  subsquare = int(math.sqrt(size))

  result = []
  constraint = []

  if forward_checking == True:
    result = validNumber(board.ForwardingCheckingBoard, row, col)
  else:
    for i in range(size):
      constraint.append(i+1)

    temp = copy.deepcopy(constraint)
    for i in range(size):
      if BoardArray[row][i] in temp:
        temp.remove(BoardArray[row][i])
      if BoardArray[i][col] in temp:
        temp.remove(BoardArray[i][col])

    SquareRow = row // subsquare
    SquareCol = col // subsquare
    for i in range(subsquare):
      for j in range(subsquare):
        if(BoardArray[SquareRow*subsquare+i][SquareCol*subsquare+j]
            in temp):
          temp.remove(BoardArray[SquareRow*subsquare+i][SquareCol*subsquare+j])

    result = result + temp
  if LCV == True:
    print "------------"
    print "before re_order_value", result

    re_order_value(row, col, board, result, forward_checking)
    print "after re_order_value", result
    print "------------"
  #print result
  return result

def re_order_value(row, col, board, l, forward_checking):
  if len(l) == 0:
    return []
  index_list = []
  result = []
  BoardArray = board.CurrentGameBoard
  size = len(BoardArray)
  subsquare = int(math.sqrt(size))
  
  for i in range(len(l)):
    index_list.append(0)

  for i in range(size):
    if (BoardArray[row][i] == 0): 
      c = list(set(l) - (set(l) - set(possible_value(row,i,board, forward_checking,False)))) 
      for x in c:
        index_list[l.index(x)] += 1
    if (BoardArray[i][col] == 0): 
      c = list(set(l) - (set(l) - set(possible_value(i, col, board, forward_checking,False)))) 
      for x in c:
        index_list[l.index(x)] += 1

  SquareRow = row // subsquare
  SquareCol = col // subsquare
  for i in range(subsquare):
    for j in range(subsquare):
      if(BoardArray[SquareRow*subsquare+i][SquareCol*subsquare+j] == 0):
        c = list(set(l) - (set(l) - set(possible_value(SquareRow*subsquare+i, SquareCol*subsquare+j, board, forward_checking,False))))
        for x in c:
          index_list[l.index(x)] += 1

  sort_list = copy.deepcopy(index_list)
  sort_list.sort()
  for i in range(len(sort_list)):
    temp = l[index_list.index(sort_list[i])]
    result.append(temp)

  l = result



#------------------------------------------------------------------
def checkingBoard(board):
  """
  Check the ForwardingCheckingBoard to see if there is one cell only contains one possible value, choose it and recursive.
  """
  BoardSize = board.BoardSize
  CurrentBoard = board.CurrentGameBoard
  SquareSize = int(math.sqrt(BoardSize))
  flag = 0

  for i in range(BoardSize):
    for j in range(BoardSize):
      if (board.CurrentGameBoard[i][j] == 0)and(len(board.ForwardingCheckingBoard[i][j]) == 1):
        board.CurrentGameBoard[i][j] = board.ForwardingCheckingBoard[i][j][0]
        board.ForwardingCheckingBoard =  manipulateBoard(board.ForwardingCheckingBoard, i, j, board.ForwardingCheckingBoard[i][j][0])
        flag = 1
        break
    if flag == 1:
      break
  if flag == 1:
    checkingBoard(board)
  else:
    return


def initForwardChecking(board):
    """Takes an SudokuBoard, and initiate an 3-dimentioan Bool array. 
    The size of the Array is BoardSize*BoardSize*BoardSize"""

    BoardSize = board.BoardSize
    CurrentBoard = board.CurrentGameBoard
    SquareSize = int(math.sqrt(BoardSize))

    #initiate an 3-dimentioan Bool array.  
    forward_checking_board =[[ [i+1 for i in range(BoardSize)] for j in range(BoardSize) ] for k in range(BoardSize)]
    
    for i in range(BoardSize):
      for j in range(BoardSize):
        if board.CurrentGameBoard[i][j] != 0:
          #mark the corresponding row&col
          for k in range(BoardSize):
            if forward_checking_board[i][k].count(board.CurrentGameBoard[i][j]) == 1:
              forward_checking_board[i][k].remove(board.CurrentGameBoard[i][j])


            if forward_checking_board[k][j].count(board.CurrentGameBoard[i][j]) == 1:
              forward_checking_board[k][j].remove(board.CurrentGameBoard[i][j])  
                    
          no_of_square_row = i // SquareSize
          no_of_square_col = j // SquareSize

          #mark the correspongding square
          for m in range(no_of_square_row*SquareSize, (no_of_square_row+1)*SquareSize):
            for n in range(no_of_square_col*SquareSize, (no_of_square_col+1)*SquareSize):
              if forward_checking_board[m][n].count(board.CurrentGameBoard[i][j]) == 1:
                forward_checking_board[m][n].remove(board.CurrentGameBoard[i][j])

    return forward_checking_board

def validNumber(forward_checking_board, row, col):
  """
  return a list of numbers that can be used to assign to board.CurrentGameBoard[row][col] 
  """
  numbers = forward_checking_board[row][col]

  return numbers

def manipulateBoard(forward_checking_board, row, col, value):
  """
  if mode == False: mark the forward_checking_board, assign false to the same row, col, and square. 
  the same value cannot be used there.

  if mode == True: mark the forward_checking_board, assign True to the same row, col, and square. 
  the same value can be used there. 
  ATTENTION: but need to mark forward_checking_board[row][col][value-1] = False
  """
  BoardSize = len(forward_checking_board)
  SquareSize = int(math.sqrt(BoardSize))

  no_of_square_row = row // SquareSize
  no_of_square_col = col // SquareSize

  for i in range(BoardSize):
    if forward_checking_board[row][i].count(value) == 1:
      forward_checking_board[row][i].remove(value)
    if forward_checking_board[i][col].count(value) == 1:
      forward_checking_board[i][col].remove(value)

  for m in range(no_of_square_row*SquareSize, (no_of_square_row+1)*SquareSize):
    for n in range(no_of_square_col*SquareSize, (no_of_square_col+1)*SquareSize):
      if forward_checking_board[m][n].count(value) == 1:
        forward_checking_board[m][n].remove(value)

  return forward_checking_board

#------------------------------------------------------------------

# for testing forwarding checking

def solve_test(initial_board, forward_checking = False, MRV = False, MCV = False,
    LCV = False):
    """Takes an initial SudokuBoard and solves it using back tracking, and zero
    or more of the heuristics and constraint propagation methods (determined by
    arguments). Returns the resulting board solution. """
    start = time.time()
    forward_board = initForwardChecking(initial_board)
    result_board, result = backtrack_test(initial_board, forward_board, forward_checking, MRV, MCV)
    print "Using time: ", time.time() - start
    return result_board

def backtrack_test(board, forward_board,  forward_checking = False, MRV = False, MCV = False):
  if is_complete(board) == True:
    return board, True
  next_row, next_col = nextEmptyPosition(board, MRV, MCV)
  lists_value = validNumber(forward_board, next_row, next_col)
  if len(lists_value) == 0:
    return board, False
  for value in lists_value:
    new_board = copy.deepcopy(board)
    new_board.set_value(next_row, next_col, value)
    if forward_checking == True:
      new_forward_board = copy.deepcopy(forward_board)
      new_forward_board = manipulateBoard(new_forward_board, next_row, next_col, value, False)
      temp_board, result  = backtrack_test(new_board, new_forward_board, forward_checking, MRV,  MCV)
      if result == True:
        return temp_board, True
    

  return board, False

