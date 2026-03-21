import os
import joblib
import pandas as pd
from app.models.carrera import Carrera

class MLService:
    _rf_model = None
    _knn_model = None
    _models_loaded = False

    @classmethod
    def load_models(cls):
        if cls._models_loaded:
            return True
        
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'machine_learning'))
        rf_path = os.path.join(base_dir, 'modelo_rf.joblib')
        knn_path = os.path.join(base_dir, 'modelo_knn.joblib')
        
        if os.path.exists(rf_path) and os.path.exists(knn_path):
            cls._rf_model = joblib.load(rf_path)
            cls._knn_model = joblib.load(knn_path)
            cls._models_loaded = True
            return True
        return False

    @classmethod
    def predict_top_3(cls, vector_riasec):
        if not cls.load_models():
            return None

        features = [[
            vector_riasec.get('R', 0),
            vector_riasec.get('I', 0),
            vector_riasec.get('A', 0),
            vector_riasec.get('S', 0),
            vector_riasec.get('E', 0),
            vector_riasec.get('C', 0)
        ]]
        
        df_features = pd.DataFrame(features, columns=['R', 'I', 'A', 'S', 'E', 'C'])

        rf_probs = cls._rf_model.predict_proba(df_features)[0]
        knn_probs = cls._knn_model.predict_proba(df_features)[0]

        combined_probs = (rf_probs + knn_probs) / 2.0
        classes = cls._rf_model.classes_

        class_prob_pairs = list(zip(classes, combined_probs))
        class_prob_pairs.sort(key=lambda x: x[1], reverse=True)
        
        top_3 = class_prob_pairs[:3]
        total_prob_top_3 = sum(p[1] for p in top_3)
        
        # Filtro "Anti-Basura" / "A lo wey": Si la suma real de las probabilidades dictaminadas 
        # por la IA es abismalmente baja (ej. < 15% entre las 3), significa que el alumno 
        # metió datos planos/aleatorios y el Random Forest está adivinando a base de ruido.
        if total_prob_top_3 < 0.15:
            return None
            
        if total_prob_top_3 == 0:
            return None
            
        recomendaciones_ml = []
        for carrera_id, prob in top_3:
            normalized_prob = (prob / total_prob_top_3) * 100
            carrera = Carrera.query.get(int(carrera_id))
            if carrera:
                recomendaciones_ml.append({
                    'carrera': carrera.to_dict(),
                    'afinidad': round(normalized_prob, 1)
                })
                
        return recomendaciones_ml
