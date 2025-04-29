import joblib
import matplotlib.pyplot as plt
from sklearn.tree import plot_tree

# Cargar el modelo Random Forest con el nuevo nombre
# Asegúrate de usar aquí el nombre real que guardaste después de entrenarlo
# Por ejemplo: modelo_randomforest_nuevo_20250428_1956.pkl
modelo_rf = joblib.load('modelo_random_forest3_20250428_111718.pkl')

# Dibujar el primer árbol del Random Forest
plt.figure(figsize=(20, 10))
plot_tree(modelo_rf.estimators_[0],
          feature_names=["temperatura", "humedad", "hora", "dia_semana"],
          class_names=["OFF", "ON"],
          filled=True, rounded=True, max_depth=3)

plt.title("Árbol de un Random Forest - Control de Calefacción")
plt.show()