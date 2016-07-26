#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
import time
import itertools
from math import *
from random import randint, choice, uniform

default_conf = {
  'gamename'        : 'loltanks',
  'gravity'         : 0.01,
  'sky_min'         : 10,
  'ground_min'      : 3,
  'players_number'  : 3,
  'players_colors'  : [curses.COLOR_RED, curses.COLOR_BLUE, curses.COLOR_GREEN, curses.COLOR_YELLOW],
  'tank_health'     : 100,
  'tank_power'      : 1.5,
  'wind_max'        : 5,
  'wind_change'     : 2,
  'wind_force'      : 0.0010,
  'snow_max'        : 1.0,
  'explosion_damage': 30,
  'explosion_radius': 5,
}

# Helper Functions
def dist(obj_a, obj_b):
  return sqrt((obj_a.y - obj_b.y)**2 + (obj_a.x - obj_b.x)**2)

def clamp(val, low, high):
  return max(low, min(high, val))

# Game Objects
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
        display_x = clamp(int(self.x + cos(radians(theta)) * i), 0, w)
        display_y = clamp(int(self.y - sin(radians(theta)) * i), 0, h)
        if(display_x >= 0 and display_x < w and display_y >= 0 and display_y < h):
          self.world.ground[display_x][display_y] = False
        try:
          win.addch(display_y, display_x, '#')
        except curses.error:
          pass   

class Shot():
  def __init__(self, x, y, angle, power, owner, conf):
    self.x        = x
    self.y        = y
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
      c = '●'
    display_y = clamp(int(self.y), 0, h-1)
    display_x = clamp(int(self.x), 0, w-1)
    if(self.age>3):
      try:
        win.addch(display_y, display_x, c)
      except curses.error:
        pass
  def despawn(self):
    self.world.gameobjects.remove(self)
    del(self)
  def explode(self):
    self.world.gameobjects += [Explosion(self.x, self.y, self.owner, self.conf)]
    self.despawn()
  def update(self, win):
    h, w = win.getmaxyx()
    if (self.y > h):
      self.owner.isdone = True
      self.despawn()
      return
    elif (self.world.check_collision(self.x, self.y) or self.age > 7 and min([dist(self, p) for p in self.world.players]) < 2):
      self.explode()
      return
    self.x += self.speed_x
    self.y -= self.speed_y
    self.speed_x += self.conf['wind_force']*self.world.wind
    self.speed_y -= self.conf['gravity']
    self.age += 1

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
    display_y = self.y - 2
    display_x = self.x - int(max([len(line) for line in self.pic])/2)
    # Draw Crosshair
    if (not self.isdone):
      for i in range(10):
        line_x = int(self.x + cos(self.angle) * (self.power*4.0*i))
        line_y = int(self.y - sin(self.angle) * (self.power*4.0*i))
        try:
          if(i == 9):
            win.addch(line_y, line_x, '✜', curses.color_pair(self.colors))
          else:
            win.addch(line_y, line_x, '·', curses.color_pair(self.colors))
        except curses.error:
          pass
    # Draw Tank
    for n,line in enumerate(self.pic):
      for k, char in enumerate(line):
        if(char != ' '):
          win.addch(display_y+n, display_x+k, char)
    win.addch(self.y, self.x, self.name[-1], curses.color_pair(self.colors))

  def update(self, win):
    if(self.health <= 0):
      self.isdead = True
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
    elif(self.angle <= pi*0.75):
      self.pic =[
      ''' \\\\__ ''',
      ''' /lol\\''',
      ''' OOOOO''']
    else:
      self.pic =[
      '''  ___ ''',
      '''=/lol\\''',
      ''' OOOOO''']
    if(all([not self.world.check_collision(xi, self.y+1) for xi in range(self.x-2, self.x+3)])):
      self.y += 1
  
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

class World():
  def __init__(self, win, conf):
    h, w = win.getmaxyx()
    ground = [[False]*h for x in range(w)]
    levels = [randint(conf['sky_min'], h - conf['ground_min'])]
    for x in range(1, w):
      levels += [clamp(levels[-1] + choice([0,0,-1,1]), 4, h-1)]
    
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
    self.snowflakes   = [[uniform(0,w-1),uniform(0,h-1),uniform(1,20)] for i in range(self.snow)]
    self.ground       = ground
    self.conf         = conf
    self.players      = players
    self.gameobjects  = gameobjects
  
  def update(self, win):
    h, w = win.getmaxyx()
    for flake in self.snowflakes:
      flake[0] += self.wind * self.conf['wind_force'] * flake[2]
      flake[1] += self.conf['gravity'] * flake[2] * 0.5
  
  def draw(self, win):
    # Draw Snow
    h, w = win.getmaxyx()
    for flake in self.snowflakes:
      try:
        if(flake[2] > 15):
          win.addch(int(flake[1]), int(flake[0]), '∗')
        else:
          win.addch(int(flake[1]), int(flake[0]), '·')
      except curses.error:
        flake[0] = flake[0]%w
        flake[1] = flake[1]%h
    # Draw Ground
    for x, col in enumerate(self.ground):
      for y, cell in enumerate(col):
        if(cell):
          try:
            win.addch(y, x, '█')
          except curses.error:
            pass
  
  def check_collision(self, x, y):
    if (y >= len(self.ground[0])):
      return True
    elif(x < 0 or x >= len(self.ground) or y < 0):
      return False
    else:
      return self.ground[int(x)][int(y)]

class Menuentry():
  def __init__(self, key, name, conf, possible_values):
    self.key              = key
    self.name             = name
    self.possible_values  = possible_values
    self.index            = possible_values.index(conf[key])

