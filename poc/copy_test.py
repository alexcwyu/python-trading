
class C1(object):
    __slots__ = "s1";

class C2(C1):
    __slots__ = "s2";

class C3(C2):
    pass

o1 = C1()
o2 = C2()
o3 = C3()

print o1.__slots__	# prints s1
print o2.__slots__	# prints s2
print o3.__slots__	# prints s2

o1.s1 = 11
o2.s1 = 21
o2.s2 = 22
o3.s1 = 31
o3.s2 = 32
o3.a = 5

import copy
p3 = copy.copy(o3)

print "p3=", p3.s1
print "p3=", p3.s2
print "p3=", p3.a