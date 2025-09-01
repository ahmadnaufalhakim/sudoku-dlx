from collections import defaultdict

# Constants for sudoku objects
## Representation for empty cell
EMPTY = -1
## For sudoku with n<=3
NORMAL_SUDOKU_INT2SYM = defaultdict(lambda: '.')
for i in range(9) :
  NORMAL_SUDOKU_INT2SYM[i] = str(i+1)
NORMAL_SUDOKU_SYM2INT = defaultdict(lambda: -1)
for k, v in NORMAL_SUDOKU_INT2SYM.items() :
  NORMAL_SUDOKU_SYM2INT[v] = k

## For sudoku with n==4
SUDOKU_4_INT2SYM = defaultdict(lambda: '.')
for i in range(16) :
  if i//10 :
    SUDOKU_4_INT2SYM[i] = chr(i%10+ord('A'))
  else :
    SUDOKU_4_INT2SYM[i] = str(i)
SUDOKU_4_SYM2INT = defaultdict(lambda: -1)
for k, v in SUDOKU_4_INT2SYM.items() :
  SUDOKU_4_SYM2INT[v] = k

## For sudoku with n==5
SUDOKU_5_INT2SYM = defaultdict(lambda: '.')
for i in range(25) :
  SUDOKU_5_INT2SYM[i] = chr(i+ord('A'))
SUDOKU_5_SYM2INT = defaultdict(lambda: -1)
for k, v in SUDOKU_5_INT2SYM.items() :
  SUDOKU_5_SYM2INT[v] = k

# Constants for the GUI layout
## Sizes
WINDOW_WIDTH = 1300
WINDOW_HEIGHT = 975
BOARD_PADDING = 40
GAME_INFO_HEIGHT = 100
GAME_INFO_FONT_SIZE = 30
GAME_CONTROL_HEIGHT = WINDOW_HEIGHT/4
GAME_NUMPAD_HEIGHT = WINDOW_HEIGHT/2
GAME_MENU_HEIGHT = WINDOW_HEIGHT/4
GAME_CONTROL_FONT_SIZE = 31
GAME_MENU_FONT_SIZE = 48
DIFFICULTY_MENU_FONT_SIZE = 31
BOARD_SIZE = WINDOW_HEIGHT - (GAME_INFO_HEIGHT + 2*BOARD_PADDING)
CELL_SIZE = lambda n : BOARD_SIZE / n**2
NUM_FONT_SIZE = lambda n : .36*BOARD_SIZE / n**1.38
CAND_FONT_SIZE = lambda n : 3*NUM_FONT_SIZE(n) / (2*n)
FPS = 60

## Colors
WHITE = (240, 240, 240)
BLACK = (0, 0, 0)
GRAY = (95, 95, 95)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (70, 130, 180)
ORANGE = (255, 127, 0)
CYAN = (0, 255, 255)
LIGHT_BLUE = (180, 200, 240)
BLUEISH_GRAY = (144, 160, 192)

#
CORRECT_NUM_COLOR = GAME_MENU_BG = (37, 206, 209) #1
CORRECT_NUM_BG = (tuple(min(c+144, 255) for c in CORRECT_NUM_COLOR))
GAME_MENU_BORDER_COLOR = (tuple(max(c-32, 0) for c in GAME_MENU_BG))
MAIN_BG = (240, 240, 240) #2
HIGHLIGHTED_CELL_BG = NUMPAD_BG = DIFFICULTY_BG = (252, 234, 222) #3
NUMPAD_BORDER_COLOR = DIFFICULTY_BORDER_COLOR = (tuple(max(c-32, 0) for c in NUMPAD_BG))
HIGHLIGHTED_NUM_BG = GAME_CONTROL_BG = DIFFICULTY_MENU_BG = (255, 138, 91) #4
GAME_CONTROL_BORDER_COLOR = DIFFICULTY_MENU_BORDER_COLOR = (tuple(max(c-32, 0) for c in GAME_CONTROL_BG))
INCORRECT_NUM_COLOR = (234, 82, 111) #5
INCORRECT_NUM_BG = (tuple(min(c+144, 255) for c in INCORRECT_NUM_COLOR))