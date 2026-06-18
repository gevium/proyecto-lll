from clases import Torre, Unidad, Muro, BaseCentral, DINERO_INICIAL_DEFENSOR, DINERO_INICIAL_ATACANTE, DINERO_POR_RONDA, RONDAS_PARA_GANAR

#CLASE DE ESTADO DEL JUEGO: representa las rondas de la partida
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
    
        self.torres = []
        self.muros = []
        self.unidades = []
        self.base = BaseCentral (posicion = (5, 5))

        self.mapa = [[None for _ in range(11)] for _ in range(11)]
        self.mapa[5][5] = self.base

def calcular_movimiento(unidad, mapa):
    fila, col = unidad.posicion
    fila_base, col_base = 5, 5

    #calcula hacia donde moverse (un paso hacia la base)
    if fila < fila_base:
        nueva_fila = fila + 1
    elif fila > fila_base:
        nueva_fila = fila - 1
    else:
        nueva_fila = fila

    if col < col_base:
        nueva_col = col + 1
    elif col > col_base:
        nueva_col = col - 1
    else:
        nueva_col = col
    
    contenido_celda = mapa[nueva_fila][nueva_col]
    if contenido_celda is not None and contenido_celda.tipo == "muro":
        return None  # bloqueada, no puede moverse
    return (nueva_fila, nueva_col)

def ejecutar_turno(estado):

    for unidad in estado.unidades:
        if unidad.esta_destruido():
            continue  # solo ignorar, la limpieza se hace en las torres
        
        for _ in range(unidad.velocidad):
            nueva_pos = calcular_movimiento(unidad, estado.mapa)
            if nueva_pos is None:
                # bloqueada por muro, la unidad ataca el muro
                fila, columna = unidad.posicion
                fila_frente = fila
                col_frente = columna + 1  # el muro está adelante
                if 0 <= col_frente <= 10 and estado.mapa[fila_frente][col_frente] is not None:
                    muro = estado.mapa[fila_frente][col_frente]
                    if muro.tipo == "muro":
                        muro.recibir_daño(unidad.daño)
                        if muro.esta_destruido():
                            estado.mapa[fila_frente][col_frente] = None
                            if muro in estado.muros:
                                estado.muros.remove(muro)
                break

            celda_destino = estado.mapa[nueva_pos[0]][nueva_pos[1]]

            if nueva_pos == (5, 5):
                # llegó a la base, la ataca sin pisarla
                estado.base.recibir_daño(unidad.daño)
                estado.dinero_atacante += 5
                break

            # si la celda tiene algo que no es la base ni está vacía, detenerse
            if celda_destino is not None:
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

