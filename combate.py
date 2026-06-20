from clases import Torre, Unidad, Muro, BaseCentral, DINERO_INICIAL_DEFENSOR, DINERO_INICIAL_ATACANTE, DINERO_POR_RONDA, RONDAS_PARA_GANAR

'''
########################################################################
CLASE: Estado juego
########################################################################
'''

#Guarda la posicion de todas las unidades y entidades, dinero y gestiona rondas
class EstadoJuego:
    def __init__(self, defensor, atacante):
        self.defensor = defensor
        self.atacante = atacante

        #Dinero inicial
        self.dinero_defensor = DINERO_INICIAL_DEFENSOR
        self.dinero_atacante = DINERO_INICIAL_ATACANTE

        #Valor iniciar de las rondas
        self.rondas_defensor = 0
        self.rondas_atacante = 0
        self.ronda_actual = 1 

        #Listas con las entidades correspondientes de la partida
        self.torres = []
        self.muros = []
        self.unidades = []
        self.base = BaseCentral (posicion = (5, 5))

        #Mapa
        self.mapa = [[None for _ in range(11)] for _ in range(11)]
        self.mapa[5][5] = self.base

#funcion que permite determinar la posicion a la que debe ir la unidad del atacante
#para acercarse a una linea vertical u horizontal que lo lleve a  la base
def calcular_movimiento(unidad, mapa):
    fila, col = unidad.posicion
    fila_base, col_base = 5, 5

    #si ya esta en la base, no se mueve
    if fila == fila_base and col == col_base:
        return None

    #Primero intenta moverse en columna, luego en fila
    if col != col_base:
        nueva_fila = fila
        nueva_col = col + 1 if col < col_base else col - 1
    else:
        nueva_col = col
        nueva_fila = fila + 1 if fila < fila_base else fila - 1

    contenido_celda = mapa[nueva_fila][nueva_col]

    if contenido_celda is not None and contenido_celda.tipo in ("muro", "torre"):
        return None #se "bloquea", no puede avanzar
    
    return (nueva_fila, nueva_col)

#funcion que permite ejecutar las habilidades de las entidades
def ejecutar_turno(estado):

    for unidad in estado.unidades: #se buscan las unidades actuales de la ronda
        if unidad.esta_destruido():
            continue  #si ya fue destruida solo se ignora, la limpieza se hace en las torres
        
        for _ in range(unidad.velocidad): #el for se repite n cantidad de veces (n = velocidad)
            #la velocidad representa la cantidad de bloques que se mueve

            nueva_pos = calcular_movimiento(unidad, estado.mapa)

            if nueva_pos is None: #Si es None, significa que encontró un muro 
                fila, columna = unidad.posicion

                #Se define
                if columna != 5: #Si la unidad no está alineada en columna con la base, el obstáculo está en la misma fila pero una columna adelante
                    fila_frente = fila
                    col_frente = columna + 1 if columna < 5 else columna - 1
                else:
                    col_frente = columna #Si ya está alineada en columna (columna == 5), el obstáculo está en la misma columna pero una fila adelant
                    fila_frente = fila + 1 if fila < 5 else fila - 1

                if 0 <= col_frente <= 10 and 0 <= fila_frente <= 10: #Verifica que la posición calculada no salga del mapa.

                    objetivo = estado.mapa[fila_frente][col_frente] 

                    if objetivo is not None and objetivo.tipo in ("muro", "torre"): #Si es una torre o muro, la daña
                        objetivo.recibir_daño(unidad.daño)

                        if objetivo.esta_destruido(): #Si el impacto la daña, la borra de la matriz
                            estado.mapa[fila_frente][col_frente] = None
                            if objetivo.tipo == "muro" and objetivo in estado.muros:
                                estado.muros.remove(objetivo)
                            elif objetivo.tipo == "torre" and objetivo in estado.torres:
                                estado.torres.remove(objetivo)
                break
            
            if nueva_pos == (5, 5):
                #llegó a la base, la ataca sin pisarla
                estado.base.recibir_daño(unidad.daño)
                estado.dinero_atacante += 5
                break

            #moverse normalmente
            estado.mapa[unidad.posicion[0]][unidad.posicion[1]] = None
            unidad.posicion = nueva_pos
            estado.mapa[nueva_pos[0]][nueva_pos[1]] = unidad

    #Disparo de las torres

    unidades_a_eliminar = [] #Almacenamiento temporal para evitar errores de mutación de listas

    for torre in estado.torres:
        if torre.esta_destruido(): #Si está destruida, se ignora
            continue

        objetivo = None
        #Busca el primer objetivo valido
        for unidad in estado.unidades:

            #Si la unidad aun existe (...) y está dentro del rango
            if not unidad.esta_destruido() and unidad.posicion is not None and torre.en_rango(unidad.posicion[0], unidad.posicion[1]):
                objetivo = unidad
                break
        
        #Si encuentra uno:
        if objetivo is not None: #Si si hay objetivo
            objetivo.recibir_daño(torre.daño)
            estado.dinero_defensor += 3

            #Si el disparó destruyó el objetivo
            if objetivo.esta_destruido():
                estado.mapa[objetivo.posicion[0]][objetivo.posicion[1]] = None
                objetivo.posicion = None
                if objetivo not in unidades_a_eliminar:
                    unidades_a_eliminar.append(objetivo)
                estado.dinero_defensor += 10 # Bonificación por eliminación completa

            #Actualización del estado de turno de la torre
            torre.turnos_restantes -= 1
            if torre.turnos_restantes <= 0:
                torre.activar_habilidad(estado, objetivo)

    #Limpieza de las unidades muertas de la lista principal
    for unidad_muerta in unidades_a_eliminar:
        if unidad_muerta in estado.unidades:
            estado.unidades.remove(unidad_muerta)
    

