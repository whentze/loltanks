import curses
import shot

basic_conf = {
  'gamename'        : 'loltanks',
  'gravity'         : 10,
  'sky_min'         : 0.2,
  'ground_min'      : 0.2,
  'ground_steepness': 0.8,
  'world_style'     : 'Block',
  'world_border'    : 'Void',
  'players_number'  : 3,
  'players_colors'  : [curses.COLOR_RED, curses.COLOR_BLUE, curses.COLOR_GREEN, curses.COLOR_YELLOW],
  'tank_health'     : 100,
  'tank_fuel'       : 50,
  'tank_power'      : 1.5,
  'tank_arsenal'    : [[shot.Shot,       -1],
                       [shot.Heavy_shot,  2],
                       [shot.Drill_shot,  1],
                       [shot.Teleporter,  3],
                       [shot.Dirt_wedge,  5],
                       [shot.Leapfrog,    1],
                       [shot.Clusterbomb, 1]],
  'wind_max'        : 5,
  'wind_change'     : 2,
  'wind_force'      : 0.0010,
  'particles_type'  : 'Snow',
  'particles_max'   : 3.0,
  'shot_age'        : 500,
  'shot_tail'        : 7,
}

nice_conf = dict(basic_conf, **{
  'sky_min'         : 0.4,
  'ground_min'      : 0.2,
  'ground_steepness': 0.4,
  'world_style'     : 'Dirt',
  'world_border'    : 'Loop',
  'players_number'  : 2,
  'particles_type'  : 'Stars',
})
