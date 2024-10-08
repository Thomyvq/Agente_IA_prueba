import tkinter as tk
from tkinter import messagebox
import random
import numpy as np
import time

class LineFollowerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Agente Seguidor de Líneas")
        self.root.geometry("1000x800")
        
        self.malla = None
        self.N = 0
        self.M = 0
        self.agente = None
        self.cell_size = 40  # Tamaño de cada celda
        self.iteraciones = []
        self.numero_paso = 0  # Para numerar cada paso
        self.pasos_recorridos = []  # Lista para guardar el recorrido del agente
        
        # Crear los botones
        self.btn_generar_malla = tk.Button(self.root, text="Generar Malla", command=self.generar_malla, width=20, height=2)
        self.btn_generar_malla.pack(pady=10)
        
        self.btn_inicializar_agente = tk.Button(self.root, text="Inicializar Agente", command=self.inicializar_agente, state=tk.DISABLED, width=20, height=2)
        self.btn_inicializar_agente.pack(pady=10)
        
        self.btn_iniciar_simulacion = tk.Button(self.root, text="Iniciar Simulación", command=self.iniciar_simulacion, state=tk.DISABLED, width=20, height=2)
        self.btn_iniciar_simulacion.pack(pady=10)
        
        self.btn_reiniciar = tk.Button(self.root, text="Reiniciar", command=self.reiniciar, state=tk.DISABLED, width=20, height=2)
        self.btn_reiniciar.pack(pady=10)
        
        self.canvas = tk.Canvas(self.root, width=700, height=700, bg='white')
        self.canvas.pack(side=tk.LEFT, pady=10)
        
        # Crear el cuadro para el registro de movimientos
        self.log_frame = tk.Frame(self.root, bd=2, relief="groove")
        self.log_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill="both", expand=True)
        self.log_label = tk.Label(self.log_frame, text="Registro de Movimientos", font=("Helvetica", 14))
        self.log_label.pack()
        self.log_text = tk.Text(self.log_frame, width=40, height=30, wrap="word", font=("Helvetica", 10))
        self.log_text.pack(padx=5, pady=5)

        self.posiciones_agente = []  # Para almacenar las posiciones del agente

    def generar_malla(self):
        self.N = random.randint(8, 12)
        self.M = random.randint(8, 12)
        self.malla = np.zeros((self.N, self.M), dtype=int)

        # Agregar líneas oscuras (1)
        for i in range(self.N):
            num_lineas = random.randint(1, self.M // 2)
            for _ in range(num_lineas):
                pos = random.randint(0, self.M - 1)
                self.malla[i][pos] = 1  # Celda oscura (línea)

        # Agregar paredes representadas por 2
        for _ in range(random.randint(2, 5)):  # Agregar entre 2 y 5 paredes
            pos_x = random.randint(0, self.N - 1)
            pos_y = random.randint(0, self.M - 1)
            self.malla[pos_x][pos_y] = 2  # Celda de pared

        self.btn_inicializar_agente.config(state=tk.NORMAL)
        self.btn_reiniciar.config(state=tk.NORMAL)
        self.dibujar_malla()
    
    def dibujar_malla(self):
        self.canvas.delete("all")
        
        # Dibujar recorrido anterior (líneas punteadas)
        for paso in self.pasos_recorridos:
            x, y = paso
            self.canvas.create_oval(
                y * self.cell_size + 15, x * self.cell_size + 15,
                y * self.cell_size + 25, x * self.cell_size + 25,
                outline='blue', width=2
            )
        
        for i in range(self.N):
            for j in range(self.M):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                if self.malla[i][j] == 1:
                    color = 'black'  # Línea
                elif self.malla[i][j] == 2:
                    color = 'gray'  # Pared
                else:
                    color = 'white'  # Espacio vacío
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='gray')
    
    def inicializar_agente(self):
        if self.malla is None:
            messagebox.showerror("Error", "Primero debe generar la malla.")
            return
        
        self.agente = AgenteSeguidorLineas(self.malla, self.N, self.M)
        self.btn_iniciar_simulacion.config(state=tk.NORMAL)
        self.numero_paso = 0  # Iniciar la numeración desde cero
        self.pasos_recorridos.clear()  # Limpiar los pasos anteriores
        self.dibujar_agente()
        
    def dibujar_agente(self):
        # Dibujar el agente en el canvas
        if self.agente:
            x, y = self.agente.pos_x, self.agente.pos_y
            # Dibujar un cuadrado para el cuerpo del agente
            self.canvas.create_rectangle(
                y * self.cell_size + 5, x * self.cell_size + 5, 
                (y + 1) * self.cell_size - 5, (x + 1) * self.cell_size - 5, 
                fill='red'
            )
            # Dibujar un pequeño rectángulo en la parte superior para mostrar la "cabeza"
            if self.agente.direccion == 'Norte':
                self.canvas.create_rectangle(
                    y * self.cell_size + 15, x * self.cell_size + 5, 
                    (y + 1) * self.cell_size - 15, x * self.cell_size + 15, 
                    fill='yellow'
                )
            elif self.agente.direccion == 'Sur':
                self.canvas.create_rectangle(
                    y * self.cell_size + 15, (x + 1) * self.cell_size - 15, 
                    (y + 1) * self.cell_size - 15, (x + 1) * self.cell_size - 5, 
                    fill='yellow'
                )
            elif self.agente.direccion == 'Este':
                self.canvas.create_rectangle(
                    (y + 1) * self.cell_size - 15, x * self.cell_size + 15, 
                    (y + 1) * self.cell_size - 5, (x + 1) * self.cell_size - 15, 
                    fill='yellow'
                )
            elif self.agente.direccion == 'Oeste':
                self.canvas.create_rectangle(
                    y * self.cell_size + 5, x * self.cell_size + 15, 
                    y * self.cell_size + 15, (x + 1) * self.cell_size - 15, 
                    fill='yellow'
                )
            # Mostrar el número del paso dentro del agente
            self.canvas.create_text(
                y * self.cell_size + self.cell_size // 2, 
                x * self.cell_size + self.cell_size // 2, 
                text=str(self.numero_paso), fill='white', font=("Helvetica", 12)
            )
    
    def iniciar_simulacion(self):
        self.iteraciones.clear()
        self.log_text.delete(1.0, tk.END)
        self.posiciones_agente.clear()  # Limpiar las posiciones almacenadas
        
        # Simulación en bucle con pausa para ver los movimientos paso a paso
        for i in range(100):
            self.log_movimiento()  # Registrar el movimiento actual
            self.agente.mover()
            self.numero_paso += 1
            self.pasos_recorridos.append((self.agente.pos_x, self.agente.pos_y))  # Guardar la posición
            self.dibujar_malla()  # Redibujar la malla con recorrido
            self.dibujar_agente()  # Dibujar el agente con el número del paso
            self.posiciones_agente.append((self.agente.pos_x, self.agente.pos_y))
            self.dibujar_ruta()
            self.root.update()  # Actualizar la interfaz
            time.sleep(0.2)  # Pausar 0.5 segundos entre movimientos
            
            if self.chequear_bucle():
                self.tree.insert("", "end", values=("Fin de simulación: Bucle detectado", "", "", "", ""))
                break
    
    def log_movimiento(self):
        # Validar si el widget Text existe
        if self.log_text.winfo_exists():
            headers = "{:<15} {:<20} {:<15} {:<20} {:<15}".format(
                "Pos. Inicial", "Percepciones", "Regla", "Acción", "Pos. Final")
            if self.numero_paso == 0:
                self.log_text.insert(tk.END, headers + "\n" + "-" * 85 + "\n")
            
            pos_inicial = f"({self.agente.pos_x}, {self.agente.pos_y})"
            percepciones = f"Cam. Principal: {self.agente.percepcion_camara_principal()}, " \
                           f"Cam. Frontal: {self.agente.percepcion_camara_frontal()}"
            regla = self.agente.regla_aplicada
            accion = self.agente.accion
            pos_final = f"({self.agente.pos_x}, {self.agente.pos_y})"
            
            row = "{:<15} {:<20} {:<15} {:<20} {:<15}".format(
                pos_inicial, percepciones, regla, accion, pos_final)
            
            self.log_text.insert(tk.END, row + "\n")
    
    def chequear_bucle(self):
        # Implementa la lógica para chequear si el agente está en un bucle
        return False  # Cambia esto según la lógica real de detección de bucles
            
    def dibujar_ruta(self):
        if len(self.posiciones_agente) > 1:
            for i in range(len(self.posiciones_agente) - 1):
                x1, y1 = self.posiciones_agente[i][1] * self.cell_size + self.cell_size // 2, self.posiciones_agente[i][0] * self.cell_size + self.cell_size // 2
                x2, y2 = self.posiciones_agente[i + 1][1] * self.cell_size + self.cell_size // 2, self.posiciones_agente[i + 1][0] * self.cell_size + self.cell_size // 2
                
                # Dibujar línea punteada
                self.canvas.create_line(x1, y1, x2, y2, dash=(2, 2), fill='blue')
    
    def reiniciar(self):
        self.malla = None
        self.N = 0
        self.M = 0
        self.agente = None
        self.iteraciones.clear()
        self.pasos_recorridos.clear()
        self.btn_inicializar_agente.config(state=tk.DISABLED)
        self.btn_reiniciar.config(state=tk.DISABLED)
        self.btn_iniciar_simulacion.config(state=tk.DISABLED)
        self.canvas.delete("all")
        self.log_text.delete(1.0, tk.END)

