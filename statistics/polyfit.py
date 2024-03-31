import numpy as np
from sklearn.linear_model import LinearRegression

def polyfit(xs, ys, k):
  reg = LinearRegression()
  list2d = []
  for x in xs:
      list2d.append([x**i for i in range(1, k+1)])
  f = reg.fit(list2d, ys)
  return f.coef_, f.intercept_, reg.predict(list2d)

def bic_iter_k(xs, ys, k_max):
  r = []
  for k in range(1, k_max + 1):
    coef, inter, pred = polyfit(xs, ys, k)
    r.append(bic(xs, ys, pred, 1, k))
  return r

def bic_for_index(xs, ys, ind):
  reg = LinearRegression()
  reg.fit(xs[:, ind], ys)
  pred = reg.predict(xs[:, ind])
  return bic(xs[:, ind], ys, pred, 1, len(ind))

def bic(xs, ys, pred, sigma, k):
  n = len(xs)
  a = (n / 2)*np.log(2*np.pi*(sigma**2))
  b = 1/(2*(sigma**2))*sum((ys - pred)**2)
  c = ((k + 1)/2)*np.log(n)
  return a+b+c
