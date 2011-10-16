# -*- coding: utf-8 -*-
def doY(a, b, *c, **d):
  if (5>a>=b>1):
    print "a>=b"
  elif (a==b):
    print "a==b"
  elif (a!=10):
    print "a!=10"
  else:
    print "else"
  if (b>a):
    print "a<b"
  else:
    if (c!=()):
      print "c not empty!"
  if (a or b or 1):
    print "true"
  vec = [1,2,3]
  tuple = [x**x for x in vec]
  ext = [1,vec,3]
  print ext[1][2]
  print ext[::]
  return "Y"

class Hello:
  str = "Hello World!"
  args = (1,2,3)
  kwargs = {"param1":"hello", "param2":"world"}
  print args[0]
  print args[:2]
  print args[0:3]
  print args[1:]
  def do(self, a, b, x=doY(b=2, a=3), y=doY("1", 2, 3, 4, kwar1="7", kwar2="8"), z=doY(1,2,*args,**kwargs)):
    return "do"
