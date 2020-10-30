with open("drones.csv") as file:
    file.readline()
    drs = file.readlines()

drones = {}

for dr in drs:
    d = dr.strip("\n").split(",")
    drones[int(d[0])] = {"CC": int(d[1]), "CU": int(
        d[2]), "D": int(d[3]), "g": int(d[4])}

with open("laboratorios.csv") as file:
    file.readline()
    lbs = file.readlines()

laboratorios = {}

for lb in lbs:
    l = lb.strip("\n").split(",")
    laboratorios[int(l[0])] = {}

with open("testeo.csv") as file:
    file.readline()
    tst = file.readlines()

centros_de_testeo = {}

for ct in tst:
    c = ct.strip("\n").split(",")
    centros_de_testeo[int(c[0])] = {"E": int(c[1])}

with open("viajes.csv") as file:
    file.readline()
    vjs = file.readlines()

viajes = {}

for vj in vjs:
    v = vj.strip("\n").split(",")
    if int(v[0]) not in viajes.keys():
        viajes[int(v[0])] = {int(v[1]): int(v[2])}
    else:
        viajes[int(v[0])][int(v[1])] = int(v[2])

# Función auxiliar, retorna el viaje más corto hacia un laboratorio l (y por ende el más conveniente)


def shortest_trip(k):
    shortest = -1
    for i in laboratorios:
        if shortest <= viajes[k][i] or shortest == -1:
            shortest = viajes[k][i]
    return shortest
