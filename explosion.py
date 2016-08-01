import curses
from math import sin, cos, radians

from util import clamp, dist

class Explosion():
  def __init__(self, x, y, owner, damage, radius):
    self.x      = x
    self.y      = y
    self.age    = 1
    self.owner  = owner
    self.world  = owner.world
    self.damage = damage
    self.radius = radius
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
      for theta in range(0, 360, 1+int(10/(i+1))):
        display_x, display_y = self.world.moveby(self.x, self.y, 
            cos(radians(theta)) * i,
            -sin(radians(theta)) * i)
        display_x, display_y = int(display_x), int(display_y)
        if(display_x >= 0 and display_x < w and display_y >= 0 and display_y < h):
          self.world.destroy_ground(display_x, display_y)
        try:
          win.addstr(display_y, display_x, '#')
        except curses.error:
          pass   

