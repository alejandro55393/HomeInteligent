import pickle
import matplotlib.pyplot as plt
from sklearn.tree import plot_tree

# Cargar el modelo entrenado
with open("modelo_calefaccion.pkl", "rb") as f:
    modelo = pickle.load(f)

# Definir las características usadas en el entrenamiento
feature_names = ["temperatura", "humedad", "hora", "dia_semana"]

# Visualizar el árbol
plt.figure(figsize=(20, 10))
plot_tree(modelo, feature_names=feature_names, class_names=["OFF", "ON"], filled=True, rounded=True)
plt.title("Árbol de Decisión - Control Calefacción")
plt.show()