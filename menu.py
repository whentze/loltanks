from math import pi

import curses
import tank

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
    Menuentry('world_style', 'Biome', conf, ['Block', 'Silhouette', 'Dirt', 'Candy', 'Pipes']),
  ]

  pad = curses.newpad(2*len(entries) + 3, w)

  model1 = tank.Tank(int(w/2) - 20, 2, 'model1', curses.color_pair(0), None, conf)
  model1.angle = 0
  model2 = tank.Tank(int(w/2) + 20, 2, 'model1', curses.color_pair(0), None, conf)
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
