from math import sin, cos, atan2, radians
from random import choice
import curses

from util import clamp, dist
from explosion import Explosion

def lines():
  return {
    ( 1, 1) : '\\',
    ( 1, 0) : '|',
    ( 1,-1) : '/',
    ( 0, 1) : '-',
    ( 0, 0) : '',
    ( 0,-1) : '-',
    (-1, 1) : '/',
    (-1, 0) : '|',
    (-1,-1) : '\\'
  }

class Shot():
  char = '●'
  def __init__(self, x, y, angle, power, owner, conf):
    self.x        = x
    self.y        = y
    self.tail     = []
    self.speed_x  = power * cos(angle)
    self.speed_y  = power * sin(angle)
    self.age      = 0
    self.owner    = owner
    self.world    = owner.world
    self.conf     = conf

  def draw(self, win):
    h, w =win.getmaxyx()
    if(self.y < 0):
      c = '^'
    elif(self.x < 0):
      c = '<'
    elif(self.x > w):
      c = '>'
    else:
      c = self.char
    display_y = clamp(int(self.y), 0, h-1)
    display_x = clamp(int(self.x), 0, w-1)
    if(self.age>3):
      try:
        if(self.x >= 0 and self.x < w and self.y >= 0 and self.y < h):
          for i,tup in enumerate(self.tail):
            next = (self.tail + [(display_y, display_x)])[i+1]
            dif_y = -1 if (next[0] < tup[0]) else (1 if (next[0] > tup[0]) else 0)
            dif_x = -1 if (next[1] < tup[1]) else (1 if (next[1] > tup[1]) else 0)
            d = lines()[(dif_y, dif_x)]
            win.addstr(tup[0], tup[1], choice(['⁙','⁖',d, d]))
        win.addstr(display_y, display_x, c)
      except curses.error:
        pass
    self.tail += [(display_y, display_x)]
    if(len(self.tail) > self.conf['shot_tail']):
      self.tail = self.tail[1:]

  def despawn(self):
    self.owner.isdone = True
    self.world.gameobjects.remove(self)
    del(self)
  def explode(self):
    self.world.gameobjects += [Explosion(self.x, self.y, self.owner, 30, 5)]
    self.despawn()
  def update(self, win):
    self.x, self.y = self.world.moveby(self.x, self.y, self.speed_x, -self.speed_y)
    self.speed_x += self.conf['wind_force']*self.world.wind
    self.speed_y -= self.conf['gravity'] * 0.001
    h, w = win.getmaxyx()
    if (self.y > h):
      self.despawn()
      return
    elif (self.age > self.conf['shot_age'] or self.world.check_collision(self.x, self.y)
        or min([dist(self, p) for p in self.world.players]) < 2):
      self.explode()
      return
    self.age += 1
    
class Heavy_shot(Shot):
  char = '☢'
  def __init__(self, x, y, angle, power, owner, conf):
    Shot.__init__(self, x, y, angle, power, owner, conf)
  def explode(self):
    self.world.gameobjects += [Explosion(self.x, self.y, self.owner, 50, 8)]
    self.despawn()

class Drill_shot(Shot):
  char = '⁂'
  def __init__(self, x, y, angle, power, owner, conf):
    Shot.__init__(self, x, y, angle, power, owner, conf)
    self.explosions = 3
  def explode(self):
    self.world.gameobjects += [Explosion(self.x, self.y, self.owner, 15, 4)]
    self.explosions -= 1
    if(self.explosions == 0):
      self.despawn()

class Teleporter(Shot):
  char = '🌀'
  def __init__(self, x, y, angle, power, owner, conf):
    Shot.__init__(self, x, y, angle, power, owner, conf)
  def explode(self):
    self.owner.x, self.owner.y = int(self.x), int(self.y)-2
    self.despawn()

class Dirt_wedge(Shot):
  char = '⛏'
  def __init__(self, x, y, angle, power, owner, conf):
    Shot.__init__(self, x, y, angle, power, owner, conf)
    self.wedge_points = []
    self.angle = angle
    self.x, self.y = self.world.moveby(self.x, self.y, -3*cos(angle), 3*sin(angle))
  def update(self, win):
    self.age += 1
    for i in range(2*self.age):
      angle = self.angle + radians(25 * (-1 + i/self.age))
      x,y = self.world.moveby(self.x, self.y, cos(angle)*self.age, -sin(angle)*self.age)
      self.wedge_points += [(int(x), int(y))]
      self.world.destroy_ground(int(x), int(y))
    if(self.age >= 10):
      self.despawn()
  def draw(self, win):
    h, w = win.getmaxyx()
    for (x, y) in self.wedge_points:
      win.addch(y, x, '🞿')
  def explode(self):
    self.owner.x, self.owner.y = int(self.x), int(self.y)-3
    self.despawn()
