def eqn_function(x):
    return -(x ** 4) - (3 * (x ** 3)) - (12 * (x ** 2)) - (44 * x) - 48


factors = []
x = 0
y = 0

while len(factors) != 2:
    val = eqn_function(x)
    val_2 = eqn_function(y)
    if val == 0 :
        factors.append(x)
    elif val_2 == 0:
        factors.append(y)
    x += 1
    y -= 1

print(factors)