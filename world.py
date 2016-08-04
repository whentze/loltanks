from random import choice, randint, uniform, shuffle
import curses

from util import clamp, Point
from tank import Tank
from portal import Portal
import blockgraphics

waves =[[1,1,1,1,1,0,0,0,0,0],
        [0,0,0,0,1,1,1,1,1,0]]

GROUNDFG   = 101
GROUNDBG   = 102
GROUNDPAIR = 7
SKYBG      = 103
SKYPAIR    = 8

class World():
  def __init__(self, win, conf):
    h, w = win.getmaxyx()
    ground = [[False]*h for x in range(w)]
    portal_radius = h//12
    portal_size = 2*portal_radius + 1

    changes = [1, -1] * int(w*conf['ground_steepness']/2)
    changes += [-portal_size, portal_size]
    changes += [0] * (w - len(changes))
    assert len(changes) == w
    shuffle(changes)
    min_y = int(h*conf['sky_min'])
    max_y = int(h*(1-conf['ground_min']))
    if(min_y >= max_y):
       raise RuntimeError('Your sky_min and/or ground_min are too large for this terminal')
    levels = [randint(min_y, max_y)]
    for x in range(w-1):
      next_y = levels[-1] + changes[0]
      while(next_y < min_y or next_y > max_y):
        shuffle(changes)
        next_y = levels[-1] + changes[0]
      levels += [next_y]
      if(changes[0] == portal_size):
        self.portal_red = Portal(Point(x+1, next_y - portal_radius, self), 'y', portal_radius, curses.color_pair(1))
      if(changes[0] == -portal_size):
        self.portal_blue = Portal(Point(x, next_y + portal_radius + 1, self), 'y', portal_radius, curses.color_pair(2))
      changes = changes[1:]
    for x in range(w):
      for y in range(h):
        ground[x][y] = levels[x] < y
    self.ground = ground
    self.groundchars =  [['█']                 *h for x in range(w)]
    self.style  = conf['world_style']
    self.border = conf['world_border']
    for x in range(w):
      for y in range(h):
        self.paint(x, y)

    gameobjects = [self]
    try:
      gameobjects += [self.portal_red, self.portal_blue]
      self.portal_red.other = self.portal_blue
      self.portal_blue.other = self.portal_red
    except NameError:
      self.portals = False
    finally:
      self.portals = True
    players     = []
    for i in range(conf['players_number']):
      curses.init_pair(i+1, conf['players_colors'][i], SKYBG)
      x = int(w*(i+1.0)/(conf['players_number']+1))
      newplayer = Tank((x, min(levels[x-2:x+3])), "Player {:d}".format(i+1), i+1, self, conf)
      players += [newplayer]
      gameobjects += [newplayer]

    self.wind         = randint(-conf['wind_max'], conf['wind_max'])
    
    # init particles
    partcount         = int(h*w*conf['particles_max']/200.0)
    self.particles    = [[uniform(0,w-1),uniform(0,h-1),uniform(20,80)]
        for i in range(partcount)]

    self.conf         = conf
    self.players      = players
    self.gameobjects  = gameobjects
    
    if(self.style == 'Dirt'):
      # green
      curses.init_color(GROUNDFG,  400,  700,  100)
      # brown
      curses.init_color(GROUNDBG,  300,  200,  100)
      # dark blue
      curses.init_color(SKYBG,       0,    0,  150)
    elif(self.style == 'Candy'):
      # pink
      curses.init_color(GROUNDFG, 1000,  300,  800)
      # purple
      curses.init_color(GROUNDBG,  800,    0,  600)
      # black
      curses.init_color(SKYBG,       0,    0,    0)
    else:
      # white
      curses.init_color(GROUNDFG, 1000, 1000, 1000)
      # black
      curses.init_color(GROUNDBG,    0,    0,    0)
      # black
      curses.init_color(SKYBG,       0,    0,    0)

    curses.init_pair(GROUNDPAIR, GROUNDFG, GROUNDBG)
    self.groundcolor = curses.color_pair(GROUNDPAIR)
    curses.init_pair(SKYPAIR, curses.COLOR_WHITE, SKYBG)
    self.skycolor = curses.color_pair(SKYPAIR)

  def update(self, win):
    h, w = win.getmaxyx()
    for part in self.particles:
      if(self.conf['particles_type'] == 'Snow'):
        part[0] += self.wind * self.conf['wind_force'] * part[2]
        part[1] += self.conf['gravity'] * part[2] * 0.0002
      if(self.conf['particles_type'] == 'Rain'):
        part[0] += self.wind * self.conf['wind_force'] * part[2]
        part[1] += self.conf['gravity']  * part[2] * 0.001

  def draw(self, win):
    h, w = win.getmaxyx()
    win.bkgdset(' ', self.skycolor)
    # Draw Particles
    parttype = self.conf['particles_type']
    for part in self.particles:
      part[0] = part[0]%w
      part[1] = part[1]%h
      try:
        if(parttype == 'Snow'):
          if(part[2] > 60):
            win.addstr(int(part[1]), int(part[0]), '∗')
          else:
            win.addstr(int(part[1]), int(part[0]), '·')
        elif(parttype == 'Rain'):
          win.addstr(int(part[1]), int(part[0]), '|', curses.color_pair(2))
        elif(parttype == 'Stars'):
          if(randint(0, 200) == 0):
            if(part[2] > 60):
              win.addstr(int(part[1]), int(part[0]), '◆')
            else:
              win.addstr(int(part[1]), int(part[0]), '✦')
          else:
            if(part[2] > 60):
              win.addstr(int(part[1]), int(part[0]), '٭')
            elif(part[2] > 40):
              win.addstr(int(part[1]), int(part[0]), '·')
            else:
              win.addstr(int(part[1]), int(part[0]), '･')
      except curses.error:
        pass

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
    if(self.style in ['Silhouette', 'Pipes']):
      for xi in range(max(0, x-1), min(len(self.ground), x+2)):
        for yi in range(max(0, y-1), min(len(self.ground[0]), y+2)):
          self.paint(xi, yi)

  def paint(self, x, y):
    if(self.ground[x][y]):
      h, w = len(self.ground[0]), len(self.ground)
      if(self.style == 'Block'):
        c = '█'
      elif(self.style == 'Silhouette'):
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
      elif(self.style == 'Dirt'):
        grass = clamp(max([0]+[y-yi for yi in range(0, y) if self.ground[x][yi]]), 0, 4)
        c = ['█', '▓', '▒', '░', ' '][grass]
      elif(self.style == 'Candy'):
        block = (waves[0][(x*2  +2*y)%10],
                 waves[0][(x*2+1+2*y)%10],
                 waves[1][(x*2  +2*y)%10],
                 waves[1][(x*2+1+2*y)%10])
        c = blockgraphics.blocks[block]
      elif(self.style == 'Pipes'):
        neighbors = (self.ground[x][y-1] or y % 4 == 0,
                     self.ground[x-1][y] or y % 4 == 0,
                     self.ground[(x+1)%w][y] or x % 4 == 0,
                     self.ground[x][(y+1)%h] or x % 4 == 0)
        c = blockgraphics.pipes[neighbors]
      self.groundchars[x][y] = c

  def check_collision(self, p):
    if (p.y >= len(self.ground[0])):
      return True
    elif(p.x < 0 or p.x >= len(self.ground)):
      if(self.border == 'Loop'):
        return self.check_collision(Point(p.x%len(self.ground), p.y))
      else:
        return self.border == 'Wall'
    elif(p.y < 0):
      return False
    else:
      return self.ground[int(p.x)][int(p.y)]

  # point moved by x_off, y_off according to this world's rules
  def moveby(self, p, x_off, y_off):
    if(self.portals):
      for portal in [self.portal_red, self.portal_blue]:
        x_dif = portal.pos.x - p.x
        y_dif = portal.pos.y - p.y
        if(portal.dimension == 'x'):
          if((p.y < portal.pos.y and p.y + y_off >= portal.pos.y or 
              p.y > portal.pos.y and p.y + y_off <= portal.pos.y) and
              abs(x_dif) < portal.radius):
            return Point(portal.other.pos.x + x_off - x_dif, portal.other.pos.y + y_off - y_dif, self)
        elif(portal.dimension == 'y'):
          if((p.x <= portal.pos.x and p.x + x_off > portal.pos.x) and
              abs(y_dif) < portal.radius):
            return Point(portal.other.pos.x + x_off - x_dif, portal.other.pos.y + y_off - y_dif, self)
          elif((p.x > portal.pos.x and p.x + x_off <= portal.pos.x) and
              abs(y_dif) < portal.radius):
            return Point(portal.other.pos.x + x_off - x_dif, portal.other.pos.y + y_off - y_dif, self)
    if(self.border == 'Loop'):
      return Point((p.x+x_off)%len(self.ground) , p.y + y_off, self)
    else:
      return Point(p.x + x_off, p.y + y_off, self)
