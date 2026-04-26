import networkx as nx
from collections import defaultdict


# Convierte "HH:MM" a minutos desde medianoche
def hora_a_minutos(hora_str):
    h, m = map(int, hora_str.split(":"))
    return h * 60 + m

# Devuelve los minutos de espera hasta que abra el metro según día y hora
def espera_hasta_apertura(dia_semana, hora_str):
    dia = dia_semana.lower()
    minutos = hora_a_minutos(hora_str)

    # horario de apertura según el día
    if dia in ("lunes", "martes", "miercoles", "miércoles", "jueves", "viernes"):
        apertura = 5 * 60      # 05:00
    elif dia in ("sabado", "sábado"):
        apertura = 6 * 60      # 06:00
    else:
        # domingo
        apertura = 7 * 60      # 07:00

    # Si la hora es antes de la apertura, hay que esperar
    if minutos < apertura:
        return apertura - minutos
    else:
        # Dentro del horario de apertura (hasta las 00:00)
        return 0

# Matriz heurística (tiempos aproximados entre estaciones)
heuristica = [
    [0,4,6,7,9,11,14,16,9,13,15,15,16,17,18,10,7,4,4,4,6,8,9,11,13,15,16,20,11,12,15,4,5,7,9],
    [4,0,2,3,5,7,10,12,6,9,11,12,13,14,15,13,10,7,6,5,5,7,7,9,10,12,13,17,8,8,12,2,4,6,9],
    [6,2,0,1,3,5,8,10,4,7,9,10,11,12,13,15,12,10,8,7,6,7,7,8,9,10,12,15,5,7,11,4,5,8,10],
    [7,3,1,0,2,4,7,9,4,5,7,8,9,11,12,17,14,11,9,8,7,7,7,7,8,9,10,13,4,5,10,5,6,8,11],
    [9,5,3,2,0,2,5,7,3,3,5,6,7,9,10,19,16,14,12,11,9,9,8,7,8,8,9,12,2,4,10,7,8,10,13],
    [11,7,5,4,2,0,3,5,4,2,4,5,7,9,10,22,19,16,14,13,12,11,10,9,8,9,9,11,3,5,11,10,11,12,15],
    [14,10,8,7,5,3,0,2,7,4,4,5,7,9,10,25,22,19,18,16,15,14,13,11,10,10,10,11,6,7,12,13,14,16,18],
    [16,12,10,9,7,5,2,0,9,6,5,6,7,9,10,27,24,21,20,18,16,15,14,12,11,10,10,10,7,9,12,15,16,17,20],
    [9,6,4,4,3,4,7,9,0,5,8,9,10,12,13,19,16,14,12,11,11,11,10,10,11,11,12,15,5,7,13,8,9,12,14],
    [13,9,7,5,3,2,4,6,5,0,2,3,4,6,8,22,19,16,14,13,11,10,9,7,6,7,7,9,2,3,9,10,10,12,14],
    [15,11,9,7,5,4,4,5,8,2,0,1,2,4,6,23,20,18,16,14,12,11,9,8,6,6,6,7,4,4,8,11,12,13,16],
    [15,12,10,8,6,5,5,6,9,3,1,0,1,3,4,24,21,18,16,15,12,11,9,7,5,4,5,6,4,4,7,12,12,13,15],
    [16,13,11,9,7,7,7,7,10,4,2,1,0,2,3,24,21,19,17,15,13,11,9,7,5,3,3,4,6,4,6,13,13,13,15],
    [17,14,12,11,9,9,9,9,12,6,4,3,2,0,1,25,22,20,18,16,14,11,10,7,5,3,2,2,7,6,5,14,14,13,16],
    [18,15,13,12,10,10,10,10,13,8,6,4,3,1,0,26,23,21,19,17,14,12,10,8,5,3,2,1,9,7,5,15,14,14,16],
    [10,13,15,17,19,22,25,27,19,22,23,24,24,25,26,0,3,6,7,9,11,14,15,18,20,22,23,27,20,20,21,12,12,12,10],
    [7,10,12,14,16,19,22,24,16,19,20,21,21,22,23,3,0,3,4,6,9,11,13,15,18,20,21,24,17,17,19,9,9,9,8],
    [4,7,10,11,14,16,19,21,14,16,18,18,19,20,21,6,3,0,2,4,7,9,11,13,16,18,19,22,15,15,17,7,7,8,8],
    [4,6,8,9,12,14,18,20,12,14,16,16,17,18,19,7,4,2,0,2,5,7,9,11,14,15,16,20,13,13,15,5,4,6,6],
    [4,5,7,8,11,13,16,18,11,13,14,15,15,16,17,9,6,4,2,0,3,5,7,9,12,13,14,18,11,11,13,3,3,4,4],
    [6,5,6,7,9,12,15,16,11,11,12,12,13,14,14,11,9,7,5,3,0,2,4,6,9,11,12,16,9,9,10,3,1,1,4],
    [8,7,7,7,9,11,14,15,11,10,11,11,11,11,12,14,11,9,7,5,2,0,2,4,7,9,10,13,8,7,8,5,3,2,5],
    [9,7,7,7,8,10,13,14,10,9,9,9,9,10,10,15,13,11,9,7,4,2,0,2,5,7,8,12,7,5,6,6,5,4,6],
    [11,9,8,7,7,9,11,12,10,7,8,7,7,7,8,18,15,13,11,9,6,4,2,0,3,4,5,9,6,4,4,8,7,6,8],
    [13,10,9,8,8,8,10,11,11,6,6,5,5,5,5,20,18,16,14,12,9,7,5,3,0,2,3,7,5,3,2,10,9,9,11],
    [15,12,10,9,8,9,10,10,11,7,6,4,3,3,3,22,20,18,15,13,11,9,7,4,2,0,1,5,6,4,3,11,11,11,13],
    [16,13,12,10,9,9,10,10,12,7,6,5,3,2,2,23,21,19,16,14,12,10,8,5,3,1,0,4,7,5,3,13,12,12,14],
    [20,17,15,13,12,11,11,10,15,9,7,6,4,2,1,27,24,22,20,18,16,13,12,9,7,5,4,0,10,8,6,16,16,15,17],
    [11,8,5,4,2,3,6,7,5,2,4,4,6,7,9,20,17,15,13,11,9,8,7,6,5,6,7,10,0,2,8,8,8,10,13],
    [12,8,7,5,4,5,7,9,7,3,4,4,4,6,7,20,17,15,13,11,9,7,5,4,3,4,5,8,2,0,5,8,8,9,11],
    [15,12,11,10,10,11,12,12,13,9,8,7,6,5,5,21,19,17,15,13,10,8,6,4,2,3,3,6,8,5,0,11,10,9,11],
    [4,2,4,5,7,10,13,15,8,10,11,12,13,14,15,12,9,7,5,3,3,5,6,8,10,11,13,16,8,8,11,0,2,4,7],
    [5,4,5,6,8,11,14,16,9,10,12,12,13,14,14,12,9,7,4,3,1,3,5,7,9,11,12,16,8,8,10,2,0,2,5],
    [7,6,8,8,10,12,16,17,12,12,13,13,13,13,14,12,9,8,6,4,1,2,4,6,9,11,12,15,10,9,9,4,2,0,3],
    [9,9,10,11,13,15,18,20,14,14,16,15,15,16,16,10,8,8,6,4,4,5,6,8,11,13,14,17,13,11,11,7,5,3,0]
]

