import copy
import math
import os
import pprint
import random
import time
from typing import List

from constants import (
  NORMAL_SUDOKU_SYM2INT,
  SUDOKU_4_SYM2INT,
  SUDOKU_5_SYM2INT,
  EMPTY
)

clear = lambda : os.system("clear")

class Sudoku :
  def __init__(self, n:int=3) -> None :
    assert 1<=n<=5
    self.n = n
    self.rows = self.cols = n**2
    self.reset_board()

  #TODO: difficulty n solution seems prone to bug
  def read_from_file(self, filename:str) :
    self.reset_board()
    with open(filename, 'r') as f :
      n = len(f.readlines())
      assert n in [9, 16, 25], "invalid file contents"
      self.reset_board()
      if n==9 :
        sym2int = NORMAL_SUDOKU_SYM2INT
      elif n==16 :
        sym2int = SUDOKU_4_SYM2INT
      else :
        sym2int = SUDOKU_5_SYM2INT
      f.seek(0)
      for i, line in enumerate(f) :
        for j, c in enumerate(line.strip()) :
          self.board[i][j] = sym2int[c]
    self.difficulty = "custom"
    from solver import BacktrackSudokuSolver
    solver = BacktrackSudokuSolver(self)
    self.solution = solver.solve()

  def reset_board(self) -> None :
    """
    Assign EMPTY value to all cells in the board
    """
    self.board = [[EMPTY for _ in range(self.cols)] for _ in range(self.rows)]
    self.difficulty = None
    self.solution = None

  def is_cell_empty(self, board:List[List[int]], row:int, col:int) -> bool :
    """
    Check if a given cell (row,col) in a given board is EMPTY
    """
    return board[row][col] == EMPTY

  def is_board_valid(self, board:List[List[int]]) -> bool :
    """
    Check if a given board is valid/solvable
    """
    # Helper function to check if a list contains unique non-EMPTY elements
    def is_list_unique(lst:List[int]):
      nums = [num for num in lst if num!=EMPTY]
      return len(nums) == len(set(nums))
    # Check all rows and columns
    for row in range(self.rows) :
      if not is_list_unique(board[row]) :
        return False
    for col in range(self.cols) :
      if not is_list_unique([board[row][col] for row in range(self.rows)]) :
        return False
    # Check all subgrids
    for i in range(self.n) :
      for j in range(self.n) :
        if not is_list_unique([board[self.n*i+r][self.n*j+c] for r in range(self.n) for c in range(self.n)]) :
          return False
    return True

  def get_empty_cells(self, board:List[List[int]]) -> List[tuple] :
    """
    Get all empty cells in a given board
    """
    empty_cells = []
    for row in range(self.rows) :
      for col in range(self.cols) :
        if self.is_cell_empty(board, row, col) :
          empty_cells.append((row, col))
    return empty_cells

  def get_non_empty_cells(self, board:List[List[int]]) -> List[tuple] :
    """
    Get all non-EMPTY cells in a given board
    """
    non_empty_cells = []
    for row in range(self.rows) :
      for col in range(self.cols) :
        if not self.is_cell_empty(board, row, col) :
          non_empty_cells.append((row,col))
    return non_empty_cells

  def get_num_candidates(self, board:List[List[int]], row:int, col:int) -> List[int] :
    """
    Get all candidate numbers for a cell on a given board
    """
    all_candidates = set(range(self.n**2))
    existing_candidates = set()
    for i in range(self.n**2) :
      if not self.is_cell_empty(board, row, i) and i!=col :
        existing_candidates.add(board[row][i])
      if not self.is_cell_empty(board, i, col) and i!=row :
        existing_candidates.add(board[i][col])
    start_row, start_col = self.n * (row // self.n), self.n * (col // self.n)
    for i in range(self.n) :
      for j in range(self.n) :
        if not self.is_cell_empty(board, start_row+i, start_col+j) and (start_row+i!=row or start_col+j!=col) :
          existing_candidates.add(board[start_row+i][start_col+j])
    return list(all_candidates.difference(existing_candidates))

  def has_one_solution(self, board:List[List[int]]) -> bool :
    """
    Check if a given board has exactly one solution.
    Returns True if there's exactly one solution, False otherwise.
    """
    # Make a copy of the board to avoid modifying the original
    board_copy = copy.deepcopy(board)
    # Helper function to recursively check for solutions
    def count_solutions(empty_cells:List[tuple], idx:int=0) -> int :
      if idx == len(empty_cells) :
        return 1
      row, col = empty_cells[idx]
      n_solutions = 0
      for num_candidate in self.get_num_candidates(board_copy, row, col) :
        if self.is_num_valid(board_copy, row, col, num_candidate) :
          board_copy[row][col] = num_candidate
          n_solutions += count_solutions(empty_cells, idx+1)
          if n_solutions > 1 :
            return n_solutions
          board_copy[row][col] = EMPTY
      return n_solutions
    if not self.is_board_valid(board_copy) :
      print("not valid")
      return False
    empty_cells = self.get_empty_cells(board_copy)
    return count_solutions(empty_cells) == 1

  def has_one_solution_algx(self) :
    from solver import AlgXSudokuSolver
    solver = AlgXSudokuSolver(self)
    return len(solver.solve()) == 1

  def get_n_solutions(self, board:List[List[int]]) -> int :
    """
    Get the number of possible solutions of a given board
    """
    # Helper function to recursively count solutions of sudoku board
    def count_solutions(empty_cells:List[tuple], idx:int=0) :
      if idx == len(empty_cells) :
        return 1
      row, col = empty_cells[idx]
      total_solutions = 0
      for num_candidate in self.get_num_candidates(board, row, col) :
        if self.is_num_valid(board, row, col, num_candidate) :
          board[row][col] = num_candidate
          total_solutions += count_solutions(empty_cells, idx+1)
          board[row][col] = EMPTY
      return total_solutions
    if not self.is_board_valid(board) :
      print("not valid")
      return 0
    empty_cells = self.get_empty_cells(board)
    return count_solutions(empty_cells)

  def generate_new_puzzle(self, difficulty:str="medium", mode:str="linear", symmetric:bool=True) -> None :
    assert difficulty in ["easy", "medium", "hard", "extreme"]
    assert mode in ["linear", "exp"]
    """
    Number of non-empty cells for each difficulty is as follows
    Easy
    n=3, remove ~40.880700000000004
    n=4, remove ~161.6896
    n=5, remove ~474.0625
    Medium
    n=3, remove ~34.749
    n=4, remove ~140.74880000000002
    n=5, remove ~419.125
    Hard
    n=3, remove ~28.584899999999998
    n=4, remove ~119.68
    n=5, remove ~363.81249999999994
    Extreme
    n=3, remove ~22.45319999999999
    n=4, remove ~98.71359999999999
    n=5, remove ~308.75
    """
    if difficulty == "easy" :
      f_n = {
        "linear": lambda n : -.1269*n+.876,
        "exp": lambda n : 1.39829*.709631**n
      }
    elif difficulty == "medium" :
      f_n = {
        "linear": lambda n : -.1208*n+.9334,
        "exp": lambda n : 1.27574*.766428**n
      }
    elif difficulty == "hard" :
      f_n = {
        "linear": lambda n : -.1146*n+.9909,
        "exp": lambda n : 1.23031*.808136**n
      }
    else :
      f_n = {
        "linear": lambda n : -.1084*n+1.048,
        "exp": lambda n : 1.22242*.840011**n
      }
    n_cells_to_be_removed = math.ceil(f_n[mode](self.n)*(self.n**2)**2)
    non_empty_cells_threshold = (self.n**2)**2 - n_cells_to_be_removed
    lower_bound = non_empty_cells_threshold-2
    upper_bound = non_empty_cells_threshold+2

    puzzle_found = False
    retries = 1
    min_n_non_empty_cells = math.inf
    best_puzzle = None
    ns = []
    while not puzzle_found and retries!=0 :
      # Reset the board and randomly fill the board
      self.reset_board()
      self.randomly_fill_board()
      self.difficulty = difficulty
      self.solution = {(r, c): self.board[r][c] for c in range(self.cols) for r in range(self.rows)}
      # Get all the initial non-empty cells in the board
      non_empty_cells = self.get_non_empty_cells(self.board)
      random.shuffle(non_empty_cells)
      n_non_empty_cells = len(non_empty_cells)
      # Additional parameters
      removed_cells = set()
      removal_strat = True  # False -> prioritize removing least constrained cells (most number of candidates);
                            # True -> prioritize removing most constrained cells (least number of candidates)
      if symmetric :
        mirror_cond = lambda x, y, n : [
          x != y,                             # \
          x + y + 1 != n**2,                  # /
          (n%2 == 0) or (x != n**2//2),       # -
          (n%2 == 0) or (y != n**2//2),       # |
          ((x != n**2//2) or (y != n**2//2))  # ·
        ]
        mirror_fn = lambda x, y, n : [
          (y, x),               # \
          (n**2-1-y, n**2-1-x), # /
          (n**2-1-x, y),        # -
          (x, n**2-1-y),        # |
          (n**2-1-x, n**2-1-y)  # ·
        ]
        axis_id = random.randint(0,4)
        while len(non_empty_cells) and n_non_empty_cells >= non_empty_cells_threshold :
          # Store all cells to be emptied
          row, col = non_empty_cells.pop()
          # print("emptying", (row,col), len(self.get_num_candidates(self.board, row, col)))
          row_mirror, col_mirror = mirror_fn(row, col, self.n)[axis_id] if mirror_cond(row, col, self.n)[axis_id] else (None, None)
          cells_to_process = [(row, col)]
          # print(f"({row, col}) and ({row_mirror, col_mirror})", (row, col) in non_empty_cells, (row_mirror, col_mirror) in non_empty_cells)
          if row_mirror is not None and col_mirror is not None :
            cells_to_process.append((row_mirror, col_mirror))
            non_empty_cells.remove((row_mirror, col_mirror))
          # Store removed numbers
          removed_cell_to_num = {}
          for r, c in cells_to_process :
            n_non_empty_cells -= 1
            removed_cell_to_num[(r, c)] = self.board[r][c]
            self.board[r][c] = EMPTY
          # Check if there is only one solution
          board_copy = copy.deepcopy(self.board)
          if not self.has_one_solution(board_copy) :
            # If multiple solutions, revert the numbers removal
            for r, c in cells_to_process :
              n_non_empty_cells += 1
              self.board[r][c] = removed_cell_to_num[(r, c)]
              removed_cells.add((r, c))
            # print("GAGAL: appending", n_non_empty_cells, len(non_empty_cells), non_empty_cells_threshold, f"({row, col}) and ({row_mirror, col_mirror})", removed_cells)
          else :
            # Otherwise, the removal succeeded, update back the non_empty_cells
            non_empty_cells.extend(removed_cells)
            removed_cells.clear()
            non_empty_cells = sorted(
              non_empty_cells,
              key=lambda cell: len(self.get_num_candidates(self.board, cell[0], cell[1]))
                                + (len(self.get_num_candidates(self.board, row_mirror, col_mirror)) if row_mirror is not None and col_mirror is not None else 0),
              reverse=removal_strat
            )
            # print("SUCCESS: clearing", n_non_empty_cells, len(non_empty_cells), non_empty_cells_threshold, f"({row, col}) and ({row_mirror, col_mirror})", removed_cells)
      else :
        while len(non_empty_cells) and n_non_empty_cells >= non_empty_cells_threshold :
          row, col = non_empty_cells.pop()
          # print("emptying", (row,col), len(self.get_num_candidates(self.board, row, col)))
          n_non_empty_cells -= 1
          removed_num = self.board[row][col]
          self.board[row][col] = EMPTY
          board_copy = copy.deepcopy(self.board)
          if not self.has_one_solution(board_copy) :
            n_non_empty_cells += 1
            self.board[row][col] = removed_num
            removed_cells.add((row, col))
            # print("GAGAL: appending", n_non_empty_cells, len(non_empty_cells), non_empty_cells_threshold, removed_cells)
          else :
            non_empty_cells.extend(removed_cells)
            removed_cells.clear()
            non_empty_cells = sorted(
              non_empty_cells,
              key=lambda cell: len(self.get_num_candidates(self.board, cell[0], cell[1])),
              reverse=removal_strat
            )
            # print("SUCCESS: clearing", n_non_empty_cells, len(non_empty_cells), non_empty_cells_threshold, removed_cells)
      puzzle_found = lower_bound<=len(self.get_non_empty_cells(self.board))<=upper_bound
      retries -= 1
      ns.append(n_non_empty_cells)
      if n_non_empty_cells < min_n_non_empty_cells :
        min_n_non_empty_cells = n_non_empty_cells
        best_puzzle = copy.deepcopy(self.board)
    self.board = best_puzzle
    # print(ns)
    return

  def generate_new_puzzle_algx(self, difficulty:str="medium", mode:str="linear", symmetric:bool=True) -> None :
    assert difficulty in ["easy", "medium", "hard", "extreme"]
    assert mode in ["linear", "exp"]
    """
    Number of non-empty cells for each difficulty is as follows
    Easy
    n=3, remove ~40.880700000000004
    n=4, remove ~161.6896
    n=5, remove ~474.0625
    Medium
    n=3, remove ~34.749
    n=4, remove ~140.74880000000002
    n=5, remove ~419.125
    Hard
    n=3, remove ~28.584899999999998
    n=4, remove ~119.68
    n=5, remove ~363.81249999999994
    Extreme
    n=3, remove ~22.45319999999999
    n=4, remove ~98.71359999999999
    n=5, remove ~308.75
    """
    if difficulty == "easy" :
      f_n = {
        "linear": lambda n : -.1269*n+.876,
        "exp": lambda n : 1.39829*.709631**n
      }
    elif difficulty == "medium" :
      f_n = {
        "linear": lambda n : -.1208*n+.9334,
        "exp": lambda n : 1.27574*.766428**n
      }
    elif difficulty == "hard" :
      f_n = {
        "linear": lambda n : -.1146*n+.9909,
        "exp": lambda n : 1.23031*.808136**n
      }
    else :
      f_n = {
        "linear": lambda n : -.1084*n+1.048,
        "exp": lambda n : 1.22242*.840011**n
      }
    n_cells_to_be_removed = math.ceil(f_n[mode](self.n)*(self.n**2)**2)
    non_empty_cells_threshold = (self.n**2)**2 - n_cells_to_be_removed
    lower_bound = non_empty_cells_threshold-2
    upper_bound = non_empty_cells_threshold+2

    puzzle_found = False
    retries = 1
    min_n_non_empty_cells = math.inf
    best_puzzle = None
    ns = []
    while not puzzle_found and retries!=0 :
      # Reset the board and randomly fill the board
      self.reset_board()
      self.randomly_fill_board()
      self.difficulty = difficulty
      self.solution = {(r, c): self.board[r][c] for c in range(self.cols) for r in range(self.rows)}
      # Get all the initial non-empty cells in the board
      non_empty_cells = self.get_non_empty_cells(self.board)
      random.shuffle(non_empty_cells)
      n_non_empty_cells = len(non_empty_cells)
      # Additional parameters
      removed_cells = set()
      removal_strat = True  # False -> prioritize removing least constrained cells (most number of candidates);
                            # True -> prioritize removing most constrained cells (least number of candidates)
      if symmetric :
        mirror_cond = lambda x, y, n : [
          x != y,                             # \
          x + y + 1 != n**2,                  # /
          (n%2 == 0) or (x != n**2//2),       # -
          (n%2 == 0) or (y != n**2//2),       # |
          ((x != n**2//2) or (y != n**2//2))  # ·
        ]
        mirror_fn = lambda x, y, n : [
          (y, x),               # \
          (n**2-1-y, n**2-1-x), # /
          (n**2-1-x, y),        # -
          (x, n**2-1-y),        # |
          (n**2-1-x, n**2-1-y)  # ·
        ]
        axis_id = random.randint(0,4)
        while len(non_empty_cells) and n_non_empty_cells >= non_empty_cells_threshold :
          # Store all cells to be emptied
          row, col = non_empty_cells.pop()
          # print("emptying", (row,col), len(self.get_num_candidates(self.board, row, col)))
          row_mirror, col_mirror = mirror_fn(row, col, self.n)[axis_id] if mirror_cond(row, col, self.n)[axis_id] else (None, None)
          cells_to_process = [(row, col)]
          # print(f"({row, col}) and ({row_mirror, col_mirror})", (row, col) in non_empty_cells, (row_mirror, col_mirror) in non_empty_cells)
          if row_mirror is not None and col_mirror is not None :
            cells_to_process.append((row_mirror, col_mirror))
            non_empty_cells.remove((row_mirror, col_mirror))
          # Store removed numbers
          removed_cell_to_num = {}
          for r, c in cells_to_process :
            n_non_empty_cells -= 1
            removed_cell_to_num[(r, c)] = self.board[r][c]
            self.board[r][c] = EMPTY
          # Check if there is only one solution
          board_copy = copy.deepcopy(self.board)
          if not self.has_one_solution_algx() :
            # If multiple solutions, revert the numbers removal
            for r, c in cells_to_process :
              n_non_empty_cells += 1
              self.board[r][c] = removed_cell_to_num[(r, c)]
              removed_cells.add((r, c))
            # print("GAGAL: appending", n_non_empty_cells, len(non_empty_cells), non_empty_cells_threshold, f"({row, col}) and ({row_mirror, col_mirror})", removed_cells)
          else :
            # Otherwise, the removal succeeded, update back the non_empty_cells
            non_empty_cells.extend(removed_cells)
            removed_cells.clear()
            non_empty_cells = sorted(
              non_empty_cells,
              key=lambda cell: len(self.get_num_candidates(self.board, cell[0], cell[1]))
                                + (len(self.get_num_candidates(self.board, row_mirror, col_mirror)) if row_mirror is not None and col_mirror is not None else 0),
              reverse=removal_strat
            )
            # print("SUCCESS: clearing", n_non_empty_cells, len(non_empty_cells), non_empty_cells_threshold, f"({row, col}) and ({row_mirror, col_mirror})", removed_cells)
      else :
        while len(non_empty_cells) and n_non_empty_cells >= non_empty_cells_threshold :
          row, col = non_empty_cells.pop()
          # print("emptying", (row,col), len(self.get_num_candidates(self.board, row, col)))
          n_non_empty_cells -= 1
          removed_num = self.board[row][col]
          self.board[row][col] = EMPTY
          board_copy = copy.deepcopy(self.board)
          if not self.has_one_solution(board_copy) :
            n_non_empty_cells += 1
            self.board[row][col] = removed_num
            removed_cells.add((row, col))
            # print("GAGAL: appending", n_non_empty_cells, len(non_empty_cells), non_empty_cells_threshold, removed_cells)
          else :
            non_empty_cells.extend(removed_cells)
            removed_cells.clear()
            non_empty_cells = sorted(
              non_empty_cells,
              key=lambda cell: len(self.get_num_candidates(self.board, cell[0], cell[1])),
              reverse=removal_strat
            )
            # print("SUCCESS: clearing", n_non_empty_cells, len(non_empty_cells), non_empty_cells_threshold, removed_cells)
      puzzle_found = lower_bound<=len(self.get_non_empty_cells(self.board))<=upper_bound
      retries -= 1
      ns.append(n_non_empty_cells)
      if n_non_empty_cells < min_n_non_empty_cells :
        min_n_non_empty_cells = n_non_empty_cells
        best_puzzle = copy.deepcopy(self.board)
    self.board = best_puzzle
    # print(ns)
    return

  def is_num_valid(self, board:List[List[int]], row:int, col:int, num:int) -> bool :
    """
    Check if a number candidate is valid to be put in a given cell on a given board
    """
    # Check if the number is in the current row or column
    for i in range(self.n**2) :
      if board[row][i] == num or board[i][col] == num :
        return False
    # Check if the number is in the current subgrid
    start_row, start_col = self.n * (row // self.n), self.n * (col // self.n)
    for i in range(self.n) :
      for j in range(self.n) :
        if board[start_row + i][start_col + j] == num :
          return False
    return True

  def randomly_fill_board(self) :
    """
    Randomly fill the board using backtrack
    """
    for row in range(self.rows) :
      for col in range(self.cols) :
        if self.is_cell_empty(self.board, row, col) :
          num_candidates = self.get_num_candidates(self.board, row, col)
          random.shuffle(num_candidates)
          for num_candidate in num_candidates :
            if self.is_num_valid(self.board, row, col, num_candidate) :
              self.board[row][col] = num_candidate
              if self.randomly_fill_board() :
                return True
              self.board[row][col] = EMPTY
          return False
    return True

if __name__ == "__main__" :
  # for i, row in solution :
  #   print((i//81), (i%81)//9, (i%9))

  sudoku = Sudoku()
  # sudoku.read_from_file("./multiple-sol.txt")
  start = time.time()
  sudoku.generate_new_puzzle("easy")
  elapsed_time = time.time() - start
  pprint.pprint(sudoku.board)
  print(elapsed_time)
  # start = time.time()
  # print(sudoku.has_one_solution_algx(), time.time()-start)
  # start = time.time()
  # print(sudoku.get_n_solutions(sudoku.board), time.time()-start)
  # start = time.time()
  # sudoku.randomly_fill_board()
  # print(time.time()-start)
  # pprint.pprint(sudoku.board)

  # # TESTING A
  # ##
  # sudoku.read_from_file("./multiple-sol-3-maybe.txt")
  # a = copy.deepcopy(sudoku.board)
  # pprint.pprint(sudoku.board)
  # ##
  # start = time.time()
  # print(sudoku.has_one_solution(sudoku.board), time.time()-start)
  # c = copy.deepcopy(sudoku.board)
  # print("a==c", a==c)
  # ##
  # start = time.time()
  # print(sudoku.get_n_solutions(sudoku.board), time.time()-start)
  # b = copy.deepcopy(sudoku.board)
  # print("a==b", a==b)
  # pprint.pprint(sudoku.board)


  # # buat ngecek generate puzzle
  # start = time.time()
  # sudoku.generate_new_puzzle("medium", "linear", True)
  # print(time.time()-start)
  # pprint.pprint(sudoku.board)
  # print("empty", len(sudoku.get_empty_cells(sudoku.board)))
  # print("non-empty", len(sudoku.get_non_empty_cells(sudoku.board)))