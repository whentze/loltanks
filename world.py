from random import choice, randint, uniform
import curses

from util import clamp
from tank import Tank

def pipes(tup):
  return {
    ( True , True , True , True ) : '╬',
    ( True , True , True , False) : '╩',
    ( True , True , False, True ) : '╦',
    ( True , True , False, False) : '═',
    ( True , False, True , True ) : '╣',
    ( True , False, True , False) : '╝',
    ( True , False, False, True ) : '╗',
    ( True , False, False, False) : '╡',
    ( False, True , True , True ) : '╠',
    ( False, True , True , False) : '╚',
    ( False, True , False, True ) : '╔',
    ( False, True , False, False) : '╞',
    ( False, False, True , True ) : '║',
    ( False, False, True , False) : '╨',
    ( False, False, False, True ) : '╥',
    ( False, False, False, False) : '◽',
  }[tup]

def blocks(tup):
  return {
    ( True , True , True , True ) : '█',
    ( True , True , True , False) : '▛',
    ( True , True , False, True ) : '▜',
    ( True , True , False, False) : '▀',
    ( True , False, True , True ) : '▙',
    ( True , False, True , False) : '▌',
    ( True , False, False, True ) : '▚',
    ( True , False, False, False) : '▘',
    ( False, True , True , True ) : '▟',
    ( False, True , True , False) : '▞',
    ( False, True , False, True ) : '▐',
    ( False, True , False, False) : '▝',
    ( False, False, True , True ) : '▄',
    ( False, False, True , False) : '▖',
    ( False, False, False, True ) : '▗',
    ( False, False, False, False) : ' ',
  }[tup]

class World():
  def __init__(self, win, conf):
    h, w = win.getmaxyx()
    ground = [[False]*h for x in range(w)]
    levels = [randint(conf['sky_min'], h - conf['ground_min'])]
    for x in range(1, w):
      levels += [clamp(
          levels[-1] + choice([0,0,-1,1]),
          conf['sky_min'],
          h - conf['ground_min'])]
    
    for x in range(w):
      for y in range(h):
        ground[x][y] = levels[x] < y

    gameobjects = [self]
    players     = []
    for i in range(conf['players_number']):
      curses.init_pair(i+1, conf['players_colors'][i], curses.COLOR_BLACK)
      x = int(w*(i+1.0)/(conf['players_number']+1))
      newplayer = Tank(x, min(levels[x-2:x+3]), "Player {:d}".format(i+1), i+1, self, conf)
      players += [newplayer]
      gameobjects += [newplayer]

    self.wind         = randint(-conf['wind_max'], conf['wind_max'])
    self.snow         = int(h*w*conf['snow_max']/100.0)
    self.snowflakes   = [[uniform(0,w-1),uniform(0,h-1),uniform(1,80)] for i in range(self.snow)]
    self.ground       = ground
    self.groundstyle  = conf['ground_style']
    self.conf         = conf
    self.players      = players
    self.gameobjects  = gameobjects

  def update(self, win):
    h, w = win.getmaxyx()
    for flake in self.snowflakes:
      flake[0] += self.wind * self.conf['wind_force'] * flake[2]
      flake[1] += self.conf['gravity'] * flake[2] * 0.0002

  def draw(self, win):
    # Draw Snow
    h, w = win.getmaxyx()
    for flake in self.snowflakes:
      try:
        if(flake[2] > 60):
          win.addstr(int(flake[1]), int(flake[0]), '∗')
        else:
          win.addstr(int(flake[1]), int(flake[0]), '·')
      except curses.error:
        flake[0] = flake[0]%w
        flake[1] = flake[1]%h
    # Draw Ground
    for x, col in enumerate(self.ground):
      for y, cell in enumerate(col):
        if(cell):
          if(self.groundstyle == 'Snow'):
            c = '█'
          elif(self.groundstyle == 'Silhouette'):
            neighbors = (self.ground[x-1][y],
                         self.ground[(x+1)%w][y],
                         self.ground[x][y-1],
                         self.ground[x][min(y+1,h-1)])
            diags =(self.ground[x-1][y-1],
                    self.ground[(x+1)%w][y-1],
                    self.ground[x-1][min(y+1,h-1)],
                    self.ground[(x+1)%w][min(y+1,h-1)])
            block = ( not(neighbors[0] and neighbors[2] and diags[0]),
                      not(neighbors[1] and neighbors[2] and diags[1]),
                      not(neighbors[0] and neighbors[3] and diags[2]),
                      not(neighbors[1] and neighbors[3] and diags[3])) 
            c = blocks(block)
          elif(self.groundstyle == 'Pipes'):
            neighbors = (self.ground[x-1][y] or y % 4 == 0,
                         self.ground[(x+1)%w][y] or y % 4 == 0,
                         self.ground[x][y-1] or x % 4 == 0,
                         self.ground[x][(y+1)%h] or x % 4 == 0)
            c = pipes(neighbors)
          try:
            win.addstr(y, x, c)
          except curses.error:
            pass

  def check_collision(self, x, y):
    if (y >= len(self.ground[0])):
      return True
    elif(x < 0 or x >= len(self.ground) or y < 0):
      return False
    else:
      return self.ground[int(x)][int(y)]
