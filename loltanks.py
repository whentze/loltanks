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
import menu

# Main Program
def main(screen):
  screen.clear()
  screen.keypad(True)
  curses.curs_set(False)
  width = curses.COLS
  height = curses.LINES

  if(height < 20 or width < 50):
    raise RuntimeError("This terminal is too damn small!")

  conf = configs.nice_conf
  menu.confmenu(conf, screen)

  screen.nodelay(True)
  screen.clear()
  screen.refresh()
  mainwin = curses.newwin(height-7, width, 0, 0)
  statuswin = curses.newwin(7, width, height-7, 0)

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
    statuswin.addstr(stats_y+4, stats_x, "Fuel : {:d}L".format(player.fuel))

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
    currentplayer.processkey(key, mainwin)
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
