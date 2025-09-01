import math
import pygame

from constants import (
  WINDOW_WIDTH, WINDOW_HEIGHT,
  BOARD_PADDING, BOARD_SIZE,
  GAME_MENU_HEIGHT,
  GAME_MENU_BG, GAME_MENU_BORDER_COLOR, GAME_MENU_FONT_SIZE,
  DIFFICULTY_MENU_BG, DIFFICULTY_MENU_BORDER_COLOR, DIFFICULTY_MENU_FONT_SIZE,
  DIFFICULTY_BG, DIFFICULTY_BORDER_COLOR,
  WHITE
)
from display.button import Button
from display.game_info import GameInfo
from sudoku import Sudoku

class GameMenu :
  def __init__(self, sudoku:Sudoku, game_info:GameInfo) -> None:
    self.sudoku = sudoku
    self.game_info = game_info
    self.button_texts = ["New Game", "Pause Timer"]
    self.difficulty_button_texts = ["Easy", "Medium", "Hard", "Extreme", "Restart"]
    self.is_new_game_active = False
    self.is_confirmation_active = False

    # Upper padding
    padding = BOARD_PADDING
    # Calculate the total button height
    available_space = GAME_MENU_HEIGHT - 2*padding
    total_button_heights = sum(
      min(.95*available_space/len(self.button_texts), available_space)
      for _ in range(len(self.button_texts))
    )
    remaining_space = available_space - total_button_heights

    # Calculate the remaining space
    spacing = remaining_space / (len(self.button_texts)-1) if len(self.button_texts) > 1 else 0
    # Create buttons with adjusted positions
    current_y = WINDOW_HEIGHT - GAME_MENU_HEIGHT
    self.buttons = {}
    for _, text in enumerate(self.button_texts) :
      width, height = (
        WINDOW_WIDTH - (BOARD_PADDING + BOARD_SIZE + 2*padding),
        min(.95*available_space/len(self.button_texts), available_space),
      )
      # Center position adjusted based on current_y (starting from up and adding spacing)
      center_pos = (
        BOARD_PADDING + BOARD_SIZE + padding + width/2,
        current_y + height/2
      )
      self.buttons[text] = Button(
        width_height=(width, height),
        text=text, text_size=GAME_MENU_FONT_SIZE,
        border_width=2, border_radius=15, border_color=GAME_MENU_BORDER_COLOR,
        center_pos=center_pos, bg_color=GAME_MENU_BG,
        toggle_button=True if "Timer" in text else None,
        toggle_state=False if "Timer" in text else None
      )
      # Update current_y to account for the button height and the spacing between buttons
      current_y += height + spacing

  def press(self, button_text:str) -> None :
    if button_text == "Pause Timer" or button_text == "Resume Timer" :
      if self.game_info.is_paused :
        self.game_info.start_timer()
      else :
        self.game_info.pause_timer()
    elif button_text == "New Game" :
      self.is_new_game_active = not self.is_new_game_active

  def draw(self, screen:pygame.Surface) -> None :
    self.buttons["New Game"].render(screen)
    if not self.game_info.is_paused :
      self.buttons["Pause Timer"].update_text("Pause Timer")
    else :
      self.buttons["Pause Timer"].update_text("Resume Timer")
    self.buttons["Pause Timer"].render(screen)
    if self.is_new_game_active :
      # self.draw_confirmation(screen)
      self.draw_new_game_menu(screen)

  def draw_new_game_menu(self, screen:pygame.Surface) -> None :
    # Draw upside down triangle
    downmost_point = (
      BOARD_SIZE + 2*BOARD_PADDING + self.buttons["New Game"].width_height[0]/2,
      WINDOW_HEIGHT - GAME_MENU_HEIGHT
    )
    triangle_scale = 15
    triangle_points = [
      (downmost_point[0]-triangle_scale, downmost_point[1]-math.sqrt(3)*triangle_scale),
      downmost_point,
      (downmost_point[0]+triangle_scale, downmost_point[1]-math.sqrt(3)*triangle_scale),
    ]
    pygame.draw.polygon(
      surface=screen,
      color=DIFFICULTY_MENU_BG,
      points=triangle_points
    )
    pygame.draw.polygon(
      surface=screen,
      color=DIFFICULTY_MENU_BORDER_COLOR,
      points=triangle_points,
      width=2
    )
    # Draw difficulty menu box
    

  def draw_confirmation(self, screen:pygame.Surface) -> None :
    surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    surface.set_alpha(192)
    surface.fill(WHITE)
    screen.blit(source=surface, dest=(0, 0))
    # confirmation_surface = pygame.Surface()