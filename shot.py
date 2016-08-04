from math import sin, cos, atan2, radians
from random import choice
import curses

from util import clamp, dist, Point
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
  def __init__(self, pos, angle, power, owner, conf):
    self.pos      = pos
    self.tail     = []
    self.speed_x  = power * cos(angle)
    self.speed_y  = power * sin(angle)
    self.age      = 0
    self.owner    = owner
    self.world    = owner.world
    self.conf     = conf
    owner.active_shots += 1

  def draw(self, win):
    h, w =win.getmaxyx()
    if(self.pos.y < 0):
      c = '^'
    elif(self.pos.x < 0):
      c = '<'
    elif(self.pos.x > w):
      c = '>'
    else:
      c = self.char
    display = self.pos.clamp(0, w-1, 0, h-1).int()
    if(self.age>3):
      try:
        if(self.pos.in_box(0, w, 0, h)):
          for i,tup in enumerate(self.tail):
            next = (self.tail + [(display.y, display.x)])[i+1]
            dif_y = -1 if (next[0] < tup[0]) else (1 if (next[0] > tup[0]) else 0)
            dif_x = -1 if (next[1] < tup[1]) else (1 if (next[1] > tup[1]) else 0)
            d = lines()[(dif_y, dif_x)]
            win.addstr(tup[0], tup[1], choice(['⁙','⁖',d, d]))
        win.addstr(display.y, display.x, c)
      except curses.error:
        pass
    self.tail += [(display.y, display.x)]
    if(len(self.tail) > self.conf['shot_tail']):
      self.tail = self.tail[1:]

  def despawn(self):
    self.owner.active_shots -= 1
    self.world.gameobjects.remove(self)
    del(self)
  def explode(self):
    self.world.gameobjects += [Explosion(self.pos, self.owner, 30, 5)]
    self.despawn()
  def update(self, win):
    self.pos += (self.speed_x, -self.speed_y)
    self.speed_x += self.conf['wind_force']*self.world.wind
    self.speed_y -= self.conf['gravity'] * 0.001
    h, w = win.getmaxyx()
    if (self.age > self.conf['shot_age'] or self.world.check_collision(self.pos)
        or min([dist(self.pos, p.pos) for p in self.world.players]) < 2):
      self.explode()
      return
    self.age += 1
    
class Heavy_shot(Shot):
  char = '☢'
  def __init__(self, pos, angle, power, owner, conf):
    Shot.__init__(self, pos, angle, power, owner, conf)
  def explode(self):
    self.world.gameobjects += [Explosion(self.pos, self.owner, 50, 8)]
    self.despawn()

class Drill_shot(Shot):
  char = '⁂'
  def __init__(self, pos, angle, power, owner, conf):
    Shot.__init__(self, pos, angle, power, owner, conf)
    self.explosions = 3
  def explode(self):
    self.world.gameobjects += [Explosion(self.pos, self.owner, 15, 4)]
    self.explosions -= 1
    if(self.explosions == 0):
      self.despawn()

class Teleporter(Shot):
  char = '🌀'
  def __init__(self, pos, angle, power, owner, conf):
    Shot.__init__(self, pos, angle, power, owner, conf)
  def explode(self):
    self.owner.pos = self.pos.int() + (0, -2)
    self.despawn()

class Dirt_wedge(Shot):
  char = '⛏'
  def __init__(self, pos, angle, power, owner, conf):
    Shot.__init__(self, pos, angle, power, owner, conf)
    self.wedge_points = []
    self.angle = angle
    self.pos += (-3*cos(angle), 3*sin(angle))
  def update(self, win):
    h, w = win.getmaxyx()
    self.age += 1
    for i in range(2*self.age):
      angle = self.angle + radians(25 * (-1 + i/self.age))
      p = (self.pos + (cos(angle)*self.age, -sin(angle)*self.age)).clamp(0, w, 0, h-1).int()
      self.wedge_points += [p]
      self.world.destroy_ground(p.x, p.y)
    if(self.age >= 10):
      self.despawn()
  def draw(self, win):
    h, w = win.getmaxyx()
    for p in self.wedge_points:
      win.addch(p.y, p.x, '🞿')

class Leapfrog(Drill_shot):
  char = '〰'
  def __init__(self, pos, angle, power, owner, conf):
    Shot.__init__(self, pos, angle, power, owner, conf)
    self.explosions = 4
  def explode(self):
    self.speed_y *= -0.6
    self.speed_x *= 0.4
    Drill_shot.explode(self)

class Clusterbomb(Shot):
  char = 'ꙮ'
  def update(self, win):
    Shot.update(self,win)
    if(self.speed_y < 0):
     self.explode()
  def explode(self):
    for i in range(0, 360, 60):
      self.world.gameobjects += [Clusterpart(self.pos, radians(i), 0.2, self.owner, self.conf, self)]
    self.world.gameobjects += [Clusterpart(self.pos, radians(i), 0, self.owner, self.conf, self)]
    self.despawn()

class Clusterpart(Shot):
  char = 'ꙩ'
  def __init__(self, pos, angle, power, owner, conf, parent):
    Shot.__init__(self, pos, angle, power, owner, conf)
    self.speed_x += parent.speed_x
    self.speed_y += parent.speed_y
  def explode(self):
    self.world.gameobjects += [Explosion(self.pos, self.owner, 10, 3)]
    self.despawn()

class Laserbeam(Shot):
  char = '𐐡'
  def __init__(self, pos, angle, power, owner, conf):
    Shot.__init__(self, pos, angle, power, owner, conf)
    self.laser_points = []
    for i in range(100):
      newpoint = (pos + (i * cos(angle), -i*sin(angle))).int()
      if(self.world.check_collision(newpoint)):
        break
      self.laser_points += [newpoint]
      for p in self.world.players:
        if(dist(newpoint, p.pos) < 2):
          p.health = max(0, p.health - (8 - int(i/20)))

  def update(self, win):
    self.age += 1
    if(self.age >= 24):
      self.despawn()
  def draw(self, win):
    for p in self.laser_points:
      try:
        win.addch(p.y, p.x, ['█', '▓', '▒', '░', ' '][int(self.age/5)], curses.color_pair(self.owner.colors))
      except curses.error:
        pass