# Lista de estaciones en el mismo orden que la matriz
estaciones = [
    "Barranca del Muerto","Mixcoac","San Antonio","San Pedro de los Pinos",
    "Tacubaya","Constituyentes","Auditorio","Polanco","Observatorio",
    "Juanacatlan","Chapultepec","Sevilla","Insurgentes","Cuauhtemoc",
    "Balderas","Universidad","Copilco","M.A. De Quevedo","Viveros",
    "Coyoacan","Zapata","Division del Norte","Eugenia","Etiopia",
    "Centro Medico","Hospital General","Niños Heroes","Juarez",
    "Patriotismo","Chilpancingo","Lazaro Cardenas","Insurgentes Sur",
    "Hospital 20 de Noviembre","Parque de los Venados","Eje Central"
]

# Accesibilidad para personas con movilidad reducida (True = accesible)
accesibilidad = {
    "Polanco": False,
    "Auditorio": False,
    "Constituyentes": True,
    "Tacubaya": True,
    "San Pedro de los Pinos": False,
    "San Antonio": False,
    "Mixcoac": False,
    "Barranca del Muerto": True,
    "Observatorio": True,
    "Juanacatlan": False,
    "Chapultepec": False,
    "Sevilla": True,
    "Insurgentes": True,
    "Cuauhtemoc": True,
    "Balderas": True,
    "Juarez": False,
    "Niños Heroes": False,
    "Hospital General": False,
    "Centro Medico": False,
    "Etiopia": False,
    "Eugenia": False,
    "Division del Norte": False,
    "Zapata": True,
    "Coyoacan": False,
    "Viveros": False,
    "M.A De Quevedo": False,
    "Copilco": True,
    "Universidad": False,
    "Insurgentes Sur": False,
    "Hospital 20 de Noviembre": True,
    "Parque de los Venados": True,
    "Eje Central": False,
    "Lazaro Cardenas": False,
    "Chilpancingo": False,
    "Patriotismo": False
}