# Clase del agente seguidor de líneas
class AgenteSeguidorLineas:
    def __init__(self, malla, N, M):
        self.malla = malla
        self.N = N
        self.M = M
        self.pos_x = random.randint(0, self.N - 1)  # Posición inicial
        self.pos_y = random.randint(0, self.M - 1)
        self.direccion = random.choice(['Norte', 'Sur', 'Este', 'Oeste'])
        self.regla_aplicada = ''
        self.accion = ''
        self.choco = False  # Variable para recordar el choque
    
    def percepcion_orientacion(self):
        return self.direccion
    
    def percepcion_contacto(self):
        # Detectar contacto con las paredes
        if self.direccion == 'Norte' and self.pos_x == 0:
            return 'Contacto'
        if self.direccion == 'Sur' and self.pos_x == self.N - 1:
            return 'Contacto'
        if self.direccion == 'Este' and self.pos_y == self.M - 1:
            return 'Contacto'
        if self.direccion == 'Oeste' and self.pos_y == 0:
            return 'Contacto'
        # Verificar colisiones con celdas de paredes (representadas por 2)
        if self.direccion == 'Norte' and self.malla[self.pos_x - 1][self.pos_y] == 2:
            return 'Contacto'
        if self.direccion == 'Sur' and self.malla[self.pos_x + 1][self.pos_y] == 2:
            return 'Contacto'
        if self.direccion == 'Este' and self.malla[self.pos_x][self.pos_y + 1] == 2:
            return 'Contacto'
        if self.direccion == 'Oeste' and self.malla[self.pos_x][self.pos_y - 1] == 2:
            return 'Contacto'
        return 'No Contacto'
    
    def percepcion_camara_principal(self):
        if self.malla[self.pos_x][self.pos_y] == 1:
            return 'Piso Oscuro'
        return 'Piso Claro'
    
    def percepcion_camara_frontal(self):
        # Devuelve el estado de las celdas adyacentes
        izquierda = self.malla[self.pos_x][self.pos_y - 1] if self.pos_y > 0 else 2  # Pared si está en el borde
        centro = self.malla[self.pos_x][self.pos_y]
        derecha = self.malla[self.pos_x][self.pos_y + 1] if self.pos_y < self.M - 1 else 2  # Pared si está en el borde
        return izquierda, centro, derecha
    
    def obtener_estado_casilla(self, x, y):
    # Comprobar si las coordenadas están dentro de los límites de la malla
        if x < 0 or x >= len(self.malla) or y < 0 or y >= len(self.malla[0]):
            return 2  # Si está fuera de los límites, es borde o pared
        # Devolver el estado de la casilla
        return self.malla[x][y]

    def mover(self):
        # Obtener el estado de las casillas frente, izquierda y derecha según la dirección actual
        if self.direccion == 'Norte':
            frente = self.obtener_estado_casilla(self.pos_x - 1, self.pos_y)
            izquierda = self.obtener_estado_casilla(self.pos_x, self.pos_y - 1)
            derecha = self.obtener_estado_casilla(self.pos_x, self.pos_y + 1)
        elif self.direccion == 'Sur':
            frente = self.obtener_estado_casilla(self.pos_x + 1, self.pos_y)
            izquierda = self.obtener_estado_casilla(self.pos_x, self.pos_y + 1)
            derecha = self.obtener_estado_casilla(self.pos_x, self.pos_y - 1)
        elif self.direccion == 'Este':
            frente = self.obtener_estado_casilla(self.pos_x, self.pos_y + 1)
            izquierda = self.obtener_estado_casilla(self.pos_x - 1, self.pos_y)
            derecha = self.obtener_estado_casilla(self.pos_x + 1, self.pos_y)
        elif self.direccion == 'Oeste':
            frente = self.obtener_estado_casilla(self.pos_x, self.pos_y - 1)
            izquierda = self.obtener_estado_casilla(self.pos_x + 1, self.pos_y)
            derecha = self.obtener_estado_casilla(self.pos_x - 1, self.pos_y)

        # Aplicar las reglas de movimiento:
        if frente == 0 and izquierda == 0 and derecha == 0:
            self.avanzar()
        # 1. Si la casilla frente es blanca y ambas (izquierda y derecha) son negras, gira a la derecha
        if frente == 0 and izquierda == 1 and derecha == 1:
            self.girar_derecha()
        # 2. Si frente es blanca, derecha es blanca y izquierda es negra, avanza y gira a la izquierda
        elif frente == 0 and derecha == 0 and izquierda == 1:
            self.avanzar()
            self.girar_izquierda()
        # 3. Si frente es blanca, izquierda es blanca y derecha es negra, avanza y gira a la derecha
        elif frente == 0 and izquierda == 0 and derecha == 1:
            self.avanzar()
            self.girar_derecha()
        # Si ninguna regla se cumple, simplemente avanza
        else:
            self.avanzar()

    def avanzar(self):
        # Actualizar la posición del agente según su dirección actual
        if self.direccion == 'Norte':
            self.pos_x -= 1
        elif self.direccion == 'Sur':
            self.pos_x += 1
        elif self.direccion == 'Este':
            self.pos_y += 1
        elif self.direccion == 'Oeste':
            self.pos_y -= 1


    def girar_derecha(self):
        # Cambiar la dirección actual del agente en sentido horario
        if self.direccion == 'Norte':
            self.direccion = 'Este'
        elif self.direccion == 'Este':
            self.direccion = 'Sur'
        elif self.direccion == 'Sur':
            self.direccion = 'Oeste'
        elif self.direccion == 'Oeste':
            self.direccion = 'Norte'

    def girar_izquierda(self):
        # Cambiar la dirección actual del agente en sentido antihorario
        if self.direccion == 'Norte':
            self.direccion = 'Oeste'
        elif self.direccion == 'Oeste':
            self.direccion = 'Sur'
        elif self.direccion == 'Sur':
            self.direccion = 'Este'
        elif self.direccion == 'Este':
            self.direccion = 'Norte'



# Iniciar la aplicación
root = tk.Tk()
app = LineFollowerApp(root)
root.mainloop()
