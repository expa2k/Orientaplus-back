import sys
import os
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.carrera import Carrera
from app.models.mercado_regional import MercadoRegional

app = create_app()

def seed_mercado():
    with app.app_context():
        # Asegurar que la tabla exista (crear solo si no existe)
        db.create_all()
        
        carreras = Carrera.query.all()
        if not carreras:
            print("No hay carreras en la BD.")
            return
            
        print("Limpiando datos de mercado antiguos...")
        MercadoRegional.query.delete()
        
        print("Generando datos de demanda y salario estimados para Sinaloa...")
        
        for carrera in carreras:
            # Logica basica para estimar sueldos creibles
            perfil = carrera.perfil_riasec
            # Ingenierias/Tecnologia (I, R, E) tienden a sueldos mas altos y alta demanda
            if 'I' in perfil and 'R' in perfil:
                salario = random.randint(180, 250) * 100
                demanda = 'Alta'
            # Artes y Sociales (S, A) varian mas
            elif 'S' in perfil or 'A' in perfil:
                salario = random.randint(100, 160) * 100
                demanda = random.choice(['Media', 'Baja'])
            # Empresarial y Convencional (E, C)
            elif 'E' in perfil or 'C' in perfil:
                salario = random.randint(140, 200) * 100
                demanda = random.choice(['Alta', 'Media'])
            else:
                salario = random.randint(120, 180) * 100
                demanda = 'Media'
                
            nuevo_registro = MercadoRegional(
                carrera_id=carrera.id,
                estado='Sinaloa',
                salario_promedio=salario,
                demanda_laboral=demanda
            )
            db.session.add(nuevo_registro)
            
        db.session.commit()
        print(f"Exito: Se insertaron {len(carreras)} perfiles laborales regionales para Sinaloa.")

if __name__ == '__main__':
    seed_mercado()
