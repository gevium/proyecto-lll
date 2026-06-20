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
    if contenido_celda is not None and contenido_celda.tipo == "muro":
        return None
    return (nueva_fila, nueva_col)
        
    contenido_celda = mapa[nueva_fila][nueva_col] #se determina que contenido (elemento) hay en la celda
    
    #Si no está vacío o hay un muro
    if contenido_celda is not None and contenido_celda.tipo == "muro":
        return None  #se queda bloqueada, no puede moverse
    return (nueva_fila, nueva_col) #retorna la nueva/proxima posicion

#funcion que permite ejecutar las habilidades de las entidades
def ejecutar_turno(estado):

    for unidad in estado.unidades: #se buscan las unidades actuales de la ronda
        if unidad.esta_destruido():
            continue  #si ya fue destruida solo se ignora, la limpieza se hace en las torres
        
        for _ in range(unidad.velocidad): #el for se repite n cantidad de veces (n = velocidad)
            nueva_pos = calcular_movimiento(unidad, estado.mapa)
            if nueva_pos is None:
                fila, columna = unidad.posicion
                #calcula la direccion del obstaculo igual que calcular_movimiento
                if columna != 5:
                    fila_frente = fila
                    col_frente = columna + 1 if columna < 5 else columna - 1
                else:
                    col_frente = columna
                    fila_frente = fila + 1 if fila < 5 else fila - 1

                if 0 <= col_frente <= 10 and 0 <= fila_frente <= 10:
                    objetivo = estado.mapa[fila_frente][col_frente]
                    if objetivo is not None and objetivo.tipo in ("muro", "torre"):
                        objetivo.recibir_daño(unidad.daño)
                        if objetivo.esta_destruido():
                            estado.mapa[fila_frente][col_frente] = None
                            if objetivo.tipo == "muro" and objetivo in estado.muros:
                                estado.muros.remove(objetivo)
                            elif objetivo.tipo == "torre" and objetivo in estado.torres:
                                estado.torres.remove(objetivo)
                break
            
            celda_destino = estado.mapa[nueva_pos[0]][nueva_pos[1]]

            if nueva_pos == (5, 5):
                # llegó a la base, la ataca sin pisarla
                estado.base.recibir_daño(unidad.daño)
                estado.dinero_atacante += 5
                break

            # si la celda tiene algo que no es la base ni está vacía, detenerse
            if celda_destino is not None:
                if celda_destino.tipo in ("muro", "torre"):
                    celda_destino.recibir_daño(unidad.daño)
                    if celda_destino.esta_destruido():
                        estado.mapa[nueva_pos[0]][nueva_pos[1]] = None
                        if celda_destino.tipo == "muro" and celda_destino in estado.muros:
                            estado.muros.remove(celda_destino)
                        elif celda_destino.tipo == "torre" and celda_destino in estado.torres:
                            estado.torres.remove(celda_destino)
                break


            # moverse normalmente
            estado.mapa[unidad.posicion[0]][unidad.posicion[1]] = None
            unidad.posicion = nueva_pos
            estado.mapa[nueva_pos[0]][nueva_pos[1]] = unidad

    # torres disparan
    for torre in estado.torres:
        if torre.esta_destruido():
            continue

        objetivo = None
        for unidad in estado.unidades:
            if not unidad.esta_destruido() and unidad.posicion is not None and torre.en_rango(unidad.posicion[0], unidad.posicion[1]):
                objetivo = unidad
                break

        if objetivo is not None:
            objetivo.recibir_daño(torre.daño)
            estado.dinero_defensor += 3

            if objetivo.esta_destruido():
                estado.mapa[objetivo.posicion[0]][objetivo.posicion[1]] = None
                objetivo.posicion = None  # <- aqui va esto
                estado.unidades.remove(objetivo)
                estado.dinero_defensor += 10

            torre.turnos_restantes -= 1
            if torre.turnos_restantes <= 0:
                torre.activar_habilidad(estado, objetivo)
    
def verificar_fin_ronda(estado):
    # el atacante gana si la base llego a 0
    if estado.base.esta_destruido():
        return "atacante"
    
    # el defensor gana si no quedan unidades vivas
    unidades_vivas = [u for u in estado.unidades if not u.esta_destruido()]
    if len(unidades_vivas) == 0:
        return "defensor"
    
    if estado.dinero_atacante <= 0 and len(estado.unidades) == 0:
        return "defensor"

    # la ronda sigue
    return None


def preparar_nueva_ronda(estado):
    # limpiar unidades
    for unidad in estado.unidades:
        if unidad.posicion is not None:
            estado.mapa[unidad.posicion[0]][unidad.posicion[1]] = None
    estado.unidades = []

    # resetear vida de la base
    estado.base.vida = estado.base.vida_maxima

    # sumar dinero de ronda a ambos
    estado.dinero_defensor += DINERO_POR_RONDA
    estado.dinero_atacante += DINERO_POR_RONDA

    # avanzar ronda
    estado.ronda_actual += 1

    # limpiar torres
    for torre in estado.torres:
        if torre.posicion is not None:
            estado.mapa[torre.posicion[0]][torre.posicion[1]] = None
    estado.torres = []

    # limpiar muros
    for muro in estado.muros:
        if muro.posicion is not None:
            estado.mapa[muro.posicion[0]][muro.posicion[1]] = None
    estado.muros = []

def ejecutar_combate(estado, actualizar_ui=None):
    MAX_TURNOS = 100
    turno = 0

    while turno < MAX_TURNOS:
        turno += 1
        ejecutar_turno(estado)
        
        # actualizar la interfaz si se paso un callback
        if actualizar_ui is not None:
            actualizar_ui()
        
        # verificar si alguien gano la ronda
        ganador = verificar_fin_ronda(estado)
        
        if ganador is not None:
            if ganador == "defensor":
                estado.rondas_defensor += 1
            else:
                estado.rondas_atacante += 1
            return ganador

    # se agotaron los turnos sin ganador, gana el defensor
    estado.rondas_defensor += 1
    return "defensor"

