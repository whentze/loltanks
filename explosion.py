import curses
from math import sin, cos, radians

from util import clamp, dist

class Explosion():
  def __init__(self, x, y, owner, conf):
    self.x      = x
    self.y      = y
    self.age    = 0
    self.owner  = owner
    self.world  = owner.world
    self.conf   = conf
    self.damage = conf['explosion_damage']
    self.radius = conf['explosion_radius']
  def update(self, win):
    if(self.age >= self.radius):
      for p in self.world.players:
        d = max(dist(self, p) - 2, 0) 
        if (d < self.radius):
         damage = self.damage * (self.radius - d)/self.radius
         p.health = max(0, int(p.health - damage))
      self.world.gameobjects.remove(self)
      self.owner.isdone = True
      del(self)
      return
    else:
      self.age += 1

  def draw(self, win):
    h, w = win.getmaxyx()
    for i in range(self.age):
      for theta in range(0, 360, 4):
        if(self.conf['world_border'] == 'Loop'):
          display_x = int(self.x + cos(radians(theta)) * i) % w
        else:
          display_x = clamp(int(self.x + cos(radians(theta)) * i), 0, w)
        display_y = clamp(int(self.y - sin(radians(theta)) * i), 0, h)
        if(display_x >= 0 and display_x < w and display_y >= 0 and display_y < h):
          self.world.destroy_ground(display_x, display_y)
        try:
          win.addstr(display_y, display_x, '#')
        except curses.error:
          pass   

