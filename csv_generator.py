from random import randint
import parametros as p
import math

rango_tiempo_demora = [1, 4] # medido en periodos de tiempo
tiempo_que_demora = []
# origen, destino, dron, tiempo
#for i in range(p.DRONES):
for j in range(p.LABORATORIOS):
    for k in range(p.CENTROS_TESTEO):
        list_aux = []
        list_aux.append(str(k))
        list_aux.append(str(j))
        #list_aux.append(str(i))
        list_aux.append(str(randint(rango_tiempo_demora[0], rango_tiempo_demora[1])))
        tiempo_que_demora.append(list_aux)

# ta listo ekipo
with open("viajes.csv", "w", encoding = "utf-8") as file:
    file.write("origen,destino,tiempo\n")
    for cosilla in tiempo_que_demora:
        file.write(",".join(cosilla) + "\n")

# ta listo ekipo
with open("drones.csv", "w", encoding = "utf-8") as file:
    rango_costo_electrico = [20, 25] # en clp
    rango_costo_uso = [40, 70] # costo por desgaste del dron
    rango_duracion_bateria = [2, 5] # medido en periodos t
    file.write("id,costo_electrico,costo_uso,duracion_bateria,tiempo_carga\n")
    for cosilla in range(p.DRONES):
        idx = cosilla
        costo_electrico = randint(rango_costo_electrico[0], rango_costo_electrico[1])
        costo_uso = randint(rango_costo_uso[0], rango_costo_uso[1])
        duracion_bateria = randint(rango_duracion_bateria[0], rango_duracion_bateria[1])
        tiempo_carga = math.ceil(duracion_bateria/2)
        file.write(f"{idx},{costo_electrico},{costo_uso},{duracion_bateria},{tiempo_carga}\n")

with open("testeo.csv", "w", encoding = "utf-8") as file:
    #numero_centro,cantidad_entregas_posibles
    rango_entrega_tests = [20, 30]
    file.write("numero_centro,cantidad_entregas_posibles\n")
    #https://noticias.udec.cl/centro-de-diagnostico-universitario-proyecta-hasta-150-test-diarios-de-covid-19/
    for i in range(p.CENTROS_TESTEO):
        file.write(f"{i}, {randint(rango_entrega_tests[0], rango_entrega_tests[1])}\n")

with open("laboratorios.csv", "w", encoding = "utf-8") as file:
    file.write("laboratorio\n")
    for i in range(p.LABORATORIOS):
        file.write(f"{i}\n")