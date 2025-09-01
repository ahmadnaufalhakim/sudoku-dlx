import pygame

from display.button import Button
from constants import (
  NORMAL_SUDOKU_INT2SYM, NORMAL_SUDOKU_SYM2INT,
  SUDOKU_4_INT2SYM, SUDOKU_4_SYM2INT,
  SUDOKU_5_INT2SYM, SUDOKU_5_SYM2INT,
  EMPTY,
  WINDOW_WIDTH, WINDOW_HEIGHT,
  BOARD_PADDING, BOARD_SIZE,
  GAME_CONTROL_HEIGHT,
  CELL_SIZE, NUM_FONT_SIZE,
  BLUE, ORANGE, LIGHT_BLUE,
  NUMPAD_BG, NUMPAD_BORDER_COLOR
)
from sudoku import Sudoku

class Numpad :
  def __init__(self, sudoku:Sudoku) -> None:
    self.sudoku = sudoku
    self.n = sudoku.n
    if self.n <= 3 :
      self.int2sym = NORMAL_SUDOKU_INT2SYM; self.sym2int = NORMAL_SUDOKU_SYM2INT
    elif self.n == 4 :
      self.int2sym = SUDOKU_4_INT2SYM; self.sym2int = SUDOKU_4_SYM2INT
    elif self.n == 5 :
      self.int2sym = SUDOKU_5_INT2SYM; self.sym2int = SUDOKU_5_SYM2INT
    self.button_syms = [self.int2sym[num] for num in range(self.n**2)]

    # Padding constant for numpad
    padding = BOARD_PADDING
    # Calculate the total button width and height based on sudoku's `n`
    available_space = (WINDOW_WIDTH - (BOARD_PADDING + BOARD_SIZE)) - 2*padding
    total_button_widths = sum(
      .95*available_space/self.n
      for _ in range(self.n)
    )
    total_button_heights = sum(
      .95*available_space/self.n
      for _ in range(self.n)
    )

    # Calculate the remaining space
    remaining_space_x = available_space - total_button_widths
    remaining_space_y = available_space - total_button_heights
    # Calculate spacing between buttons
    spacing_x = remaining_space_x / (self.n-1) if len(self.button_syms) > 1 else 0
    spacing_y = remaining_space_y / (self.n-1) if len(self.button_syms) > 1 else 0

    # Create buttons with adjusted positions
    initial_x = BOARD_PADDING + BOARD_SIZE + padding
    initial_y = GAME_CONTROL_HEIGHT + padding
    self.buttons = {}
    for i, sym in enumerate(self.button_syms) :
      width, height = (
        .95*available_space/self.n,
        .95*available_space/self.n
      )
      top_left_pos = (
        initial_x + (width + spacing_x)*(i%self.n),
        initial_y + (height + spacing_y)*(i//self.n)
      )
      self.buttons[sym] = Button(
        width_height=(width, height),
        text=sym, text_size=int(NUM_FONT_SIZE(self.n)),
        border_width=3, border_radius=5, border_color=NUMPAD_BORDER_COLOR,
        top_left_pos=top_left_pos, bg_color=NUMPAD_BG
      )

  def draw(self, screen:pygame.Surface) -> None :
    for button in self.buttons.values() :
      button.render(screen)