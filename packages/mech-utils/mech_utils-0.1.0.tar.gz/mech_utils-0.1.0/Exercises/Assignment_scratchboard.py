import math


def conductivity_t(T):
    A=1.610037
    B=0.85754
    C=-12.3355*10**-4
    D=140.3813

    return A*T**B*math.exp(C*T)*math.exp(D/T)

print(conductivity_t(100))
print(conductivity_t(200))
print(conductivity_t(300))

def conductivity_interpol(T):
    a=0.0029843358828523115
    b=-1.5150184539222656
    c=422.27421559128169
    return(a*T**2 + b*T + c)

print(conductivity_interpol(250))
print(conductivity_t(250))
print((conductivity_interpol(250)-conductivity_t(250))/conductivity_interpol(250))



