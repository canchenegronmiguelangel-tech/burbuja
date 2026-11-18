"""
Ejercicio 1 - Ordenamiento Burbuja: ranking de calificaciones
Ordena de MAYOR a MENOR las calificaciones de un grupo de alumnos con el método de la burbuja.

Cómo usarlo:
  1. Captura manualmente los datos (Alumno y Calificación (0-100)) y pulsa "Agregar"
     (o usa "Cargar ejemplo").
  2. Pulsa "Paso a paso" para avanzar una comparación a la vez, o "Automático".
  3. Pulsa "Reiniciar" para volver a la lista original.

Ejecutar:  python 1_burbuja_calificaciones.py
"""
import tkinter as tk
from tkinter import messagebox

ETIQ_NOMBRE = "Alumno"
ETIQ_VALOR = "Calificación (0-100)"
EJEMPLO = [("Ana", 85), ("Luis", 92), ("María", 78), ("Carlos", 95), ("Sofía", 88), ("Pedro", 70)]
convertir = int
VALOR_MIN, VALOR_MAX = 0, 100
formato = str

ANCHO, ALTO = 780, 330
AZUL, AMARILLO, ROJO, VERDE, MORADO = "#5b9bd5", "#ffd966", "#e06666", "#93c47d", "#b48ad6"


# ---------------------------------------------------------------------------
# ALGORITMO: es un generador. Cada 'yield' es un paso que la interfaz dibuja.
# ---------------------------------------------------------------------------
def algoritmo(datos):
    """Burbuja: compara vecinos y los intercambia si están en mal orden (mayor -> menor)."""
    n = len(datos)
    ordenados = set()
    for i in range(n - 1):
        hubo_cambio = False
        for j in range(n - 1 - i):
            a, b = datos[j], datos[j + 1]
            yield dict(tipo="comparar", comp=(j, j + 1), ordenados=ordenados,
                       msg=f"Comparo {a[0]} ({formato(a[1])}) con {b[0]} ({formato(b[1])}).")
            if a[1] < b[1]:
                datos[j], datos[j + 1] = b, a
                hubo_cambio = True
                yield dict(tipo="intercambio", comp=(j, j + 1), ordenados=ordenados,
                           msg=f"{a[1]} < {b[1]}: intercambio posiciones {j} y {j + 1}.")
        ordenados.add(n - 1 - i)   # el menor de la pasada "flota" hasta el final
        if not hubo_cambio:
            break                  # ya no hubo cambios: la lista está ordenada
    yield dict(tipo="fin", ordenados=set(range(n)), msg="¡Lista ordenada de mayor a menor!")


