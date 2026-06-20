from clases import Jugador, TORRES, UNIDADES
from combate import EstadoJuego, ejecutar_turno, verificar_fin_ronda
import tkinter as tk
from ventanas import mostrar_mapa_y_defensor

# Simular dos jugadores
j1 = Jugador("defensor", "1234")
j2 = Jugador("atacante", "1234")
estado = EstadoJuego(j1, j2)

# Verificar que el estado se creó bien
print("Dinero defensor:", estado.dinero_defensor)
print("Dinero atacante:", estado.dinero_atacante)
print("Base vida:", estado.base.vida)
print("Base posicion:", estado.base.posicion)
print("Mapa[5][5]:", estado.mapa[5][5].tipo)

from clases import Torre, Unidad, TORRES, UNIDADES

# Crear una torre básica y colocarla
datos_torre = TORRES["basica"]
torre = Torre(datos_torre["nombre"], datos_torre["costo"], datos_torre["vida"],
              datos_torre["daño"], datos_torre["alcance"], datos_torre["habilidad"],
              datos_torre["turnos_habilidad"])
torre.posicion = (5, 3)
estado.torres.append(torre)
estado.mapa[5][3] = torre

# Crear una unidad y colocarla
datos_unidad = UNIDADES["soldado"]
unidad = Unidad(datos_unidad["nombre"], datos_unidad["costo"], datos_unidad["vida"],
                datos_unidad["daño"], datos_unidad["velocidad"], datos_unidad["habilidad"],
                datos_unidad["turnos_habilidad"])
unidad.posicion = (5, 0)
estado.unidades.append(unidad)
estado.mapa[5][0] = unidad

# Ejecutar varios turnos y ver qué pasa
for i in range(5):
    ejecutar_turno(estado)
    print(f"Turno {i+1} — Unidad vida: {unidad.vida}, posicion: {unidad.posicion}, Base vida: {estado.base.vida}")
    resultado = verificar_fin_ronda(estado)
    if resultado:
        print("Ganador de ronda:", resultado)
        break

root = tk.Tk()
root.geometry("500x600")
mostrar_mapa_y_defensor(root, j1, j2, "medieval")
root.mainloop()