#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import curses
import time
import itertools
from math import pi, degrees
from random import randint, choice, uniform

from util import clamp, dist
from world import World
from tank import Tank
import configs

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
    Menuentry('explosion_radius', 'Explosion Radius', conf, range(1,11)),
    Menuentry('gravity',  'Gravity', conf, range(51)),
    Menuentry('wind_max', 'Wind', conf, range(21)),
    Menuentry('snow_max', 'Snow', conf, range(11)),
    Menuentry('world_border', 'World Border', conf, ['Void', 'Wall', 'Loop']),
    Menuentry('ground_style', 'Biome', conf, ['Block', 'Silhouette', 'Dirt', 'Candy', 'Pipes']),
  ]

  pad = curses.newpad(2*len(entries) + 3, w)

  model1 = Tank(int(w/2) - 20, 2, 'model1', curses.color_pair(0), None, conf)
  model1.angle = 0
  model2 = Tank(int(w/2) + 20, 2, 'model1', curses.color_pair(0), None, conf)
  model2.angle = pi

  while(1):
    pad.erase()
    win.erase()
    welcome = 'welcome to ' + conf['gamename'] + '!'
    win.addstr(1, int((w-len(welcome))/2), welcome)
    model1.draw(win)
    win.addstr(model1.y-1, model1.x+5, '-=●')
    model2.draw(win)
    win.addstr(model2.y-1, model2.x-7, '●=-')

    for y,entry in enumerate(entries):
      if(entry.index > 0):
        leftarrow = '< '
      else:
        leftarrow = '  '
      if(entry.index < len(entry.possible_values)-1):
        rightarrow = ' >'
      else:
        rightarrow = '  '
      if(y == pos):
        pad.addstr(y, int(w/2) - len(entry.name)-3,
          entry.name+" ~:~ "+leftarrow+str(entry.possible_values[entry.index])+rightarrow)
      else:
        pad.addstr(y, int(w/2) - len(entry.name)-3,
          entry.name+"  :  "+leftarrow+str(entry.possible_values[entry.index])+rightarrow)
    if(pos == len(entries)):
      pad.addstr(len(entries), int(w/2) - 6, '~Start Game!~')
    else:
      pad.addstr(len(entries), int(w/2) - 5, 'Start Game!')
    win.refresh()
    pad.refresh(max(pos+11 - h, 0), 0, 4, 0, h-7, w-1)

    instructions = curses.newwin(5, w - 10, h - 5, 5)
    instructions.addstr(1, int(w/2)-12, 'How to play:')
    instructions.addstr(2, int(w*0.4)-15, 'Space : Fire ')
    instructions.addstr(3, int(w*0.4)-15, ' ↑/↓  : Aim')
    instructions.addstr(2, int(w*0.6)-10,   '+/- : Set Power')
    instructions.addstr(3, int(w*0.6)-10,   '←/→ : Turn')
    instructions.box()
    instructions.refresh()

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

  if(height < 20 or width < 50):
    raise RuntimeError("This terminal is too damn small!")

  conf = configs.default_conf
  confmenu(conf, screen)

  screen.nodelay(True)
  screen.clear()
  screen.refresh()
  mainwin = curses.newwin(height-6, width, 0, 0)
  statuswin = curses.newwin(6, width, height-6, 0)

  while(1):
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
      while (not p.isdone and not len([p for p in world.players if not p.isdead]) <= 1 ):
        gamestep(screen, mainwin, statuswin, p, world, conf, n_turns)
      if (len([p for p in world.players if not p.isdead]) == 1):
        gameover(screen, [p for p in world.players if not p.isdead][0])
        break
      if (len([p for p in world.players if not p.isdead]) == 0):
        gameover(screen, None)
        break
      n_turns += 1

def gameover(screen, winner):
  height, width = screen.getmaxyx()
  screen.erase()
  if(winner == None):
    screen.addstr(int(height/2), int((width-len("Everyone died!"))/2), "Everyone died!")
  else:
    screen.addstr(int(height/2), int((width-len(winner.name + " has won!"))/2), winner.name + " has won!")
  screen.addstr(int(height/2)+2, int((width-22)/2), 'Press any key to play again!')
  screen.refresh()
  screen.nodelay(False)
  screen.getch()
  screen.nodelay(True)
  return  

def gamestep(screen, mainwin, statuswin, currentplayer, world, conf, n_turns):
  t_begin = time.clock()
  h, w = mainwin.getmaxyx()
  mainwin.erase()
  statuswin.erase()

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
  statuswin.addstr(1, stats_x, "Turn : {:d}".format(n_turns))
  if(world.wind > 0):
    windstr = ">" * world.wind
  elif(world.wind < 0):
    windstr = "<" * abs(world.wind)
  else:
    windstr = "="
  if(len(windstr) < width/(1.0+len(world.players)) - 10):
    statuswin.addstr(2, stats_x, "Wind : " + windstr)
  else:
    statuswin.addstr(2, stats_x, "Wind : " + str(abs(world.wind)) + windstr[0])

  # Main Window
  for obj in world.gameobjects:
    obj.update(mainwin)
    obj.draw(mainwin)
  try:
    key = screen.getch()
  except Error:  
    pass

  if(not currentplayer.shot_fired):
    currentplayer.processkey(key)
  else:
    mainwin.addstr(1,1,'shots fired!')

  mainwin.refresh()
  statuswin.refresh()
  t_end = time.clock()
  if(t_end < t_begin + 0.02):
    time.sleep(t_begin + 0.02 - t_end)

try:
  curses.wrapper(main)
except KeyboardInterrupt:
  exit()
except curses.error:
  print("Please don't resize the window!")
  exit()
except RuntimeError as e:
  print(str(e))
  exit()
