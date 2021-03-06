from math import pi, sin, cos
import copy
import curses

from util import clamp, Point
from shot import Shot

tanksize = 2

class Tank():
  def __init__(self, pos, name, colors, world, conf):
    self.pos            = Point(pos[0], pos[1], world)
    self.name           = name
    self.colors         = colors
    self.world          = world
    self.conf           = conf
    self.health         = conf['tank_health']
    self.fuel           = conf['tank_fuel']
    self.arsenal        = copy.deepcopy(conf['tank_arsenal'])
    self.active_weapon  = 0
    self.weapon_display_timer = 0
    self.angle          = pi/4
    self.isdead         = False
    self.active_shots   = 0
    self.isactive       = False
    self.power          = 0.50
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
    # Draw Crosshair
    if (self.isactive):
      p = self.muzzle
      for i in range(10):
        p += (cos(self.angle) * (self.power*4.0),
              -sin(self.angle) * (self.power*4.0))
        dot = p.int()
        try:
          if(i == 9):
            win.addstr(dot.y, dot.x, '✜', curses.color_pair(self.colors))
          else:
            win.addstr(dot.y, dot.x, '·', curses.color_pair(self.colors))
        except curses.error:
          pass
    # Draw Selected Weapon
    h, w = win.getmaxyx()
    if(self.weapon_display_timer > 0):
      weapon = self.arsenal[self.active_weapon]
      weaponwin = win.derwin(3, 7, clamp(self.pos.y - 5, 0, h-3), clamp(self.pos.x - 3, 0, w-7))
      try:
        weaponwin.box()
        if(weapon[1] == -1):
          weaponwin.addstr(1, 3, weapon[0].char)
        else:
          weaponwin.addstr(1, 2, weapon[0].char + ':' + str(weapon[1]))
      except curses.error:
        pass
      weaponwin.refresh()
    # Draw Tanks
    x_off = -int(max([len(line) for line in self.pic])/2)
    y_off = -tanksize
    for n,line in enumerate(self.pic):
      for k, char in enumerate(line):
        draw = self.pos + (x_off + k, y_off + n)
        if(char != ' ' and draw.in_box(0, w, 0, h)):
          win.addstr(draw.y, draw.x, char)
    if(self.pos == self.pos.clamp(0, w-1, 0, h-1)):
      win.addstr(self.pos.y, self.pos.x, self.name[-1], curses.color_pair(self.colors))

  def update(self, win):
    self.weapon_display_timer = max(0, self.weapon_display_timer - 1)
    if(all(
        [not self.world.check_collision(self.pos+(xi,1)) for xi in
        range(-tanksize, tanksize+1)])):
      self.pos += (0, 1)

    self.muzzle = self.pos + ((1+tanksize)*cos(self.angle),
         -max(1,(tanksize)*sin(self.angle)))
    if(self.health <= 0):
      self.isdead   = True
      self.isactive = False

  def processkey(self, key, win):
    h, w = win.getmaxyx()
    if (key == ord(' ')):
      weapon = self.arsenal[self.active_weapon]
      if (weapon[1] != 0):
        self.shoot()
        if(weapon[1] != -1):
          weapon[1] = max(0, weapon[1] - 1)
        return True
      else:
        self.weapon_display_timer = 50
    elif (key == curses.KEY_LEFT):
      if self.angle <= pi/2:
        self.angle = pi - self.angle
      else:
        self.move(-1)
    elif (key == curses.KEY_RIGHT):
      if self.angle >= pi/2:
        self.angle = pi - self.angle
      else:
        self.move(1)
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
    elif (key in map(lambda k : ord(str(k)), range(10))):
      n = int(chr(key))
      self.active_weapon = (n-1) % len(self.arsenal)
      self.weapon_display_timer = 50
      
    return False
  def shoot(self):
    shot = self.arsenal[self.active_weapon][0](
                self.muzzle,
                self.angle,
                self.power*self.conf['tank_power'],
                self,
                self.conf)
    self.world.gameobjects += [shot]
    self.isactive = False
  def move(self, direction):
    if self.fuel > 0:
      if not any([self.world.check_collision(self.pos + (direction*(tanksize + 1), -i))
            for i in range(tanksize+1)]):
        self.pos += (direction, 0)
        self.fuel -= 1
      elif not any([self.world.check_collision(self.pos + (direction*(tanksize + 1), -i))
            for i in range(1, tanksize+2)]):
        self.pos += (direction, -1)
        self.fuel -= 1
