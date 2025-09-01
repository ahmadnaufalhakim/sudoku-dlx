import copy
import pprint
import random
import time
from typing import List, Optional

from constants import EMPTY
from sudoku import Sudoku

class AlgX :
  def __init__(self, ec_mat:List[List[int]]) -> None :
    """
    Initialize the Algorithm X solver with a given exact cover matrix

    ec_mat: List of lists representing the exact cover matrix
    """
    assert ec_mat[0] is not None
    self.ec_mat = ec_mat
    self.rows, self.cols = len(ec_mat), len(ec_mat[0])

  def search(self, solution:dict={}, backup:List=[], k:int=0) -> Optional[List] :
    """
    Implementation of Donald Knuth's Algorithm X.
    Returns the first solution it finds to the exact cover matrix
    """
    if all(row is None for row in self.ec_mat) :
      if sum(n_constraints for _, n_constraints in solution.items()) == self.cols :
        return list(solution.keys())
      return None

    # Select column with the fewest 1's
    col = self.select_column()
    # If the column with the "fewest" 1's hasn't any 1 in it, algorithm terminates unsuccessfully
    if sum(row[col] for row in self.ec_mat if row is not None) == 0 :
      return None

    sln_candidates = self.get_rows_for_column(col)
    random.shuffle(sln_candidates)

    for sln_cand in sln_candidates :
      # Select this row
      solution[sln_cand] = self.ec_mat[sln_cand].count(1)
      satisfied_columns = [j for j in range(len(self.ec_mat[sln_cand])) if self.ec_mat[sln_cand][j] == 1]
      # Cover all columns that are satisfied by this row
      for satisfied_column in satisfied_columns :
        self.cover_column(satisfied_column, backup)
      # Recurse and search deeper
      result = self.search(solution, backup, k+1)
      if result is not None :
        return result
      # Uncover all columns if this row didn't lead to a solution
      for _ in range(len(satisfied_columns)) :
        self.uncover_column(backup)
      # Deselect this row 
      del solution[sln_cand]
    return None

  def select_column(self) -> int :
    """
    Select the next column to cover (e.g., column with the fewest 1's)
    """
    return min(
      [j for j in range(self.cols) if all(isinstance(row[j], int) for row in self.ec_mat if row is not None)],
      key=lambda col: sum(row[col] for row in self.ec_mat if row is not None)
    )

  def get_rows_for_column(self, col:int) -> List :
    """
    Get all rows that satisfy the given column constraint `col`
    """
    # Return all rows that have a '1' in the given column
    return [i for i in range(self.rows) if self.ec_mat[i] is not None and self.ec_mat[i][col] == 1]

  def cover_column(self, col:int, backup:List=[]) -> None :
    """
    Cover column `col` and save the column index `col` and all the removed rows in the `backup` list
    """
    removed_rows = []
    # Mark removed rows as `None` and store them in the `backup` list
    for i in range(self.rows) :
      if self.ec_mat[i] is not None and self.ec_mat[i][col] == 1 :
        removed_rows.append((i, self.ec_mat[i]))  # Store tuple (row index, row contents)
        self.ec_mat[i] = None # Remove row by setting it to `None`
    # Remove the column from the remaining rows
    for row in self.ec_mat :
      if row is not None :
        row[col] = str(row[col])
    # Store the covered column index and removed rows in the `backup` list
    backup.append((col, removed_rows))

  def uncover_column(self, backup:List) -> None :
    """
    Uncover columns and restore removed rows using columns removal history list `backup`
    """
    # Get the most recently removed rows for this column
    col, removed_rows = backup.pop()
    # Restore the column values in all non-removed rows
    for row in self.ec_mat :
      if row is not None :
        if isinstance(row[col], str) :
          row[col] = int(row[col])
    # Restore the removed rows
    for i, row_content in removed_rows :
      self.ec_mat[i] = row_content

