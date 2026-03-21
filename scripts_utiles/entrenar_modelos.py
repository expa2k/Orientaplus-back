import os
import sys
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score
import joblib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

app = create_app()

def entrenar_modelos():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'machine_learning'))
    csv_path = os.path.join(base_dir, 'dataset_sintetico_uas.csv')
    
    if not os.path.exists(csv_path):
        print(f"Error: No se encontro el archivo de datos en {csv_path}")
        return

    print("Cargando dataset...")
    df = pd.read_csv(csv_path)
    
    X = df[['R', 'I', 'A', 'S', 'E', 'C']].astype(float)
    
    # NORMALIZACION DE ESCALA (SCALE INVARIANCE):
    # Convertimos cada fila en proporciones (0.0 a 1.0) para que al modelo le importe
    # la 'forma' del perfil y no la magnitud absoluta de los puntos.
    X = X.div(X.sum(axis=1), axis=0)
    # Llenar ceros en caso de divisiones por cero raras
    X = X.fillna(1.0/6.0)

    y = df['carrera_id']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Optimizando hiperparametros de Random Forest (puede tomar un minuto o dos)...")
    rf_param_grid = {'n_estimators': [100, 200], 'max_depth': [None, 10, 20], 'min_samples_split': [2, 5]}
    rf_base = RandomForestClassifier(random_state=42)
    rf_grid = GridSearchCV(rf_base, rf_param_grid, cv=3, n_jobs=-1)
    rf_grid.fit(X_train, y_train)
    rf_clf = rf_grid.best_estimator_
    rf_pred = rf_clf.predict(X_test)
    rf_acc = accuracy_score(y_test, rf_pred)
    print(f"Mejor Random Forest encontrado: {rf_grid.best_params_}")
    print(f"Random Forest Accuracy Optimizado: {rf_acc:.2f}")
    
    print("Optimizando hiperparametros de KNN...")
    knn_param_grid = {'n_neighbors': [3, 5, 7, 11], 'weights': ['uniform', 'distance']}
    knn_base = KNeighborsClassifier()
    knn_grid = GridSearchCV(knn_base, knn_param_grid, cv=3, n_jobs=-1)
    knn_grid.fit(X_train, y_train)
    knn_clf = knn_grid.best_estimator_
    knn_pred = knn_clf.predict(X_test)
    knn_acc = accuracy_score(y_test, knn_pred)
    print(f"Mejor KNN encontrado: {knn_grid.best_params_}")
    print(f"KNN Accuracy Optimizado: {knn_acc:.2f}")
    
    rf_model_path = os.path.join(base_dir, 'modelo_rf.joblib')
    knn_model_path = os.path.join(base_dir, 'modelo_knn.joblib')
    
    joblib.dump(rf_clf, rf_model_path)
    joblib.dump(knn_clf, knn_model_path)
    
    print("Modelos exportados correctamente a formato .joblib")

if __name__ == '__main__':
    with app.app_context():
        entrenar_modelos()
