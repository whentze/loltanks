from math import sqrt

def clamp(val, low, high):
  return max(low, min(high, val))

def dist(obj_a, obj_b):
  return sqrt((obj_a.y - obj_b.y)**2 + (obj_a.x - obj_b.x)**2)
