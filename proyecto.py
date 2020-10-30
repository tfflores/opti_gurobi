from gurobipy import *
from datos import drones, laboratorios,  centros_de_testeo, viajes
import parametros as p
from utils import ultimo_y

h = p.DURACION_MAXIMA_MUESTRA

I_ = range(p.DRONES)
K_ = range(p.CENTROS_TESTEO)
L_ = range(p.LABORATORIOS)
T_ = range(p.PERIODOS)

D = sum(centros_de_testeo[i]["entregas"] for i in K_)

model = Model("Optimizadrón Entrega 2")

### Variables de decisión
x = model.addVars(I_, K_, L_, T_, vtype=GRB.BINARY, name="x")

a = model.addVars(I_, K_, T_, vtype=GRB.BINARY, name="a")

d = model.addVars(L_, T_, vtype=GRB.INTEGER, name="d")

y = model.addVars(I_, L_, T_, vtype=GRB.BINARY, name="y")

b = model.addVars(I_, T_, vtype=GRB.INTEGER, name="b")

z = model.addVars(I_, K_, T_, vtype=GRB.BINARY, name="z")

model.update()

obj = quicksum(drones[i]["CU"]*x[i,k,l,t] + drones[i]["CC"]*a[i,k,t] for i in I_ for k in K_ for l in L_ for t in T_) 


def shortest_trip(l):
    shortest = -1
    for i in viajes:
        if shortest <= viajes[i][l]:
            shortest = viajes[i][l]
    return shortest


### Restricciones
# 1 Un dron no puede realizar más de una entrega al mismo tiempo
model.addConstrs((quicksum(x[i, k, l, t] for l in L_ for k in K_) <= 1 for i in I_ for t in T_), name="Entregas")

# 2 Un dron no puede hacer una entrega cuya duración sea mayor al tiempo que dura su batería 
model.addConstrs((x[i, k, l, t]*viajes[k][l] <= drones[i]["D"] for i in I_ for k in K_ for l in L_ for t in T_), name="R2")

# 4 Un dron no puede realizar una entrega mientras se está cargando

model.addConstrs((x[i, k, l, t] + a[i, k, t] <= 1 for i in I_ for k in K_ for l in L_ for t in T_ ), name="R4")

# 5 Ninguna entrega debe quedar incompleta. Si se inicia una entrega, esta debe ser terminada
    ## PENDIENTE: tiempos del conjunto M custom

#model.addConstrs((quicksum(x[i,k,l,tj] for k in K_ for l in L_ for t in T_ for tj in range(t, t+viajes[k][l]+drones[i]["g"]) if t+viajes[k][l]+drones[i]["g"] <= p.PERIODOS) >= viajes[kj][lj] for i in I_ for kj in K_ for lj in L_), name="R5")


#model.addConstrs((quicksum(x[i,k,l,tj] for k in K_ for l in L_ for t in T_ for tj in range(t, t+viajes[k][l]) if t+viajes[k][l] < 72) >= viajes[kj][lj]*y[i, lj, t] for i in I_ for kj in K_ for lj in L_ for t in T_), name="R5")

#6 Dos drones distintos no pueden iniciar una entrega hacia el mismo laboratorioen el mismo periodo t:

model.addConstrs((y[i1, l, t] + y[i2, l, t] <= 1 for t in T_ for l in L_ for i1 in I_ for i2 in I_ if i1 != i2), name = "R6")

# 7 Construcción de variable b_i_t:

model.addConstrs((x[i, k, l, t] * (drones[i]["D"] - y[i, l, t0] * quicksum(x[i, k, l, tj] for tj in range(t0, t + 1))) 

+ a[i, k, t] * (drones[i]["D"] - y[i, l, t0] * quicksum(x[i, k, l, tj] for tj in range(t0, t0 + viajes[k][l])) + 2 * z[i, k, t0 + viajes[k][l]] * quicksum(a[i, k, tj] for tj in range(t0 + viajes[k][l], t))) 

+ drones[i]["D"] * (1 - x[i, k, l, t] - a[i, k, t]) == b[i, t] for i in I_ for k in K_ for l in L_ for t in T_), name = "R7")

# 8 El dron debe cargarse por completo:
    ## PENDIENTE: tiempos del conjunto M custom
model.addConstrs((quicksum(a[i, k, t] for t in T_) >= drones[i]["g"] for i in I_ for k in K_), name="R8")

# 9 Si el dron está cargado completamente, este debe dejar de cargarse.

#model.addConstrs((drones[i]["D"] - b[i,t] >= a[i, k, t] for i in I_ for k in K_ for t in T_), name = "R9")

# 10. Construcción de la variable z:
#model.addConstrs((z[i, k, t] == y[i, l, t-viajes[k][l]] * x[i, k, l, t-viajes[k][l]] for i in I_ for k in K_ for l in L_ for t in T_ if t-viajes[k][l] > 0), name = "R10")

# 11. Construcción de la variable y:

#model.addConstrs((x[i, k, l, 0] == y[i, l ,0] for i in I_ for k in K_ for l in L_ for t in T_), name = "R11a")
#model.addConstrs((x[i, k, l, t] - x[i, k, l, t - 1] <= y[i, l ,t]  for i in I_ for k in K_ for l in L_ for t in T_ if t > 0),name = "R11b")
model.addConstrs((quicksum(y[i, l, tj] for t in T_ for l in L_ for tj in range(t*(shortest_trip(l)+drones[i]["g"]), (t+1)*(shortest_trip(l)+drones[i]["g"])) if (t+1)*(shortest_trip(l)+drones[i]["g"]) <= p.PERIODOS-(t+1)*(shortest_trip(l)+drones[i]["g"])) == 1 for i in I_), name="R11") # R11 nueva
#for tj in range(t, t+viajes[k][l]+drones[i]["g"]) if t+viajes[k][l]+drones[i]["g"]<=p.PERIODOS
# 12. Construcción de la variable d_l_t:
model.addConstrs((quicksum(y[i, l, r] for i in I_ for r in range(t)) == d[l, t] for t in T_ for l in L_), name="R12")

# 13. Se debe respetar el maximo de entregas que puede recibir un laboratorio
model.addConstrs((d[l, t] <= laboratorios[l]["E"] for l in L_ for t in T_), name = "R13")

# 14. El total de entregas realizadas tiene que satisfacer la demanda 
t_final = T_[-1]
model.addConstr((quicksum(d[l, t_final] for l in L_) >= 40+35+32), name="R14")

# 15 Naturaleza de las variables:
model.addConstrs((d[l, t] >= 0 for l in L_ for t in T_), name="R15a")
model.addConstrs((b[i, t] >= 0 for i in I_ for t in T_), name="R15b")



# sum for range(t, t + viajes[k][j] + ) y[i, l, t] == 1



model.setObjective(obj, GRB.MINIMIZE)

#model.computeIIS() 

model.optimize()
for v in model.getVars():
    if "a" in v.varName and v.x == 1:
        print('%s %g' % (v.varName, v.x))