#Analiza si se cumplen las condiciones de victoria o derrota
def verificar_fin_ronda(estado):

    #el atacante gana si la base llego a 0
    if estado.base.esta_destruido():
        return "atacante"
    
    #el defensor gana si no quedan unidades vivas
    unidades_vivas = [u for u in estado.unidades if not u.esta_destruido()]
    if len(unidades_vivas) == 0:
        return "defensor"
    
    #El atacante se queda sin dinero ni unidades
    if estado.dinero_atacante <= 0 and len(estado.unidades) == 0:
        return "defensor"

    #la ronda sigue
    return None

#Se limpia todo el tablero por completo
def preparar_nueva_ronda(estado):

    #se limpian unidades
    for unidad in estado.unidades:
        if unidad.posicion is not None:
            estado.mapa[unidad.posicion[0]][unidad.posicion[1]] = None
    estado.unidades = []

    #se resetea vida de la base
    estado.base.vida = estado.base.vida_maxima

    #se suma dinero de ronda a ambos
    estado.dinero_defensor += DINERO_POR_RONDA
    estado.dinero_atacante += DINERO_POR_RONDA

    #se avanza un ronda
    estado.ronda_actual += 1

    #se limpian las torres
    for torre in estado.torres:
        if torre.posicion is not None:
            estado.mapa[torre.posicion[0]][torre.posicion[1]] = None
    estado.torres = []

    #se limpian los muros
    for muro in estado.muros:
        if muro.posicion is not None:
            estado.mapa[muro.posicion[0]][muro.posicion[1]] = None
    estado.muros = []

#Funcion que controla el bucle de rondas
def ejecutar_combate(estado, actualizar_ui=None):
    MAX_TURNOS = 100
    turno = 0

    while turno < MAX_TURNOS:
        turno += 1
        ejecutar_turno(estado)
        
        #si se llamó alguna funcion/instruccion, se actualiza el UI
        if actualizar_ui is not None:
            actualizar_ui()
        
        #verifica si alguien gano la ronda
        ganador = verificar_fin_ronda(estado)

        #Si ya hay un ganador de la ronda   
        if ganador is not None:
            if ganador == "defensor":
                estado.rondas_defensor += 1
            else:
                estado.rondas_atacante += 1
            return ganador

    #se agotaron los turnos sin ganador, gana el defensor
    estado.rondas_defensor += 1
    return "defensor"

