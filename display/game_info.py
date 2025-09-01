import pygame

from constants import (
  WINDOW_HEIGHT,
  BOARD_PADDING, BOARD_SIZE,
  GAME_INFO_HEIGHT, GAME_INFO_FONT_SIZE,
  BLACK
)
from sudoku import Sudoku

pygame.init()

class GameInfo :
  def __init__(self, sudoku:Sudoku) -> None :
    self.difficulty = sudoku.difficulty.capitalize() if sudoku.difficulty is not None else '-'
    self.is_paused = True
    self.current_seconds = 0
    self.mistakes = 0

  def pause_timer(self) -> None :
    self.is_paused = True

  def restart_timer(self) -> None :
    self.pause_timer()
    self.current_seconds = 0

  def start_timer(self) -> None :
    self.is_paused = False

  def tick(self) -> None :
    # print("self.is_paused ==", self.is_paused)
    if not self.is_paused :
      self.current_seconds += 1

  def draw(self, screen:pygame.Surface) -> None :
    self.draw_difficulty(screen)
    self.draw_timer(screen)
    self.draw_mistakes(screen)

  def increment_mistake(self) -> None :
    self.mistakes += 1

  def draw_difficulty(self, screen:pygame.Surface) -> None :
    # Draw difficulty info
    font = pygame.font.Font(None, GAME_INFO_FONT_SIZE)
    text_surface = font.render(f"Difficulty : {self.difficulty}", True, BLACK)
    screen.blit(
      source=text_surface,
      dest=(
        BOARD_PADDING,
        (BOARD_PADDING + BOARD_SIZE) + 1.25*(GAME_INFO_HEIGHT)/4
      )
    )

  def draw_timer(self, screen:pygame.Surface) -> None :
    # Draw timer info
    if self.current_seconds >= 0 :
      seconds = self.current_seconds%60
      minutes = (self.current_seconds//60)%60
      hours = (self.current_seconds//60)//60
    text = f"{f'{hours:02}:' if hours else ''}{minutes:02}:{seconds:02}"

    font = pygame.font.Font(None, GAME_INFO_FONT_SIZE)
    text_surface = font.render(f"Time elapsed : {text}", True, BLACK)
    screen.blit(
      source=text_surface,
      dest=(
        BOARD_PADDING,
        (BOARD_PADDING + BOARD_SIZE) + 2.5*(GAME_INFO_HEIGHT)/4
      )
    )

  def draw_mistakes(self, screen:pygame.Surface) -> None :
    # Draw mistakes info
    font = pygame.font.Font(None, GAME_INFO_FONT_SIZE)
    text_surface = font.render(f"Mistakes : {self.mistakes}", True, BLACK)
    screen.blit(
      source=text_surface,
      dest=(
        BOARD_PADDING,
        (BOARD_PADDING + BOARD_SIZE) + 3.75*(GAME_INFO_HEIGHT)/4
      )
    )