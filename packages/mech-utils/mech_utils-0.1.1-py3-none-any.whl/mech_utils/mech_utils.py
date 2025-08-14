



def lagrange_basis_function(j, x, xs):
    function = 1
    for i in range(len(xs)):
        if j == i:
            continue

        function = function * ((x - xs[i]) / (xs[j] - xs[i]))

    return function

def interpolate( xs: list, ys: list, x):
    function = 0
    for j in range(len(xs)):
        function = function + lagrange_basis_function(j, x, xs)*ys[j]

    return function