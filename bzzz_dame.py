import numpy as np
import random
import matplotlib.pyplot as plt
import numpy.fft
from mpmath import *

def convolve_many(arrays):
    """
    Convolve a list of 1d float arrays together, using FFTs.
    The arrays need not have the same length, but each array should
    have length at least 1.

    """
    result_length = 1 + sum((len(array) - 1) for array in arrays)
    # Copy each array into a 2d array of the appropriate shape.
    rows = numpy.zeros((len(arrays), result_length))
    for i, array in enumerate(arrays):
        rows[i, :len(array)] = array
    # Transform, take the product, and do the inverse transform
    # to get the convolution.
    fft_of_rows = numpy.fft.fft(rows)
    fft_of_convolution = fft_of_rows.prod(axis=0)
    convolution = numpy.fft.ifft(fft_of_convolution)
    # Assuming real inputs, the imaginary part of the output can
    # be ignored.
    return convolution.real

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
  return (1/sqrt(2*pi*sigma**2))*exp(-(x - mu)**2/(2*sigma**2))

coeffs = [mk_coeff() for i in range(4)]

arr = []
for i in range(30):
  x = random.random()*10 - 5
  s = calc_poly(coeffs, x)
  arr.append([x, s + mk_offset()])

arr = np.array(arr)

#plt.scatter(arr[:,0], arr[:,1])
#plt.show()

def y_dist(xs, ys, coeffs):
  out = 1
  for x, y in zip(xs, ys):
    mu = calc_poly(coeffs, x)
    out *= normal_dist(mu, offset_sigma, y)
  return out

def coeff_dist(coeffs):
  out = 1
  for c in coeffs:
    out *= normal_dist(coeff_mu, coeff_sigma, c)
  return out

def dist_quad(xs, ys):
  def func_to_integrate(*coeffs):
    return y_dist(xs, ys, coeffs)*coeff_dist(coeffs)
  quad(func_to_integrate, )
