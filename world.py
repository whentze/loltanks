from random import choice, randint, uniform
import curses

from util import clamp
from tank import Tank
import blockgraphics

waves =[[1,1,1,1,1,0,0,0,0,0],
        [0,0,0,0,1,1,1,1,1,0]]

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
    self.ground = ground
    self.groundchars =  [['█']                 *h for x in range(w)]
    self.groundstyle  = conf['ground_style']
    for x in range(w):
      for y in range(h):
        self.paint(x, y)

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
    self.conf         = conf
    self.players      = players
    self.gameobjects  = gameobjects
    
    if(self.groundstyle == 'Dirt'):
      # green
      curses.init_color(101,  400,  700,  100)
      # brown
      curses.init_color(102,  300,  200,  100)
      # dirt/grass
      curses.init_pair(7, 101, 102)
      self.groundcolor = curses.color_pair(7)
    elif(self.groundstyle == 'Candy'):
      # pink
      curses.init_color(101, 1000,  300,  800)
      # purple
      curses.init_color(102,  800,    0,  600)
      # candy 
      curses.init_pair(7, 101, 102)
      self.groundcolor = curses.color_pair(7)
    else:
      self.groundcolor = curses.color_pair(0)

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
    try:
      for x, col in enumerate(self.ground):
        for y, cell in enumerate(col):
          if(cell):
              win.addch(y, x, self.groundchars[x][y], self.groundcolor)
    except curses.error:
      # The very last character will error so except only once
      pass

  def destroy_ground(self, x, y):
    self.ground[x][y] = False
    if(self.groundstyle in ['Silhouette', 'Pipes']):
      for xi in range(max(0, x-1), min(len(self.ground), x+2)):
        for yi in range(max(0, y-1), min(len(self.ground[0]), y+2)):
          self.paint(xi, yi)

  def paint(self, x, y):
    if(self.ground[x][y]):
      h, w = len(self.ground[0]), len(self.ground)
      if(self.groundstyle == 'Block'):
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
        c = blockgraphics.blocks[block]
      elif(self.groundstyle == 'Dirt'):
        grass = clamp(max([0]+[y-yi for yi in range(0, y) if self.ground[x][yi]]), 0, 4)
        c = ['█', '▓', '▒', '░', ' '][grass]
      elif(self.groundstyle == 'Candy'):
        block = (waves[0][(x*2  +2*y)%10],
                 waves[0][(x*2+1+2*y)%10],
                 waves[1][(x*2  +2*y)%10],
                 waves[1][(x*2+1+2*y)%10])
        c = blockgraphics.blocks[block]
      elif(self.groundstyle == 'Pipes'):
        neighbors = (self.ground[x][y-1] or y % 4 == 0,
                     self.ground[x-1][y] or y % 4 == 0,
                     self.ground[(x+1)%w][y] or x % 4 == 0,
                     self.ground[x][(y+1)%h] or x % 4 == 0)
        c = blockgraphics.pipes[neighbors]
      self.groundchars[x][y] = c

  def check_collision(self, x, y):
    if (y >= len(self.ground[0])):
      return True
    elif(x < 0 or x >= len(self.ground) or y < 0):
      return False
    else:
      return self.ground[int(x)][int(y)]
