import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score
import numpy as np

# Cargar los datos
try:
    with open('./data.pickle', 'rb') as f:
        data_dict = pickle.load(f)
except FileNotFoundError:
    raise FileNotFoundError("El archivo de datos no se encuentra.")
except Exception as e:
    raise Exception(f"Error al cargar el archivo de datos: {e}")

data = np.asarray(data_dict['data'])
labels = np.asarray(data_dict['labels'])

# Dividir los datos en conjuntos de entrenamiento y prueba
x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, shuffle=True, stratify=labels)

# Definir el modelo
model = RandomForestClassifier()

# Ajustar el modelo con búsqueda de hiperparámetros
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10],
}
grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=5, n_jobs=-1, verbose=2)
grid_search.fit(x_train, y_train)

# Mejor modelo
best_model = grid_search.best_estimator_

# Realizar predicciones
y_predict = best_model.predict(x_test)

# Evaluar el modelo
score = accuracy_score(y_test, y_predict)
print(f'{score * 100:.2f}% de las muestras fueron clasificadas correctamente!')

# Guardar el modelo entrenado
try:
    with open('model.p', 'wb') as f:
        pickle.dump({'model': best_model}, f)
except Exception as e:
    raise Exception(f"Error al guardar el modelo: {e}")
