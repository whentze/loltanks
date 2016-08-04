import curses
from math import sin, cos, radians

from util import clamp, dist

class Explosion():
  def __init__(self, pos, owner, damage, radius):
    self.pos    = pos
    self.age    = 1
    self.owner  = owner
    self.world  = owner.world
    self.damage = damage
    self.radius = radius
  def update(self, win):
    if(self.age >= self.radius):
      for p in self.world.players:
        d = max(dist(self.pos, p.pos) - 2, 0) 
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
        display = (self.pos + (cos(radians(theta)) * i, -sin(radians(theta)) * i)).int()
        if(display.in_box(0, w, 0, h)):
          self.world.destroy_ground(display.x, display.y)
        try:
          win.addstr(display.y, display.x, '#')
        except curses.error:
          pass   

