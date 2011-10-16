# -*- coding: utf-8 -*-
import myModule
from sys import copyright

class VeryUsefull:
  _cop = copyright
  def PrintCopyright(self):
    print self._cop
    print "or"
    print copyright

class Painter:
  counter = 0
  def DrawFigure(self, fig):
    fig.Draw()
    self.counter += 1
  def ViewCounter(self):
    print self.counter

List = []
f = myModule.Figure()
c = myModule.Circle()
from myModule import Rectangle as rec
a = ['spam1', 'spam2', 'spam3', 'spam4']
a1, a2, a3, a4 = a
r = rec()
f.x, f.y, f.color  = 1, 5, "yellow"
c.x, c.y, c.radius, c.color = 6, 78, 10, "black"
r.x, r.y, r.a, r.b = 1, 2, 3, 4
List.append(f)
List.append(c)
List.append(r)
myPainter = Painter()
for x in List:
  myPainter.DrawFigure(x)
t = VeryUsefull()
t.PrintCopyright()
c.Center()
c.Draw()
myPainter.ViewCounter()