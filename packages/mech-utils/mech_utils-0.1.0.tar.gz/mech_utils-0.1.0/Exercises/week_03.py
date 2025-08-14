import numpy as np



xs = [1.5, 1.6, 1.8]
vs = [6.23, 7.09, 8.97]

def interp_poly(xs, vs):
    """
    returns an interpolated polynomial for lists of data points xs and ys
    xs should be the same length as vs
    """
    degree = len(xs)
    A = np.array([[x**p for p in range(degree-1, -1, -1)] for x in xs])
    Y = np.array(vs)
    var = np.linalg.solve(A, Y)
    return var

def poly(x):
    result = 0
    degree = len((interp_poly(xs, vs))-1)
    var = (interp_poly(xs, vs))
    for power, coef in enumerate(var):
        result += coef * x**(degree-power-1)
    return result




print(poly(1.7))
