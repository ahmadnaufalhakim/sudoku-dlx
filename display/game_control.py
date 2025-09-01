from collections import deque
import pygame

from display.button import Button
from display.sudoku_board import SudokuBoard
from constants import (
  WINDOW_WIDTH, WINDOW_HEIGHT,
  BOARD_PADDING, BOARD_SIZE,
  GAME_CONTROL_HEIGHT, GAME_CONTROL_FONT_SIZE,
  GAME_CONTROL_BG, GAME_CONTROL_BORDER_COLOR,
  BLACK
)
from sudoku import Sudoku

class GameControl :
  def __init__(self, sudoku:Sudoku, sudoku_board:SudokuBoard, color_palette:int=0) -> None :
    self.sudoku = sudoku
    self.sudoku_board = sudoku_board
    self.color_palette = color_palette
    self.history = deque(maxlen=10)
    self.pencil_mode = False
    self.button_texts = ["Undo", "Erase", "Pencil", "Hint", "Solve"]

    # Side padding constant for game control buttons
    side_padding = BOARD_PADDING
    # Calculate the total button width based on text length
    total_button_widths = sum(
      min((WINDOW_WIDTH - (BOARD_PADDING + BOARD_SIZE))/len(self.button_texts)*1.25, 14*len(text))
      for text in self.button_texts
    )
    # Calculate the remaining space after all button widths, accounting for side padding
    available_space = (WINDOW_WIDTH - (BOARD_PADDING + BOARD_SIZE)) - 2*side_padding
    remaining_space = available_space - total_button_widths
    # Calculate spacing between buttons
    spacing = remaining_space / (len(self.button_texts)-1) if len(self.button_texts) > 1 else 0
    # Create buttons with adjusted positions
    current_x = BOARD_PADDING + BOARD_SIZE + side_padding
    self.buttons = {}
    for _, text in enumerate(self.button_texts) :
      width, height = (
        min((WINDOW_WIDTH - (BOARD_PADDING + BOARD_SIZE))/len(self.button_texts)*1.25, 14*len(text)),
        GAME_CONTROL_FONT_SIZE*1.5
      )
      # Center position adjusted based on current_x (starting from left and adding spacing)
      center_pos = (
        current_x + width/2,
        (GAME_CONTROL_HEIGHT)/2
      )
      self.buttons[text] = Button(
        width_height=(width, height),
        text=text, text_size=GAME_CONTROL_FONT_SIZE,
        border_width=2, border_radius=10, border_color=GAME_CONTROL_BORDER_COLOR,
        center_pos=center_pos, bg_color=GAME_CONTROL_BG,
        toggle_button=True if text=="Pencil" else None,
        toggle_state=self.pencil_mode if text=="Pencil" else None
      )
      # Update current_x to account for the button width and the spacing between buttons
      current_x += width + spacing

  def press(self, button_text:str) -> None :
    if button_text == "Undo" :
      print("undo action")
    elif button_text == "Erase" :
      self.sudoku_board.erase_cell()
    elif button_text == "Pencil" :
      self.pencil_mode = not self.pencil_mode
      print("pencil mode is now", self.pencil_mode)
    elif button_text == "Hint" :
      print("hinting")
    elif button_text == "Solve" :
      print("solving")

  def add_action_to_history(self, action) -> None :
    self.history.append(action)

  def reset_history(self) -> None :
    self.history.clear()

  def draw(self, screen:pygame.Surface) -> None :
    for button in self.buttons.values() :
      button.render(screen)
    font = pygame.font.Font(None, GAME_CONTROL_FONT_SIZE)
    text = f"Pencil mode is {f'in' if not self.pencil_mode else ''}active{f'' if not self.pencil_mode else '!'}"
    text_surface = font.render(text, True, BLACK)
    text_surface_rect = text_surface.get_rect(topleft=(
      2*BOARD_PADDING + BOARD_SIZE,
      GAME_CONTROL_HEIGHT - BOARD_PADDING
    ))
    screen.blit(source=text_surface, dest=text_surface_rect)