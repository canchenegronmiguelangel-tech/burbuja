"""
Ejercicio 1: Ordenamiento Burbuja
Problema: Ordenar las calificaciones de un grupo de alumnos de mayor a menor
para mostrar el ranking del grupo.
"""


def burbuja_descendente(lista):
    n = len(lista)
    for i in range(n - 1):
        intercambio = False
        for j in range(n - 1 - i):
            # Compara elementos vecinos y los intercambia si están en mal orden
            if lista[j][1] < lista[j + 1][1]:
                lista[j], lista[j + 1] = lista[j + 1], lista[j]
                intercambio = True
        # Si no hubo intercambios, la lista ya está ordenada
        if not intercambio:
            break
    return lista


if __name__ == "__main__":
    alumnos = [
        ("Ana", 85),
        ("Luis", 92),
        ("María", 78),
        ("Carlos", 95),
        ("Sofía", 88),
        ("Pedro", 70),
    ]

    print("Calificaciones originales:")
    for nombre, cal in alumnos:
        print(f"  {nombre}: {cal}")

    burbuja_descendente(alumnos)

    print("\nRanking (de mayor a menor):")
    for posicion, (nombre, cal) in enumerate(alumnos, start=1):
        print(f"  {posicion}. {nombre}: {cal}")