def es_accesible(estacion):
    # Si pone una estación que no existe, asumimos no accesible
    return accesibilidad.get(estacion, False)

indice = {e: i for i, e in enumerate(estaciones)}

def idx(nombre):
    return indice[nombre]

def nombre_estacion(nodo):
    return nodo.split("_L")[0]

# Heurística A*: calcula un tiempo aproximado
def h(a, b):
    return heuristica[idx(nombre_estacion(a))][idx(nombre_estacion(b))]

# Grafo de metro
G = nx.Graph()

# Tramo dentro de la misma línea
def tramo(e1, e2, linea, t):
    G.add_edge(f"{e1}_L{linea}", f"{e2}_L{linea}", weight=t)

# Transbordo entre líneas en la misma estación
def transbordo(est, l1, l2, t):
    G.add_edge(f"{est}_L{l1}", f"{est}_L{l2}", weight=t)

# --- L7 ---
tramo("Barranca del Muerto","Mixcoac",7,4)
tramo("Mixcoac","San Antonio",7,2)
tramo("San Antonio","San Pedro de los Pinos",7,1)
tramo("San Pedro de los Pinos","Tacubaya",7,2)
tramo("Tacubaya","Constituyentes",7,2)
tramo("Constituyentes","Auditorio",7,3)
tramo("Auditorio","Polanco",7,2)

# --- L1 ---
tramo("Observatorio","Tacubaya",1,3)
tramo("Tacubaya","Juanacatlan",1,3)
tramo("Juanacatlan","Chapultepec",1,2)
tramo("Chapultepec","Sevilla",1,1)
tramo("Sevilla","Insurgentes",1,1)
tramo("Insurgentes","Cuauhtemoc",1,2)
tramo("Cuauhtemoc","Balderas",1,1)

