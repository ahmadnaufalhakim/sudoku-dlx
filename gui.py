import pygame
import random

from constants import (
  WINDOW_WIDTH, WINDOW_HEIGHT,
  MAIN_BG
)
from display.game_control import GameControl
from display.game_info import GameInfo
from display.game_menu import GameMenu
from display.sudoku_board import SudokuBoard
from display.numpad import Numpad
from sudoku import Sudoku

def new_game() :
  pass

if __name__ == "__main__" :
  sdk = Sudoku(3)
  screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
  pygame.display.set_caption("Sudoku dlx")
  pygame.font.init()
  clr_palette = random.choice(list(range(len(MAIN_BG))))

  # New game
  pygame.time.set_timer(pygame.USEREVENT, 0)
  print("b4", sdk.difficulty)
  sdk.generate_new_puzzle("easy")
  print("aftr", sdk.difficulty)
  pygame.time.set_timer(pygame.USEREVENT, 1000)
  game_info = GameInfo(sdk)
  sdk_board = SudokuBoard(sdk)
  game_ctrl = GameControl(sdk, sdk_board)
  numpad = Numpad(sdk)
  game_menu = GameMenu(sdk, game_info)
  game_info.start_timer()
  running = True

  while running :
    screen.fill(MAIN_BG)
    game_info.draw(screen)
    sdk_board.draw(screen)
    game_ctrl.draw(screen)
    numpad.draw(screen)
    game_menu.draw(screen)
    events = pygame.event.get()

    for event in events :
      # idk what this does??
      # pygame.event.pump()
      if event.type == pygame.QUIT :
        running = False
      if event.type == pygame.MOUSEBUTTONDOWN :
        if pygame.mouse.get_pressed()[0] :
          x, y = pygame.mouse.get_pos()
          sdk_board.select_cell(x, y)
      if event.type == pygame.KEYDOWN :
        if (event.key in range(pygame.K_0, pygame.K_9+1) or
            event.key in range(pygame.K_a, pygame.K_z+1)) :
          if game_ctrl.pencil_mode :
            sdk_board.add_candidate(pygame.key.name(event.key).upper())
          else :
            sdk_board.set_cell(pygame.key.name(event.key).upper())
        if (event.key in range(pygame.K_RIGHT, pygame.K_UP+1)) :
          sdk_board.move(event)
        if (event.key in [pygame.K_BACKSPACE, pygame.K_DELETE]) :
          sdk_board.erase_cell()
        if (event.key == pygame.K_ESCAPE) :
          sdk_board.deselect_cell()
      if event.type == pygame.USEREVENT :
        game_info.tick()

    for k, v in game_ctrl.buttons.items() :
      if v.is_clicked(events) :
        game_ctrl.press(k)

    for k, v in numpad.buttons.items() :
      if v.is_clicked(events) :
        if game_ctrl.pencil_mode :
          sdk_board.add_candidate(k)
        else :
          sdk_board.set_cell(k)

    for k, v in game_menu.buttons.items() :
      if v.is_clicked(events) :
        print(k)
        game_menu.press(k)
        # break


    pygame.display.flip()