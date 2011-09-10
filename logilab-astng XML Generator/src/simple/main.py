

class NextClass:                            # define class
    def printer(self, text):                # define method
        self.message = text                 # change instance
        print self.message                  # access instance

x = NextClass()                             # make instance

x.printer('instance call')              # call its method

print x.message                               # instance changed

NextClass.printer(x, 'class call')      # direct class call

print x.message                               # instance changed again
a,b,c = 1,2,3
if(a<b<c):
    pass
import simple.pack.module1
import simple.another_pack.module2
simple.pack.module1.another_func()
