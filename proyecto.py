from gurobipy import *
from datos import drones, laboratorios,  centros_de_testeo, viajes
import parametros as p
from time import time 

ini = time()

h = p.DURACION_MAXIMA_MUESTRA

I_ = range(p.DRONES)
K_ = range(p.CENTROS_TESTEO)
L_ = range(p.LABORATORIOS)
T_ = range(p.PERIODOS)
D = p.DEMANDA

model = Model("Optimizadrón Entrega 2")

### Variables de decisión
x = model.addVars(I_, K_, L_, T_, vtype=GRB.BINARY, name="x")

a = model.addVars(I_, K_, T_, vtype=GRB.BINARY, name="a")

d = model.addVars(K_, T_, vtype=GRB.INTEGER, name="d")

y = model.addVars(I_, K_, T_, vtype=GRB.BINARY, name="y")


model.update()

obj = quicksum(drones[i]["CU"]*x[i,k,l,t] + drones[i]["CC"]*a[i,k,t] for i in I_ for k in K_ for l in L_ for t in T_) 


def shortest_trip(k):
    shortest = -1
    for i in viajes[k]:
        if shortest >= viajes[k][i] or shortest ==-1:
            shortest = viajes[k][i]
    return shortest


### Restricciones
# 1 Un dron no puede realizar más de una entrega al mismo tiempo
model.addConstrs((quicksum(x[i, k, l, t] for l in L_ for k in K_) <= 1 for i in I_ for t in T_), name="Entregas")

# 2 Un dron no puede hacer una entrega cuya duración sea mayor al tiempo que dura su batería 
model.addConstrs((x[i, k, l, t]*viajes[k][l] <= min(drones[i]["D"], h) for i in I_ for k in K_ for l in L_ for t in T_), name="R2")

# 3 Un dron no puede realizar una entrega mientras se está cargando

model.addConstrs((x[i, k, l, t] + a[i, k, t] <= 1 for i in I_ for k in K_ for l in L_ for t in T_ ), name="R3")

# 4 Ninguna entrega debe quedar incompleta. Si se inicia una entrega, esta debe ser terminada

model.addConstrs((x.sum(i, '*', '*', '*') >= viajes[k][l] for i in I_ for k in K_ for l in L_), name="R4")
model.addConstrs((x[i, k, l, t2] - x[i, k, l, t1] <= y[i, k, t2]) for i in I_ for t1, t2 in zip(T_, T_[1:]) for k in K_ for l in L_)

# 5 Dos drones distintos no pueden iniciar una entrega hacia el mismo laboratorioen el mismo periodo t:

model.addConstrs((y[i1, k, t] + y[i2, k, t] <= 1 for t in T_ for k in K_ for i1 in I_ for i2 in I_ if i1 != i2), name = "R5")
 
# 6 El dron se debe cargar segun las horas que usa:

model.addConstrs((quicksum(a[i, k, t] for t in T_) >= quicksum(x[i, k, l, t] for t in T_)/2 for i in I_ for k in K_ for l in L_ ), name="R6")

# 7 Si el dron está cargado completamente, este debe dejar de cargarse.

model.addConstrs((quicksum(a[i, k, t] for t in T_) <= quicksum(y[i,k,t] for t in T_)*drones[i]["g"] for i in I_ for k in K_), name = "R7")


# 8. Construcción de la variable y:

model.addConstrs((quicksum(y[i, k, tj] for t in T_ for k in K_ for tj in range(t*(shortest_trip(k)+drones[i]["g"]), (t+1)*(shortest_trip(k)+drones[i]["g"])) if (t+1)*(shortest_trip(k)+drones[i]["g"]) <= p.PERIODOS-(t+1)*(shortest_trip(k)+drones[i]["g"])) == 1 for i in I_), name="R8") # R11 nueva

# 9. Construcción de la variable d_l_t:

model.addConstrs((quicksum(y[i, k, r] for i in I_ for r in range(t)) == d[k, t] for t in T_ for k in K_), name="R9")

# 10. Se debe respetar el maximo de entregas que puede recibir un laboratorio
model.addConstrs((d[k, t] <= laboratorios[l]["E"] for k in K_ for t in T_ for l in L_), name = "R10")

# 11. El total de entregas realizadas tiene que satisfacer la demanda 
t_final = T_[-1]
model.addConstr((quicksum(d[k, t_final] for k in K_) >= D), name="R11")

# 12 Naturaleza de las variables:
model.addConstrs((d[k, t] >= 0 for k in K_ for t in T_), name="R12")


model.setObjective(obj, GRB.MINIMIZE)

model.optimize()

fin = time()

print("---------------------------------------------------------------------------")

for i in model.getVars():
    print(f"{i.varName}, {i.x}")

print("---------------------------------------------------------------------------")

print(f"Tiempo total de ejecución: {(fin - ini)} segundos")
    