class AlgXSudokuSolver(AlgX) :
  def __init__(self, sudoku:Sudoku) -> None :
    super().__init__(self.sudoku_as_ec_mat(sudoku))
    self.sudoku = copy.deepcopy(sudoku)

  def solve(self) -> Optional[dict] :
    """
    Solve the given unsolved Sudoku board using Algorithm X

    sudoku: A sudoku object
    """
    N_CANDIDATES = self.sudoku.n*self.sudoku.n
    N_CELLS = N_CANDIDATES*N_CANDIDATES
    solution = {}
    for r in range(N_CANDIDATES) :
      for c in range(N_CANDIDATES) :
        if not self.sudoku.is_cell_empty(self.sudoku.board, r, c) :
          num = self.sudoku.board[r][c]
          row_id = r*N_CELLS + c*N_CANDIDATES + num
          solution[row_id] = self.ec_mat[row_id].count(1)
          column_ids = [j for j in range(len(self.ec_mat[row_id])) if self.ec_mat[row_id][j] == 1]
          for column_id in column_ids :
            self.cover_column(column_id)
    return {
      (row_id//81, (row_id%81)//9): row_id%9
      for row_id in self.search(solution.copy())
      if row_id not in solution
    }

  def sudoku_as_ec_mat(self, sudoku:Sudoku) -> List[List[int]] :
    """
    Convert a given sudoku object to exact cover matrix
    """
    n = sudoku.n
    N_CANDIDATES = n*n
    N_CELLS = N_CANDIDATES*N_CANDIDATES
    ec_mat = []

    # Generate exact cover matrix for the given sudoku object
    # There are 4 constraints: row-column, row-number, column-number, and block-number
    for r in range(N_CANDIDATES) :
      for c in range(N_CANDIDATES) :
        for num in range(N_CANDIDATES) :
          row = [0] * (4*N_CELLS)

          # Row-column constraint (there is one number in each cell)
          row[0*N_CELLS + r*N_CANDIDATES + c] = 1

          # Row-number constraint (digit `num` appears in row r)
          row[1*N_CELLS + r*N_CANDIDATES + num] = 1

          # Column-number constraint (digit `num` appears in column c)
          row[2*N_CELLS + c*N_CANDIDATES + num] = 1

          # Block constraint (digit `num` appears in the n*n sub-block)
          block_offset = N_CANDIDATES * (n*(r//n) + c//n)
          row[3*N_CELLS + block_offset + num] = 1

          # Add the row to the exact cover matrix
          ec_mat.append(row)

    # Do exact cover matrix checking using the given sudoku board
    self.check_ec_mat(ec_mat, sudoku)
    return ec_mat

  def check_ec_mat(self, ec_mat:List[List[int]], sudoku:Sudoku) -> None :
    """
    Perform assertions to check the correctness of the exact cover matrix (ec_mat)
    """
    n = sudoku.n
    N_CANDIDATES = n*n
    N_CELLS = N_CANDIDATES*N_CANDIDATES

    # 1. Check the overall dimensions of the matrix
    assert len(ec_mat) == N_CELLS*N_CANDIDATES, f"Matrix should have {N_CELLS*N_CANDIDATES} rows, but got {len(ec_mat)}"
    assert all(len(row) == 4*N_CELLS for row in ec_mat), f"Each row should have {4*N_CELLS} columns"

    # 2. Check each row has exactly 4 ones (one for each constraint)
    for i, row in enumerate(ec_mat):
      assert sum(row) == 4, f"Row {i} should have exactly 4 ones, but got {sum(row)}"

    # 3. Check specific constraints (e.g., using number placements on the given sudoku board)
    for r, c in sudoku.get_non_empty_cells(sudoku.board) :
      num = sudoku.board[r][c]
      row = ec_mat[r*N_CELLS + c*N_CANDIDATES + num]
      # Cell constraint: one number per cell
      assert row[0*N_CELLS + r*N_CANDIDATES + c] == 1, f"Cell constraint failed for ({r},{c})"
      # Row constraint: one occurrence of each digit in each row
      assert row[1*N_CELLS + r*N_CANDIDATES + num] == 1, f"Row constraint failed for row {r}"
      # Column constraint: one occurrence of each digit in each column
      assert row[2*N_CELLS + c*N_CANDIDATES + num] == 1, f"Column constraint failed for column {c}"
      # Block constraint: one occurrence of each digit in each block
      block_offset = N_CANDIDATES * (n*(r//n) + (c//n))
      assert row[3*N_CELLS + block_offset + num] == 1, f"Block constraint failed for block ({r//n},{c//n})"
    return

class BacktrackSudokuSolver :
  def __init__(self, sudoku:Sudoku) -> None:
    self.sudoku = copy.deepcopy(sudoku)

  def solve(self, solution:dict={}, k:int=0) -> Optional[dict] :
    """
    Solve the given unsolved Sudoku board using backtrack algorithm

    sudoku: A sudoku object
    """
    obv_cells = []
    if not (self.solve_obvious_cells(obv_cells) and
            self.solve_obvious_rows(obv_cells) and
            self.solve_obvious_cols(obv_cells) and
            self.solve_obvious_blocks(obv_cells)) :
      return None
    # print(f"\t"*k, k, "cells updated:", obv_cells, len(obv_cells))
    for r, c in obv_cells :
      solution[(r, c)] = self.sudoku.board[r][c]

    if self.is_board_full() :
      # print(f"\t"*k, k, "SIGMA SIGMA SIGMA")
      return solution
    else :
      empty_cells = sorted(
        self.sudoku.get_empty_cells(self.sudoku.board),
        key=lambda cell: len(self.sudoku.get_num_candidates(self.sudoku.board, cell[0], cell[1]))
      )
      num_candidates = self.sudoku.get_num_candidates(self.sudoku.board, empty_cells[0][0], empty_cells[0][1])
      for num_candidate in num_candidates :
        # print(f"\t"*k, k, "searching", empty_cells[0], num_candidates, num_candidate)
        solution[(empty_cells[0][0], empty_cells[0][1])] = num_candidate
        self.sudoku.board[empty_cells[0][0]][empty_cells[0][1]] = num_candidate
        result = self.solve(solution, k+1)
        if result is not None :
          return result
        else :
          self.sudoku.board[empty_cells[0][0]][empty_cells[0][1]] = EMPTY
          del solution[(empty_cells[0][0], empty_cells[0][1])]
      self.unsolve_obvious(obv_cells)
      return None

  def solve_obvious_cells(self, obv_cells:List=[]) -> bool :
    """
    Solve cells with only one possible candidate based on the current board state
    """
    if not self.is_board_full() :
      empty_cells = self.sudoku.get_empty_cells(self.sudoku.board)
      for r, c in empty_cells :
        num_candidates = self.sudoku.get_num_candidates(self.sudoku.board, r, c)
        if len(num_candidates) == 0 :
          print("ohno!", "cell", (r,c), "have no cand")
          self.unsolve_obvious(obv_cells)
          return False
        elif len(num_candidates) == 1 :
          self.sudoku.board[r][c] = num_candidates[0]
          obv_cells.append((r, c))
          print("obv_cell", (r,c), num_candidates, obv_cells)
    return True

  def solve_obvious_rows(self, obv_cells:List=[]) -> bool :
    """
    Fill numbers in rows where a digit has only one valid position
    """
    if not self.is_board_full() :
      for r in range(self.sudoku.n**2) :
        for num in range(self.sudoku.n**2) :
          is_num_exist_in_row = False
          is_cell_safe = lambda r,c,num : self.sudoku.is_cell_empty(self.sudoku.board, r, c) and self.sudoku.is_num_valid(self.sudoku.board, r, c, num)
          cell_candidates = []
          for c in range(self.sudoku.n**2) :
            if self.sudoku.board[r][c] == num :
              is_num_exist_in_row = True
              break
            elif is_cell_safe(r, c, num) :
              cell_candidates.append((r, c))
          if not is_num_exist_in_row :
            if len(cell_candidates) == 0 :
              print("ohno!", "row", r, "can't put", num)
              self.unsolve_obvious(obv_cells)
              return False
            elif len(cell_candidates) == 1 :
              self.sudoku.board[cell_candidates[0][0]][cell_candidates[0][1]] = num
              obv_cells.append((cell_candidates[0][0], cell_candidates[0][1]))
              print("obv_row", cell_candidates, num, obv_cells)
    return True

  def solve_obvious_cols(self, obv_cells:List=[]) -> bool :
    """
    Fill numbers in columns where a digit has only one valid position
    """
    if not self.is_board_full() :
      for c in range(self.sudoku.n**2) :
        for num in range(self.sudoku.n**2) :
          is_num_exist_in_col = False
          is_cell_safe = lambda r,c,num : self.sudoku.is_cell_empty(self.sudoku.board, r, c) and self.sudoku.is_num_valid(self.sudoku.board, r, c, num)
          cell_candidates = []
          for r in range(self.sudoku.n**2) :
            if self.sudoku.board[r][c] == num :
              is_num_exist_in_col = True
              break
            elif is_cell_safe(r, c, num) :
              cell_candidates.append((r, c))
          if not is_num_exist_in_col :
            if len(cell_candidates) == 0 :
              pprint.pprint(self.sudoku.board)
              print("ohno!", "col", c, "can't put", num)
              self.unsolve_obvious(obv_cells)
              return False
            elif len(cell_candidates) == 1 :
              self.sudoku.board[cell_candidates[0][0]][cell_candidates[0][1]] = num
              obv_cells.append((cell_candidates[0][0], cell_candidates[0][1]))
              print("obv_col", cell_candidates, num, obv_cells)
    return True

  def solve_obvious_blocks(self, obv_cells:List=[]) -> bool :
    """
    Fill numbers in sub blocks where a digit has only one valid position
    """
    if not self.is_board_full() :
      for i in range(self.sudoku.n) :
        for j in range(self.sudoku.n) :
          for num in range(self.sudoku.n**2) :
            is_num_exist_in_block = False
            is_cell_safe = lambda r,c,num : self.sudoku.is_cell_empty(self.sudoku.board, r, c) and self.sudoku.is_num_valid(self.sudoku.board, r, c, num)
            cell_candidates = []
            for r in range(self.sudoku.n) :
              if is_num_exist_in_block :
                break
              for c in range(self.sudoku.n) :
                if self.sudoku.board[self.sudoku.n*i+r][self.sudoku.n*j+c] == num :
                  # print("block", (i,j), "found", num, "on", (self.sudoku.n*i+r, self.sudoku.n*j+c))
                  is_num_exist_in_block = True
                  break
                elif is_cell_safe(self.sudoku.n*i+r, self.sudoku.n*j+c, num) :
                  cell_candidates.append((self.sudoku.n*i+r, self.sudoku.n*j+c))
            if not is_num_exist_in_block :
              if len(cell_candidates) == 0 :
                print("ohno!", "block", (i,j), "can't put", num)
                self.unsolve_obvious(obv_cells)
                return False
              elif len(cell_candidates) == 1 :
                # print("yay:)", "block", (i,j), "put", num, "in", cell_candidates)
                self.sudoku.board[cell_candidates[0][0]][cell_candidates[0][1]] = num
                obv_cells.append((cell_candidates[0][0], cell_candidates[0][1]))
    return True

  def unsolve_obvious(self, obv_cells:List=[]) -> None :
    """
    Revert cells filled by 'solve_obvious_<constraint>' methods, restoring the board to its previous state
    """
    print("about to unsolve", len(obv_cells), "cells", obv_cells)
    for r, c in obv_cells :
      print("unsolving", (r,c))
      self.sudoku.board[r][c] = EMPTY
    return

  def is_board_full(self) -> bool :
    """
    Check if all cells of the given sudoku board is filled
    """
    for r in range(self.sudoku.rows) :
      for c in range(self.sudoku.cols) :
        if self.sudoku.is_cell_empty(self.sudoku.board, r, c) :
          return False
    return True

if __name__ == "__main__" :
  sdk = Sudoku(3)
  # sdk.generate_new_puzzle(difficulty="extreme", mode="linear", symmetric=True)
  sdk.read_from_file("./extreme.txt")
  pprint.pprint(sdk.board)
  print("empty", len(sdk.get_empty_cells(sdk.board)))
  print("non-empty", len(sdk.get_non_empty_cells(sdk.board)))

  x_sdk_solver = AlgXSudokuSolver(sdk)
  bt_sdk_solver = BacktrackSudokuSolver(sdk)
  # print(len(x_sdk_solver.solve()))

  # Alg X vs BT
  # x_sdk_solver = AlgXSudokuSolver(sdk)
  # start = time.time()
  # print(len(x_sdk_solver.solve()))
  # print(time.time()-start)
  # bt_sdk_solver = BacktrackSudokuSolver(sdk)
  # start = time.time()
  # print(len(bt_sdk_solver.solve()))
  # print(time.time()-start)
  # pprint.pprint(bt_sdk_solver.sudoku.board)