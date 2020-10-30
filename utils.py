from gurobipy import *

def ultimo_y(t, y, i, l):
    for ti in range(t, -1, -1):
        if y[i, l, ti].x == 1:
            return ti