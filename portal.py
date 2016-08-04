class Portal():
  def __init__(self, pos, dimension, radius, colors):
    self.pos        = pos
    self.dimension  = dimension
    self.radius     = radius
    self.colors     = colors

  def draw(self, win):
    for i in range(-self.radius, self.radius + 1):
      if(self.dimension == 'x'):
        win.addch(self.pos.y, self.pos.x + i, '–', self.colors)
      else:
        win.addch(self.pos.y + i, self.pos.x, '|', self.colors)
  def update(self, win):
    pass

    