# --- L3 ---
tramo("Universidad","Copilco",3,3)
tramo("Copilco","M.A. De Quevedo",3,3)
tramo("M.A. De Quevedo","Viveros",3,2)
tramo("Viveros","Coyoacan",3,2)
tramo("Coyoacan","Zapata",3,3)
tramo("Zapata","Division del Norte",3,2)
tramo("Division del Norte","Eugenia",3,2)
tramo("Eugenia","Etiopia",3,2)
tramo("Etiopia","Centro Medico",3,3)
tramo("Centro Medico","Hospital General",3,2)
tramo("Hospital General","Niños Heroes",3,2)
tramo("Niños Heroes","Balderas",3,2)
tramo("Balderas","Juarez",3,2)

# --- L9 ---
tramo("Tacubaya","Patriotismo",9,3)
tramo("Patriotismo","Chilpancingo",9,2)
tramo("Chilpancingo","Centro Medico",9,3)
tramo("Centro Medico","Lazaro Cardenas",9,3)

# --- L12 ---
tramo("Mixcoac","Insurgentes Sur",12,2)
tramo("Insurgentes Sur","Hospital 20 de Noviembre",12,2)
tramo("Hospital 20 de Noviembre","Zapata",12,1)
tramo("Zapata","Parque de los Venados",12,1)
tramo("Parque de los Venados","Eje Central",12,3)

# Transbordos
transbordo("Tacubaya",7,9,3)
transbordo("Tacubaya",1,9,1)
transbordo("Tacubaya",1,7,4)
transbordo("Balderas",1,3,2)
transbordo("Centro Medico",3,9,3)
transbordo("Mixcoac",7,12,3)
transbordo("Zapata",3,12,1)

# Estaciones -> nodos (sirve para evitar transbordo inicial)
nodos_est = defaultdict(list)
for nodo in G.nodes:
    nodos_est[nombre_estacion(nodo)].append(nodo)

# Esta función busca la ruta óptima entre dos estaciones usando A*.
# Tiene en cuenta:
#  - Día de la semana y hora actual (si está cerrado, suma la espera)
#  - Fines de semana: +4 min en cada tramo (menos frecuencia de trenes)
#  - Minusválidos: solo permite origen/destino accesibles
def mejor_ruta_estaciones(origen, destino, dia_semana, hora_str, minusvalido=False):
    # Si el usuario es PMR, comprobamos accesibilidad de origen y destino
    if minusvalido:
        if not es_accesible(origen) or not es_accesible(destino):
            return None, None

    dia = dia_semana.lower()
    es_fin_de_semana = dia in ("sabado", "sábado", "domingo")

    # Tiempo de espera si está cerrado
    espera = espera_hasta_apertura(dia_semana, hora_str)

    # Peso normal (sin penalización por tramo)
    def peso(u, v, datos):
        return datos.get("weight", 1)

    mejor_ruta = None
    mejor_tiempo = float("inf")

    for a in nodos_est[origen]:
        for b in nodos_est[destino]:
            try:
                ruta = nx.astar_path(G, a, b, heuristic=h, weight=peso)
                t = nx.astar_path_length(G, a, b, heuristic=h, weight=peso)
            except:
                continue

            if t < mejor_tiempo:
                mejor_tiempo = t
                mejor_ruta = ruta

    if mejor_ruta is None:
        return None, None

    # Tiempo final = trayecto + espera por metro cerrado
    tiempo_total = mejor_tiempo + espera

    # Penalización ligera de fin de semana (solo 4 minutos en total)
    if es_fin_de_semana:
        tiempo_total += 4

    return mejor_ruta, tiempo_total

# Convierte "Tacubaya_L1" → "Tacubaya"
def formatear_camino(ruta):

    return " → ".join(ruta)


# Prueba rápida
if __name__ == "__main__":
    # Ejemplo: lunes a las 08:00, usuario sin discapacidad
    r, t = mejor_ruta_estaciones("Universidad", "Polanco",
                                 dia_semana="Domingo",
                                 hora_str="08:00",
                                 minusvalido=True)

    if r is None:
        print("No se puede proponer ruta en metro (origen/destino no accesibles).")
    else:
        print(formatear_camino(r), "\nTiempo:", t, "min")
