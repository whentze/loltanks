from math import sqrt
from collections import namedtuple

def clamp(val, low, high):
  return max(low, min(high, val))

def dist(obj_a, obj_b):
  return sqrt((obj_a.y - obj_b.y)**2 + (obj_a.x - obj_b.x)**2)

class Point(namedtuple('Point', 'x y world')):
  def clamp(self, xmin, xmax, ymin, ymax):
    return Point(clamp(self.x, xmin, xmax), clamp(self.y, ymin, ymax), self.world)
  def __add__(self, other):
    return self.world.moveby(self, other[0], other[1])
  def __neg__(self):
    return Point(-self.x, -self.y)
  def __mod__(self, other):
    return Point(self.x % other[0], self.y % other[1], self.world)
  def int(self):
    return Point(int(self.x), int(self.y), self.world)
  def in_box(self, xmin, xmax, ymin, ymax):
    return (self.x >= xmin and self.x < xmax and self.y >= ymin and self.y < ymax)