# Configuration Menu
def confmenu(conf, win):
  h,w = win.getmaxyx()
  win.clear()
  pos = 0
  entries=[
    Menuentry('players_number', 'Number of Players', conf, range(2,5)),
    Menuentry('tank_health', 'Player Health', conf, [1, 25, 50, 100, 150, 200]),
    Menuentry('explosion_damage', 'Shot Damage', conf, range(10,51,10)),
    Menuentry('explosion_radius', 'Explosion Radius', conf, range(1,10)),
    Menuentry('wind_max', 'Wind', conf, range(11)),
    Menuentry('snow_max', 'Snow', conf, range(11)),
  ]
  while(1):
    win.erase()
    for y,entry in enumerate(entries):
      if(entry.index > 0):
        leftarrow = '<'
      else:
        leftarrow = ' '
      if(entry.index < len(entry.possible_values)-1):
        rightarrow = '>'
      else:
        rightarrow = ' '
      if(y == pos):
        win.addstr(2*y+1, int(w/2) - len(entry.name)-2,
          entry.name+" ~:~ "+leftarrow+str(entry.possible_values[entry.index])+rightarrow)
      else:
        win.addstr(2*y+1, int(w/2) - len(entry.name)-2,
          entry.name+"  :  "+leftarrow+str(entry.possible_values[entry.index])+rightarrow)
    if(pos == len(entries)):
      win.addstr(2*len(entries)+1, int(w/2) - 6, '~Start Game!~')
    else:
      win.addstr(2*len(entries)+1, int(w/2) - 5, 'Start Game!')
    win.refresh()
    
    key = win.getch()
    if((pos == len(entries) and key == ord(' ')) or key == ord('\n')):
      # Save Config and start game
      for e in entries:
        conf[e.key] = e.possible_values[e.index]
      return
    elif(pos != len(entries)):
      entry = entries[pos]
      if (key == curses.KEY_LEFT):
        entry.index = max(entry.index - 1, 0)
      elif (key == curses.KEY_RIGHT):
        entry.index = min(entry.index + 1, len(entry.possible_values) - 1)
    if (key == curses.KEY_UP):
      pos = (pos - 1)%(len(entries)+1)
    elif (key == curses.KEY_DOWN):
      pos = (pos + 1)%(len(entries)+1)
      
# Main Program
def main(screen):
  screen.clear()
  screen.keypad(True)
  curses.curs_set(False)
  width = curses.COLS
  height = curses.LINES
  conf = {}
  for key in default_conf:
    conf[key] = default_conf[key]
  
  if(height < 20 or width < 60):
    print("Your terminal is too damn small!")
    exit()
  screen.addstr(int(height/2), int((width-len(conf['gamename']))/2), conf['gamename'])
  screen.addstr(int(height/2)+2, int((width-22)/2), 'press any key to play!')
  screen.refresh()
  screen.getch()
  
  confmenu(conf, screen)
  
  screen.nodelay(True)
  screen.clear()
  screen.refresh()
  mainwin = curses.newwin(height-6, width, 0, 0)
  statuswin = curses.newwin(6, width, height-6, 0)
  
  world = World(mainwin, conf)
  activeplayer = 0
  n_turns = 1
  
  for p in itertools.cycle(world.players):
    if(p.isdead):
      continue
    world.wind = randint(max(-conf['wind_max'], world.wind-conf['wind_change']),
                         min( conf['wind_max'], world.wind+conf['wind_change']))
    p.isdone = False
    p.shot_fired = False
    while (not p.isdone):
      gamestep(screen, mainwin, statuswin, p, world, conf, n_turns)
    n_turns += 1

def gamestep(screen, mainwin, statuswin, currentplayer, world, conf, n_turns):
  t_begin = time.clock()
  h, w = mainwin.getmaxyx()
  mainwin.erase()
  statuswin.erase()
  try:
    key = screen.getch()
  except Error:  
    pass
  
  if(not currentplayer.shot_fired):
    currentplayer.processkey(key)
  else:
    mainwin.addstr(1,1,'shots fired!')
  # Status Window
  statuswin.box()
  heigth, width = statuswin.getmaxyx()
  statuswin.addstr(0, int((width-len(conf['gamename'])-2)/2), ' '+conf['gamename']+' ')
  
  # Player Stats
  for i,player in enumerate(world.players):
    stats_x = 2 + int(width * i/(1+len(world.players)))
    stats_y = 1
    statuswin.addstr(stats_y  , stats_x, player.name, curses.color_pair(player.colors))
    statuswin.addstr(stats_y+1, stats_x, "HP   : {:d}".format(player.health))
    statuswin.addstr(stats_y+2, stats_x, "Angle: {:.1f}°".format(degrees(player.angle)))
    statuswin.addstr(stats_y+3, stats_x, "Power: {:.0%}".format(player.power))
  # Global Stats
  stats_x = 2 + int(width * len(world.players)/(1+len(world.players)))
  statuswin.addstr(1, stats_x, "Turn   : {:d}".format(n_turns))
  if(world.wind > 0):
    windstr = ">" * world.wind
  elif(world.wind < 0):
    windstr = "<" * abs(world.wind)
  else:
    windstr = "="
  statuswin.addstr(2, stats_x, "Wind   : " + windstr)
  # Main Window
  
  for obj in world.gameobjects:
    obj.update(mainwin)
    obj.draw(mainwin)
  mainwin.refresh()
  statuswin.refresh()
  t_end = time.clock()
  if(t_end < t_begin + 0.02):
    time.sleep(t_begin + 0.02 - t_end)

try:
  curses.wrapper(main)
except KeyboardInterrupt:
  exit()
