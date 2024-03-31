# goji houteishiki solver

from mpmath import mp

mp.dps = 20

K = lambda k: mp.quad(lambda x: 1/(mp.sqrt(1 - (k**2)*(mp.sin(x)**2))), [0, mp.pi/2])

latparam = lambda k: mp.j*K(mp.sqrt(1-k**2))/K(k)

J = lambda m, t: (phi5(t) + phi5m(t, 0))*(phi5m(t, 4) - phi5m(5, 1))*(phi5m(t, 3) - phi5m(t, 2))

inv_n = lambda n, t: -(1/(n + t))

phi = lambda t: 

kei = lambda R: (r*(5**(5/4)) + mp.sqrt((R**2)*mp.sqrt(5**5) - 16))/(r*(5**(5/4)) + mp.sqrt((R**2)*mp.sqrt(5**5) + 16))