# ---------------------------------------------------------------------------
# INTERFAZ GRÁFICA
# ---------------------------------------------------------------------------
class App:
    MAX_ELEMENTOS = 12

    def __init__(self, root):
        self.root = root
        root.title("Ejercicio 1 - Ordenamiento Burbuja: ranking de calificaciones")
        self.datos = []
        self.original = []
        self.gen = None
        self.estado = "listo"          # listo | ordenando | terminado
        self.auto_activo = False
        self.comparaciones = 0
        self.movimientos = 0
        self.num_paso = 0
        self.construir_interfaz()
        self.dibujar()

    # ----- construcción de la ventana -----
    def construir_interfaz(self):
        entrada = tk.Frame(self.root, padx=10, pady=8)
        entrada.pack(fill="x")
        tk.Label(entrada, text=ETIQ_NOMBRE + ":").pack(side="left")
        self.e_nombre = tk.Entry(entrada, width=18)
        self.e_nombre.pack(side="left", padx=(4, 12))
        tk.Label(entrada, text=ETIQ_VALOR + ":").pack(side="left")
        self.e_valor = tk.Entry(entrada, width=10)
        self.e_valor.pack(side="left", padx=(4, 12))
        tk.Button(entrada, text="Agregar", command=self.agregar).pack(side="left", padx=2)
        tk.Button(entrada, text="Cargar ejemplo", command=self.cargar_ejemplo).pack(side="left", padx=2)
        tk.Button(entrada, text="Borrar todo", command=self.borrar_todo).pack(side="left", padx=2)
        self.e_nombre.bind("<Return>", lambda e: self.e_valor.focus())
        self.e_valor.bind("<Return>", lambda e: self.agregar())

        self.canvas = tk.Canvas(self.root, width=ANCHO, height=ALTO, bg="white",
                                highlightthickness=1, highlightbackground="#bbbbbb")
        self.canvas.pack(padx=10)

        ley = tk.Frame(self.root)
        ley.pack(pady=(4, 0))
        for color, texto in [(AZUL, "Sin ordenar"), (AMARILLO, "Comparando"), (ROJO, "Intercambio"),
                             (MORADO, "Mínimo actual"), (VERDE, "Ordenado")]:
            tk.Label(ley, bg=color, width=2).pack(side="left", padx=(10, 2))
            tk.Label(ley, text=texto).pack(side="left")

        ctrl = tk.Frame(self.root, padx=10, pady=8)
        ctrl.pack(fill="x")
        tk.Button(ctrl, text="Paso a paso", width=12, command=self.paso).pack(side="left", padx=2)
        self.btn_auto = tk.Button(ctrl, text="Automático", width=12, command=self.alternar_auto)
        self.btn_auto.pack(side="left", padx=2)
        tk.Button(ctrl, text="Reiniciar", width=12, command=self.reiniciar).pack(side="left", padx=2)
        tk.Label(ctrl, text="   Pausa entre pasos (ms):").pack(side="left")
        self.vel = tk.Scale(ctrl, from_=100, to=1500, orient="horizontal", length=160)
        self.vel.set(500)
        self.vel.pack(side="left")
        self.lbl_estado = tk.Label(ctrl, text="", font=("Arial", 10, "bold"))
        self.lbl_estado.pack(side="right")

        marco_log = tk.Frame(self.root, padx=10)
        marco_log.pack(fill="both", expand=True, pady=(0, 10))
        scroll = tk.Scrollbar(marco_log)
        scroll.pack(side="right", fill="y")
        self.log = tk.Text(marco_log, height=8, state="disabled", yscrollcommand=scroll.set,
                           font=("Consolas", 10))
        self.log.pack(side="left", fill="both", expand=True)
        scroll.config(command=self.log.yview)
        self.actualizar_estado()

    # ----- captura manual de datos -----
    def bloqueado(self):
        if self.estado != "listo":
            messagebox.showinfo("Aviso", "Pulsa 'Reiniciar' antes de modificar la lista.")
            return True
        return False

    def agregar(self):
        if self.bloqueado():
            return
        nombre = self.e_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Dato faltante", f"Escribe: {ETIQ_NOMBRE}.")
            return
        try:
            valor = convertir(self.e_valor.get().strip())
        except ValueError:
            messagebox.showwarning("Dato inválido", f"'{ETIQ_VALOR}' debe ser un número.")
            return
        if not (VALOR_MIN <= valor <= VALOR_MAX):
            messagebox.showwarning("Fuera de rango",
                                   f"'{ETIQ_VALOR}' debe estar entre {VALOR_MIN} y {VALOR_MAX}.")
            return
        if len(self.datos) >= self.MAX_ELEMENTOS:
            messagebox.showwarning("Límite", f"Máximo {self.MAX_ELEMENTOS} elementos.")
            return
        self.datos.append((nombre, valor))
        self.e_nombre.delete(0, "end")
        self.e_valor.delete(0, "end")
        self.e_nombre.focus()
        self.dibujar()
        self.actualizar_estado()

    def cargar_ejemplo(self):
        if self.bloqueado():
            return
        self.datos = list(EJEMPLO)
        self.dibujar()
        self.actualizar_estado()

    def borrar_todo(self):
        self.detener_auto()
        self.datos = []
        self.original = []
        self.gen = None
        self.estado = "listo"
        self.limpiar_log()
        self.dibujar()
        self.actualizar_estado()

    # ----- control de la ejecución -----
    def paso(self):
        """Ejecuta UN paso del algoritmo. Devuelve True si quedan más pasos."""
        if self.estado == "terminado":
            messagebox.showinfo("Aviso", "La lista ya está ordenada. Pulsa 'Reiniciar'.")
            return False
        if self.estado == "listo":
            if len(self.datos) < 2:
                messagebox.showinfo("Aviso", "Agrega al menos 2 elementos.")
                return False
            self.original = list(self.datos)
            self.gen = algoritmo(self.datos)       # ordena self.datos "en vivo"
            self.estado = "ordenando"
            self.comparaciones = self.movimientos = self.num_paso = 0
            self.limpiar_log()
        try:
            info = next(self.gen)
        except StopIteration:
            info = {"tipo": "fin", "ordenados": set(range(len(self.datos))), "msg": "Listo."}
        self.num_paso += 1
        if info["tipo"] == "comparar":
            self.comparaciones += 1
        elif info["tipo"] == "intercambio":
            self.movimientos += 1
        self.dibujar(info)
        self.escribir(f"Paso {self.num_paso}: {info['msg']}")
        self.actualizar_estado()
        if info["tipo"] == "fin":
            self.estado = "terminado"
            self.detener_auto()
            self.escribir(f"Total: {self.comparaciones} comparaciones y {self.movimientos} intercambios.")
            return False
        return True

    def alternar_auto(self):
        if self.auto_activo:
            self.detener_auto()
            return
        if self.estado == "terminado":
            messagebox.showinfo("Aviso", "La lista ya está ordenada. Pulsa 'Reiniciar'.")
            return
        self.auto_activo = True
        self.btn_auto.config(text="Pausar")
        self.ciclo()

    def ciclo(self):
        if not self.auto_activo:
            return
        if self.paso():
            self.root.after(self.vel.get(), self.ciclo)

    def detener_auto(self):
        self.auto_activo = False
        self.btn_auto.config(text="Automático")

    def reiniciar(self):
        self.detener_auto()
        if self.original:
            self.datos = list(self.original)
        self.gen = None
        self.estado = "listo"
        self.comparaciones = self.movimientos = self.num_paso = 0
        self.limpiar_log()
        self.dibujar()
        self.actualizar_estado()

    # ----- dibujo -----
    def dibujar(self, info=None):
        c = self.canvas
        c.delete("all")
        n = len(self.datos)
        if n == 0:
            c.create_text(ANCHO / 2, ALTO / 2, fill="#888888", font=("Arial", 13),
                          text="Captura datos manualmente o pulsa 'Cargar ejemplo'")
            return
        info = info or {}
        comp = info.get("comp", ())
        ordenados = info.get("ordenados", set())
        minimo = info.get("minimo")
        hubo_swap = info.get("tipo") == "intercambio"
        maximo = max(v for _, v in self.datos) or 1
        ancho = ANCHO / n
        base = ALTO - 45
        for i, (nombre, valor) in enumerate(self.datos):
            x0, x1 = i * ancho + 8, (i + 1) * ancho - 8
            y0 = base - (valor / maximo) * (ALTO - 100) - 4
            if i in comp and hubo_swap:
                color = ROJO
            elif i == minimo:
                color = MORADO
            elif i in comp:
                color = AMARILLO
            elif i in ordenados:
                color = VERDE
            else:
                color = AZUL
            c.create_rectangle(x0, y0, x1, base, fill=color, outline="#333333")
            cx = (x0 + x1) / 2
            c.create_text(cx, y0 - 11, text=formato(valor), font=("Arial", 10, "bold"))
            c.create_text(cx, base + 13, text=nombre[:10], font=("Arial", 9))
            c.create_text(cx, base + 28, text=f"[{i}]", fill="#888888", font=("Arial", 8))

    # ----- utilidades -----
    def escribir(self, texto):
        self.log.config(state="normal")
        self.log.insert("end", texto + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def limpiar_log(self):
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")

    def actualizar_estado(self):
        self.lbl_estado.config(text=f"Elementos: {len(self.datos)}   Comparaciones: "
                                    f"{self.comparaciones}   Intercambios: {self.movimientos}")


if __name__ == "__main__":
    ventana = tk.Tk()
    App(ventana)
    ventana.mainloop()