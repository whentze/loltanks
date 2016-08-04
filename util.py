from math import sqrt
from collections import namedtuple

def clamp(val, low, high):
  return max(low, min(high, val))

def dist(obj_a, obj_b):
  return sqrt((obj_a.y - obj_b.y)**2 + (obj_a.x - obj_b.x)**2)

class Point(namedtuple('Point', 'x y')):
  def clamp(self, xmin, xmax, ymin, ymax):
    return Point(clamp(self.x, xmin, xmax), clamp(self.y, ymin, ymax))
  def __add__(self, other):
    return Point(self.x + other.x, self.y + other.y)
  def __neg__(self):
    return Point(-self.x, -self.y)
  def __mod__(self, other):
    return Point(self.x % other.x, self.y % other.y)
  def __int__(self):
    return Point(int(self.x), int(self.y))
