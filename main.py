import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import mediapipe as mp
import numpy as np
import pickle
import datetime
from database import *

# Cargar el modelo
model_dict = pickle.load(open('./model.p', 'rb'))
model = model_dict['model']

# Configuración de MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

# Diccionario de etiquetas
labels_dict = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'J', 
               10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 17: 'R', 
               18: 'S', 19: 'T', 20: 'U', 21: 'V', 22: 'W', 23: 'X', 24: 'Y', 25: 'Z'}

# Lista para almacenar los caracteres
word = []

# Variable para almacenar el carácter detectado
letter_detected = False
predicted_character = ""

# Capturar video con la cámara
cap = cv2.VideoCapture(1)
cap.set(3, 640)
cap.set(4, 480)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Traductor de Lenguaje de Señas")
        self.geometry("800x600")
        self.resizable(False, False)

        # Frame para el sidebar
        sidebar_frame = ctk.CTkFrame(self, width=200, height=600, fg_color='#E0E0E0')
        sidebar_frame.place(x=0, y=0)

        # Botones del sidebar (Translate, History)
        translate_button = ctk.CTkButton(sidebar_frame, text="Traducir", width=160, height=50, command=lambda: self.change_content("Traducir"), bg_color="#009688", fg_color="#009688", text_color="#FFFFFF")
        translate_button.place(x=20, y=25)

        # Separador entre botones
        separator = ctk.CTkFrame(sidebar_frame, width=180, height=2, fg_color='black')
        separator.place(x=10, y=87)

        history_button = ctk.CTkButton(sidebar_frame, text="Historial", width=160, height=50, command=lambda: self.change_content("Historial"), bg_color="#009688", fg_color="#009688", text_color="#FFFFFF")
        history_button.place(x=20, y=100)

        self.translate_layout()

    def change_content(self, button):
        if button == "Traducir":
            self.section_frame.destroy()
            self.translate_layout()
        elif button == "Historial":
            self.section_frame.destroy()
            self.history_layout()

    def translate_layout(self):
        # Frame para el contenido
        self.section_frame = ctk.CTkFrame(self, width=600, height=600)
        self.section_frame.place(x=200, y=0)

        # Frame para la cámara
        self.video_frame = ctk.CTkFrame(self.section_frame, width=600, height=440, fg_color='#F9F9F9', bg_color='#F9F9F9')
        self.video_frame.place(x=0, y=0)

        # Frame para la palabra
        word_frame = ctk.CTkFrame(self.section_frame, width=600, height=60, fg_color='#F9F9F9', bg_color='#F9F9F9')
        word_frame.place(x=0, y=440)

        # Frame para los botones
        button_frame = ctk.CTkFrame(self.section_frame, width=600, height=100, fg_color='#F9F9F9', bg_color='#F9F9F9')
        button_frame.place(x=0, y=500)

        # Label para la palabra
        self.word_label = ctk.CTkLabel(word_frame, text="Palabra: ", font=("Arial", 20), text_color="#333333")
        self.word_label.place(x=10, y=15)

        # Boton para agregar una letra
        add_button = ctk.CTkButton(word_frame, text="Agregar", width=100, height=50, command=self.add_letter, fg_color="#B2DFDB", bg_color="#B2DFDB", text_color="#333333")
        add_button.place(x=450, y=5)

        # Boton para borrar la ultima letra
        delete_button = ctk.CTkButton(button_frame, text="Borrar", width=100, height=50, command=self.delete_letter, fg_color="#FFCDD2", bg_color="#FFCDD2", text_color="#333333")
        delete_button.place(x=50, y=25)

        # Boton para confirmar la palabra
        confirm_button = ctk.CTkButton(button_frame, text="Confirmar", width=100, height=50, command=self.confirm_word, fg_color="#B2DFDB", bg_color="#B2DFDB", text_color="#333333")
        confirm_button.place(x=250, y=25)

        # Boton para limpiar la palabra
        clear_button = ctk.CTkButton(button_frame, text="Limpiar", width=100, height=50, command=self.clear_word, fg_color="#FFCDD2", bg_color="#FFCDD2", text_color="#333333")
        clear_button.place(x=450, y=25)

        # Mostrar el video
        self.video()

    def history_layout(self):
        # Frame para el historial que ocupa la parte principal de la ventana, excluyendo el sidebar
        self.section_frame = ctk.CTkFrame(self)
        self.section_frame.place(x=200, y=0, relwidth=1, relheight=1, anchor="nw")

        # Frame interno para contenido del historial
        history_frame = ctk.CTkFrame(self.section_frame, fg_color='yellow')
        history_frame.pack(fill="both", expand=True)

        # Crear el canvas y el scrollbar
        self.canvas = tk.Canvas(history_frame)
        scrollbar = tk.Scrollbar(history_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Inicializar la tabla
        self.update_history_table()

    def update_history_table(self):
        # Limpiar el frame antes de actualizar
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Encabezados de la tabla
        tk.Label(self.scrollable_frame, text="Palabra", borderwidth=1, relief="solid").grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        tk.Label(self.scrollable_frame, text="Fecha", borderwidth=1, relief="solid").grid(row=0, column=1, sticky="nsew", padx=1, pady=1)
        tk.Label(self.scrollable_frame, text="Acción", borderwidth=1, relief="solid").grid(row=0, column=2, sticky="nsew", padx=1, pady=1)

        # Obtener los datos de la base de datos
        data = select()

        # Mostrar los datos en la tabla
        for i, row in enumerate(data):
            tk.Label(self.scrollable_frame, text=row[1], borderwidth=1, relief="solid").grid(row=i+1, column=0, sticky="nsew", padx=1, pady=1)
            tk.Label(self.scrollable_frame, text=row[2], borderwidth=1, relief="solid").grid(row=i+1, column=1, sticky="nsew", padx=1, pady=1)
            tk.Button(self.scrollable_frame, text="Eliminar", command=lambda id=row[0]: self.delete_and_update(id)).grid(row=i+1, column=2, sticky="nsew", padx=1, pady=1)

        # Configurar espacio uniforme para filas
        for i in range(len(data) + 1):
            self.scrollable_frame.grid_rowconfigure(i, weight=1)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=1)
        self.scrollable_frame.grid_columnconfigure(2, weight=1)

    def delete_and_update(self, id):
        # Eliminar el elemento de la base de datos
        delete(id)
        # Actualizar la tabla
        self.update_history_table()


    def video(self):
        def show_frame():
            global letter_detected, predicted_character

            ret, frame = cap.read()
            if not ret:
                return

            frame = cv2.resize(frame, (800, 700))

            H, W, _ = frame.shape
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Corregido a RGB
            results = hands.process(frame_rgb)

            letter_detected = False

            if results.multi_hand_landmarks:
                if len(results.multi_hand_landmarks) == 1:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    mp_drawing.draw_landmarks(
                        frame_rgb,  # Utilizando frame_rgb en lugar de frame
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())

                    data_aux = []
                    x_ = []
                    y_ = []

                    for i in range(len(hand_landmarks.landmark)):
                        x = hand_landmarks.landmark[i].x
                        y = hand_landmarks.landmark[i].y
                        x_.append(x)
                        y_.append(y)

                    for i in range(len(hand_landmarks.landmark)):
                        x = hand_landmarks.landmark[i].x
                        y = hand_landmarks.landmark[i].y
                        data_aux.append(x - min(x_))
                        data_aux.append(y - min(y_))

                    x1 = int(min(x_) * W) - 10
                    y1 = int(min(y_) * H) - 10
                    x2 = int(max(x_) * W) - 10
                    y2 = int(max(y_) * H) - 10

                    prediction = model.predict([np.asarray(data_aux)])
                    predicted_character = labels_dict[int(prediction[0])]
                    letter_detected = True

                    cv2.rectangle(frame_rgb, (x1, y1), (x2, y2), (0, 0, 0), 4)
                    cv2.putText(frame_rgb, predicted_character, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3, cv2.LINE_AA)

            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            video_label.imgtk = imgtk
            video_label.configure(image=imgtk)
            video_label.after(10, show_frame)

        video_label = tk.Label(self.video_frame)
        video_label.pack()
        show_frame()

    def add_letter(self):
        global word
        if letter_detected:
            word.append(predicted_character)
            self.update_word_label()

    def delete_letter(self):
        global word
        if word:
            word.pop()
            self.update_word_label()

    def confirm_word(self):
        global word
        if word:
            word_str = ''.join(word)
            insert(word_str, datetime.datetime.now())
            word = []
            self.update_word_label()
            messagebox.showinfo("Confirmación", "Palabra guardada en el historial.")

    def clear_word(self):
        global word
        word = []
        self.update_word_label()

    def update_word_label(self):
        global word
        word_str = ''.join(word)
        self.word_label.configure(text=f"Palabra: {word_str}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
