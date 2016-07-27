from math import pi, sin, cos
import curses

from util import clamp
from shot import Shot

class Tank():
  def __init__(self, x, y, name, colors, world, conf):
    self.x          = x
    self.y          = y
    self.name       = name
    self.colors     = colors
    self.world      = world
    self.conf       = conf
    self.health     = conf['tank_health']
    self.shot       = None
    self.angle      = pi/4
    self.isdead     = False
    self.shot_fired = False
    self.isdone     = True
    self.power      = 0.50
    self.pic =[
    r' ___  ',
    r'/lol\=',
    r'OOOOO ']

  def draw(self, win):
    if(self.isdead):
      self.pic =[
      '''  ___  ''',
      ''' /rip\ ''',
      ''' OOOOO ''']
    elif(self.angle < pi*0.10):
      self.pic =[
      '''  ___  ''',
      ''' /lol\=''',
      ''' OOOOO ''']
    elif(self.angle < pi*0.40):
      self.pic =[
      '''  __// ''',
      ''' /lol\ ''',
      ''' OOOOO ''']
    elif(self.angle < pi*0.5):
      self.pic =[
      '''  _||  ''',
      ''' /lol\ ''',
      ''' OOOOO ''']
    elif(self.angle < pi*0.60):
      self.pic =[
      '''  ||_ ''',
      ''' /lol\\''',
      ''' OOOOO''']
    elif(self.angle <= pi*0.90):
      self.pic =[
      ''' \\\\__ ''',
      ''' /lol\\''',
      ''' OOOOO''']
    else:
      self.pic =[
      '''  ___ ''',
      '''=/lol\\''',
      ''' OOOOO''']
    display_y = self.y - 2
    display_x = self.x - int(max([len(line) for line in self.pic])/2)
    # Draw Crosshair
    if (not self.isdone):
      for i in range(10):
        line_x = int(self.x + cos(self.angle) * (self.power*4.0*i))
        line_y = int(self.y - sin(self.angle) * (self.power*4.0*i))
        try:
          if(i == 9):
            win.addstr(line_y, line_x, '✜', curses.color_pair(self.colors))
          else:
            win.addstr(line_y, line_x, '·', curses.color_pair(self.colors))
        except curses.error:
          pass
    # Draw Tank
    for n,line in enumerate(self.pic):
      for k, char in enumerate(line):
        if(char != ' '):
          win.addstr(display_y+n, display_x+k, char)
    win.addstr(self.y, self.x, self.name[-1], curses.color_pair(self.colors))

  def update(self, win):
    if(all([not self.world.check_collision(xi, self.y+1) for xi in range(self.x-2, self.x+3)])):
      self.y += 1
    
    if(self.health <= 0):
      self.isdead = True
      self.isdone = True

  def processkey(self, key):
    if (key == ord(' ')):
      self.shoot()
      return True
    elif (key == curses.KEY_LEFT and self.angle <= pi/2):
        self.angle = pi - self.angle
    elif (key == curses.KEY_RIGHT and self.angle >= pi/2):
      self.angle = pi - self.angle
    elif (key == curses.KEY_UP):
      if (self.angle <= pi/2):
        self.angle = min(pi/2.001, self.angle+0.01)
      else:
        self.angle = max(pi/1.999, self.angle-0.01)
    elif (key == curses.KEY_DOWN):
      if (self.angle <= pi/2):
        self.angle = max(0, self.angle-0.01+pi/8)-pi/8
      else:
        self.angle = min(pi*9/8, self.angle+0.01)
    elif (key == ord('+')):
      self.power = min(1.00, self.power+0.01)
    elif (key == ord('-')):
      self.power = max(0.00, self.power-0.01)
    return False
  def shoot(self):
    shot = Shot(self.x, self.y, self.angle, self.power*self.conf['tank_power'], self, self.conf)
    self.world.gameobjects += [shot]
    self.shot_fired = True
