import sys
import os
import csv
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.carrera import Carrera

app = create_app()

def generar_dataset(rutacsv, muestras_por_carrera=300):
    """
    Genera estudiantes falsos cuyas puntuaciones encajan en mayor o menor
    medida con las dimensiones dominantes de cada carrera de la base de datos.
    """
    with app.app_context():
        carreras = Carrera.query.filter_by(activo=True).all()
        if not carreras:
            print("❌ No hay carreras en la base de datos. Primero corre el seed de carreras.")
            return

        print(f"✅ Se encontraron {len(carreras)} carreras oficiales.")
        print(f"⚙️  Generando {muestras_por_carrera} estudiantes sintéticos por carrera...")
        
        os.makedirs(os.path.dirname(rutacsv), exist_ok=True)
        
        with open(rutacsv, mode='w', newline='', encoding='utf-8') as archivo_csv:
            campos = ['R', 'I', 'A', 'S', 'E', 'C', 'carrera_id', 'nombre_carrera']
            escritor = csv.DictWriter(archivo_csv, fieldnames=campos)
            escritor.writeheader()
            
            total_generado = 0
            
            for carrera in carreras:
                perfil = carrera.perfil_riasec.upper() # Ej: 'IRE'
                
                for _ in range(muestras_por_carrera):
                    estudiante_sintetico = {
                        'R': random.uniform(1.5, 4.0),
                        'I': random.uniform(1.5, 4.0),
                        'A': random.uniform(1.5, 4.0),
                        'S': random.uniform(1.5, 4.0),
                        'E': random.uniform(1.5, 4.0),
                        'C': random.uniform(1.5, 4.0),
                        'carrera_id': carrera.id,
                        'nombre_carrera': carrera.nombre
                    }
                    
                    # Dar un "Boost" matemático a las letras principales de la carrera realista
                    # Escala real: Likert (1-5) + NLP (0-3) = max ~8
                    for indice, letra in enumerate(perfil):
                        peso = len(perfil) - indice # La primera letra es más fuerte (3, 2, 1)
                        rango_min = 4.0 + (peso * 0.8) # ej primaria: 6.4
                        rango_max = rango_min + 1.5    # ej primaria: 7.9
                        
                        estudiante_sintetico[letra] = random.uniform(rango_min, rango_max)
                        
                    # Redondeamos a 2 decimales para más limpieza
                    for l in ['R', 'I', 'A', 'S', 'E', 'C']:
                        estudiante_sintetico[l] = round(min(estudiante_sintetico[l], 9.5), 2)
                        
                    escritor.writerow(estudiante_sintetico)
                    total_generado += 1
                    
        print(f"🎉 ¡Dataset Sintético completado!")
        print(f"📁 {total_generado} filas exportadas a: {rutacsv}")

if __name__ == '__main__':
    ruta_destino = os.path.join(os.path.dirname(__file__), '..', 'machine_learning', 'dataset_sintetico_uas.csv')
    generar_dataset(ruta_destino, muestras_por_carrera=100)
