import scipy
from scipy.integrate import quad
import random
import numpy as np

coeff_mu = 0
coeff_sigma = 1

def mk_coeff():
  return random.normalvariate(coeff_mu, coeff_sigma)

offset_sigma = 1

def mk_offset():
  return random.normalvariate(0, offset_sigma)

def calc_poly(coeffs, x):
  return sum([j*x**i for i, j in enumerate(coeffs)])

def normal_dist(mu, sigma, x):
  return (1/sqrt(2*np.pi*sigma**2))*exp(-(x - mu)**2/(2*sigma**2))

coeffs = [mk_coeff() for i in range(4)]

arr = []
for i in range(30):
  x = random.random()*10 - 5
  s = calc_poly(coeffs, x)
  arr.append([x, s + mk_offset()])

arr = np.array(arr)

