# -*- coding: utf-8 -*-
from myPackage.data import Hello
def _MoveToTheCenter(self):
  self.x = 0
  self.y = 0

class Figure:
  x = 0
  y = 0
  color = "red"
  def Draw(self):
    print "x =", self.x, ", y =", self.y, ", color ", self.color
    color = "\a\b\v\n\r\f\t"
  
class Circle(Figure):
  radius = 0
  global _MoveToTheCenter
  Center = _MoveToTheCenter
  def Draw(self):
    print "Drawing circle at x =", self.x, ", y =", self.y, ", color", self.color

class Rectangle(Figure):
  a = 0
  b = 0
  def Draw(self):
    print "Drawing rectangle at x =", self.x, ", y =", self.y, ", color", self.color
