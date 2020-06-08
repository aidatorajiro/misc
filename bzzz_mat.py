import scipy
from scipy.integrate import quad
import random
import numpy as np

mink = 2
maxk = 20

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

k = random.randint(mink,maxk)

print("actual k = %s" % k)

coeffs = [mk_coeff() for i in range(k + 1)]

data = []
for i in range(30):
  x = random.random()*10 - 5
  s = calc_poly(coeffs, x)
  data.append([x, s + mk_offset()])

data = np.array(data)

# calculate (a_1x_1 + a_2x_2 + ...)^2 as a matrix
def square(arr):
  n = len(arr)
  mat = np.zeros((n, n))
  for i in range(n):
    for j in range(i + 1):
      if i == j:
        mat[j,i] = arr[i]**2
      else:
        mat[j,i] = arr[i]*arr[j]*2
  return mat

# calculate gaussian integral for exp(polynomial represented by given matrix)
def gaussian_integral(mat):
  n = len(mat)
  tmp = mat
  out = 1
  for i in range(n-1):
    left = tmp[0,0]
    right = tmp[0,1:]
    out *= np.sqrt(-np.pi/left)
    tmp[1:,1:] += -square(right)/(4*left)
    tmp = tmp[1:,1:]
  return np.log(out) + tmp[0,0]

import scipy.integrate

# test
# gaussian_integral(np.array([[-1,2,3],[0,-3,1],[0,0,6.]]))
# scipy.integrate.nquad(lambda x,y: np.exp(-x**2+2*x*y+3*x+-3*y**2+y+6),[[-np.inf,np.inf],[-np.inf,np.inf]])

def calculate_weight(data, k):
  m = k + 2
  mat_line = np.zeros((m, m))
  n = len(data)
  for i in range(n):
    x = data[i, 0]
    y = data[i, 1]
    arr = np.concatenate([[-(x**i) for i in range(m - 1)], [y]])
    mat_line -= square(arr)
  mat_line /= (2*offset_sigma**2)
  mat_coeff = -np.eye(m)
  mat_coeff[0:-1,-1] += 2*coeff_mu
  mat_coeff[-1,-1] -= coeff_mu**2
  return gaussian_integral(mat_coeff + mat_line)

weights = []

for current_k in range(mink, maxk + 1):
  w = calculate_weight(data, current_k)
  weights.append(w)
  print("k = %s weight: %s" % (current_k, w))

predict_k = np.array(weights).argmax() + mink

print("predict k = %s" % predict_k)