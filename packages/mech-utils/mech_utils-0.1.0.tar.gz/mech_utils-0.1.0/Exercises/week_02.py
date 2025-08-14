import math
import matplotlib.pyplot as plt
import numpy as np

#document parameters

Ts = [100.0, 200.0, 300.0, 500.0, 700.0, 900.0]
A = 1.610037
B = 0.85754
C = -12.3355 * 10 ** -4
D = 140.3813

def thermal_conductivity(T):
    return A*T**B*math.exp(C*T)*math.exp(D/T)

def therm_conductivity_range(Ts: list):
    ks = []
    for T in Ts:
        ks.append(thermal_conductivity(T))
    return ks

def lagrange_basis_function(x, j, xs):
    function = 1
    for i in range(len(xs)):
        if j == i:
            continue

        function = function * ((x - xs[i]) / (xs[j] - xs[i]))

    return function

def interpolate(x, xs, ys):
    function = 0
    for j in range(len(xs)):
        function = function + lagrange_basis_function(x, j, xs)*ys[j]

    return function

def plot_thermal_conductivity():
    temps = np.linspace(100, 900, 100)
    real_conductivity = []
    interp_conductivity = []
    for T in temps:
        real_conductivity.append(thermal_conductivity(T))

    for T in temps:
        interp_conductivity.append(interpolate(T, Ts, therm_conductivity_range(Ts)))

    plt.plot(temps, real_conductivity, color = 'r',label='real conductivity')
    plt.plot(temps, interp_conductivity, color='b', label='interpolated conductivity')
    plt.xlabel('Temperature')
    plt.ylabel('Thermal Conductivity')
    plt.grid(True)
    plt.legend()
    plt.show()


