from matplotlib import pyplot
import numpy
import math

def a(m):
    th = math.acos((m-1)/(m+1))
    n = math.ceil((math.pi - th/2)/th)
    return (math.sin(n*th))

print("".join(["1" if a(i)>0 else "0" for i in range(1,10000)]))

pyplot.plot([a(i) for i in range(1, 1000)])
pyplot.show()

pyplot.plot(numpy.linspace(1,1000, 100000), numpy.array([a(i) for i in numpy.linspace(1,1000, 100000)]))
pyplot.show()