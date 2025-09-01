import pprint
import pygame

from constants import (
  NORMAL_SUDOKU_INT2SYM, NORMAL_SUDOKU_SYM2INT,
  SUDOKU_4_INT2SYM, SUDOKU_4_SYM2INT,
  SUDOKU_5_INT2SYM, SUDOKU_5_SYM2INT,
  EMPTY,
  BOARD_PADDING,
  BOARD_SIZE,
  CELL_SIZE,
  NUM_FONT_SIZE, CAND_FONT_SIZE,
  WHITE, BLACK, GRAY, RED, GREEN, BLUE, ORANGE, CYAN, LIGHT_BLUE, BLUEISH_GRAY,
  HIGHLIGHTED_CELL_BG, HIGHLIGHTED_NUM_BG,
  CORRECT_NUM_COLOR, CORRECT_NUM_BG,
  INCORRECT_NUM_COLOR, INCORRECT_NUM_BG
)
from sudoku import Sudoku

class SudokuBoard :
  def __init__(self, sudoku:Sudoku, color_palette:int=0) -> None:
    self.sudoku = sudoku
    self.n = sudoku.n
    if self.n <= 3 :
      self.int2sym = NORMAL_SUDOKU_INT2SYM; self.sym2int = NORMAL_SUDOKU_SYM2INT
    elif self.n == 4 :
      self.int2sym = SUDOKU_4_INT2SYM; self.sym2int = SUDOKU_4_SYM2INT
    elif self.n == 5 :
      self.int2sym = SUDOKU_5_INT2SYM; self.sym2int = SUDOKU_5_SYM2INT
    self.rows = self.cols = self.n**2
    self.color_palette = color_palette
    self.cell_size = CELL_SIZE(self.n)
    self.num_font_size = NUM_FONT_SIZE(self.n)
    self.cand_font_size = CAND_FONT_SIZE(self.n)
    self.candidates = [[set() for _ in range(self.cols)] for _ in range(self.rows)]
    self.selected_cell = None
    self.selected_num = None
    for cell in self.sudoku.get_non_empty_cells(self.sudoku.board) :
      self.sudoku.solution.pop(cell, None)
    print(len(self.sudoku.solution))
    print(len(self.sudoku.get_empty_cells(self.sudoku.board)))
    # pprint.pprint(self.sudoku.solution)

  def highlight_affected_cells(self, screen:pygame.Surface) -> None :
    if self.selected_cell is None :
      return
    r, c = self.selected_cell
    # Draw affected row
    pygame.draw.rect(
      surface=screen,
      color=HIGHLIGHTED_CELL_BG,
      rect=pygame.Rect(
        (BOARD_PADDING, BOARD_PADDING + r*self.cell_size),
        (BOARD_SIZE, self.cell_size)
      )
    )
    # Draw affected col
    pygame.draw.rect(
      surface=screen,
      color=HIGHLIGHTED_CELL_BG,
      rect=pygame.Rect(
        (BOARD_PADDING + c*self.cell_size, BOARD_PADDING),
        (self.cell_size, BOARD_SIZE)
      )
    )
    # Draw affected block
    pygame.draw.rect(
      surface=screen,
      color=HIGHLIGHTED_CELL_BG,
      rect=pygame.Rect(
        (BOARD_PADDING + c//self.n*self.n*self.cell_size, BOARD_PADDING + r//self.n*self.n*self.cell_size),
        (self.cell_size*self.n, self.cell_size*self.n)
      )
    )
    # Draw selected cell with a bit darker background color
    pygame.draw.rect(
      surface=screen,
      color=tuple(max(c-32, 0) for c in HIGHLIGHTED_CELL_BG),
      rect=pygame.Rect(
        (BOARD_PADDING + c*self.cell_size, BOARD_PADDING + r*self.cell_size),
        (self.cell_size, self.cell_size)
      )
    )

  def draw_board(self, screen:pygame.Surface) -> None :
    # Draw the outermost board line
    pygame.draw.rect(
      surface=screen,
      color=BLACK,
      rect=pygame.Rect(
        (BOARD_PADDING, BOARD_PADDING),
        (BOARD_SIZE, BOARD_SIZE)
      ),
      width=4,
      border_radius=5
    )
    # Draw horizontal and vertical lines
    for i in range(self.n**2-1) :
      width = 1 if (i+1)%self.n!=0 else 3
      # Draw horizontal lines
      pygame.draw.line(
        surface=screen,
        color=BLACK,
        start_pos=(BOARD_PADDING, BOARD_PADDING + (i+1)*self.cell_size),
        end_pos=(BOARD_PADDING + BOARD_SIZE, BOARD_PADDING + (i+1)*self.cell_size),
        width=width
      )
      # Draw vertical lines
      pygame.draw.line(
        surface=screen,
        color=BLACK,
        start_pos=(BOARD_PADDING + (i+1)*self.cell_size, BOARD_PADDING),
        end_pos=(BOARD_PADDING + (i+1)*self.cell_size, BOARD_PADDING + BOARD_SIZE),
        width=width
      )

  def draw_nums_and_cands(self, screen:pygame.Surface) -> None :
    # Draw the numbers and candidates
    for r in range(self.rows) :
      for c in range(self.cols) :
        num = self.sudoku.board[r][c]
        # If there already exist a number in the cell
        if num != EMPTY :
          is_num_highlighted = self.selected_num is not None and num == self.selected_num
          font = pygame.font.Font(None, int(self.num_font_size))
          if is_num_highlighted :
            font.set_bold(True)
          text_surface = font.render(
            self.int2sym[num],
            True,
            BLACK if (r, c) not in self.sudoku.solution
              else CORRECT_NUM_COLOR if num == self.sudoku.solution[(r, c)]
              else INCORRECT_NUM_COLOR
          )
          text_surface_rect = text_surface.get_rect(center=(
            BOARD_PADDING + c*self.cell_size + self.cell_size/2,
            BOARD_PADDING + r*self.cell_size + self.cell_size/2
          ))
          if is_num_highlighted :
            cell_rect = pygame.Rect(
              (BOARD_PADDING + c*self.cell_size, BOARD_PADDING + r*self.cell_size),
              (self.cell_size, self.cell_size)
            )
            screen.fill(
              color=HIGHLIGHTED_NUM_BG,
              rect=cell_rect
            )
            pygame.draw.rect(
              surface=screen,
              color=BLACK,
              rect=cell_rect,
              width=3
            )
          elif (r, c) in self.sudoku.solution :
            cell_rect = pygame.Rect(
              (BOARD_PADDING + c*self.cell_size, BOARD_PADDING + r*self.cell_size),
              (self.cell_size, self.cell_size)
            )
            screen.fill(
              color=CORRECT_NUM_BG if num == self.sudoku.solution[(r, c)]
                else INCORRECT_NUM_BG,
              rect=cell_rect
            )
          screen.blit(
            source=text_surface,
            dest=text_surface_rect
          )
        # Else if there exist any candidates in the cell
        elif len(self.candidates[r][c]) :
          font = pygame.font.Font(None, int(self.cand_font_size))
          for candidate in sorted(self.candidates[r][c]) :
            text_surface = font.render(self.int2sym[candidate], True, BLACK)
            text_surface_rect = text_surface.get_rect(center=(
              BOARD_PADDING + c*self.cell_size + (candidate%self.n+.5)*self.cell_size/self.n,
              BOARD_PADDING + r*self.cell_size + (candidate//self.n+.5)*self.cell_size/self.n,
            ))
            screen.blit(
              source=text_surface,
              dest=text_surface_rect
            )

  def draw(self, screen:pygame.Surface) -> None :
    self.highlight_affected_cells(screen)
    self.draw_nums_and_cands(screen)
    self.draw_board(screen)

  def deselect_cell(self) -> None :
    self.selected_cell = None
    self.selected_num = None

  def select_cell(self, x:int, y:int) -> None :
    if (BOARD_PADDING <= x <= BOARD_PADDING + BOARD_SIZE and
        BOARD_PADDING <= y <= BOARD_PADDING + BOARD_SIZE)  :
      r, c = int((y-BOARD_PADDING)//self.cell_size), int((x-BOARD_PADDING)//self.cell_size)
      if (r, c) != self.selected_cell :
        self.selected_cell = (r, c)
        self.selected_num = self.sudoku.board[r][c]
      else :
        self.deselect_cell()

  def set_cell(self, sym:str) -> None :
    if (self.selected_cell is not None and
        (self.selected_cell[0], self.selected_cell[1]) in self.sudoku.solution and
        sym in self.sym2int) :
      r, c = self.selected_cell
      self.candidates[r][c].clear()
      self.selected_num = self.sym2int[sym]
      self.sudoku.board[r][c] = self.selected_num
      # Remove candidates across the affected row, cell, and block
      for i in range(self.n**2) :
        self.candidates[r][i].discard(self.selected_num)
        self.candidates[i][c].discard(self.selected_num)
      start_row, start_col = self.n*(r//self.n), self.n*(c//self.n)
      for i in range(self.n) :
        for j in range(self.n) :
          self.candidates[start_row+i][start_col+j].discard(self.selected_num)

  def add_candidate(self, sym:str) -> None :
    if (self.selected_cell is not None and
        (self.selected_cell[0], self.selected_cell[1]) in self.sudoku.solution and
        sym in self.sym2int) :
      r, c = self.selected_cell
      self.sudoku.board[r][c] = EMPTY
      if self.sym2int[sym] not in self.candidates[r][c] :
        self.candidates[r][c].add(self.sym2int[sym])
      else :
        self.candidates[r][c].discard(self.sym2int[sym])

  def erase_cell(self) -> None :
    if (self.selected_cell is not None and
        (self.selected_cell[0], self.selected_cell[1]) in self.sudoku.solution) :
      r, c = self.selected_cell
      self.candidates[r][c].clear()
      self.sudoku.board[r][c] = EMPTY
      self.selected_num = None

  def move(self, event:pygame.event.Event) -> None :
    if self.selected_cell is not None :
      r, c = self.selected_cell
      if event.key == pygame.K_UP :
        r = max(r-1, 0)
      if event.key == pygame.K_DOWN :
        r = min(r+1, self.n**2-1)
      if event.key == pygame.K_LEFT :
        c = max(c-1, 0)
      if event.key == pygame.K_RIGHT :
        c = min(c+1, self.n**2-1)
      self.selected_cell = (r, c)
      self.selected_num = self.sudoku.board[r][c]