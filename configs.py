import curses

default_conf = {
  'gamename'        : 'loltanks',
  'gravity'         : 10,
  'sky_min'         : 7,
  'ground_min'      : 3,
  'ground_style'    : 'Block',
  'world_border'    : 'Void',
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
  'shot_age'        : 500,
  'shot_tail'        : 7,
}
