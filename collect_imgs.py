import os
import cv2

# Configuración del directorio de datos
DATA_DIR = './data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

number_of_classes = 27
dataset_size = 100

# Abrir la cámara
cap = cv2.VideoCapture(1) 

if not cap.isOpened():
    print("Error: No se pudo abrir la cámara.")
    exit()

# Recolectar datos para cada clase
for j in range(number_of_classes):
    class_dir = os.path.join(DATA_DIR, str(j))
    if not os.path.exists(class_dir):
        os.makedirs(class_dir)

    print(f'Collecting data for class {j}')

    # Esperar a que el usuario esté listo
    done = False
    while not done:
        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo capturar un frame del video.")
            break
        
        cv2.putText(frame, 'Ready? Press "Q" when ready! :)', (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3,
                    cv2.LINE_AA)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            done = True

    # Capturar y guardar imágenes
    counter = 0
    while counter < dataset_size:
        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo capturar un frame del video.")
            break
        
        cv2.imshow('frame', frame)
        img_path = os.path.join(class_dir, f'{counter}.jpg')
        cv2.imwrite(img_path, frame)
        print(f'Imagen guardada en {img_path}')
        
        counter += 1
        cv2.waitKey(1)  # Pequeña espera para evitar la captura demasiado rápida

# Liberar recursos
cap.release()
cv2.destroyAllWindows()

