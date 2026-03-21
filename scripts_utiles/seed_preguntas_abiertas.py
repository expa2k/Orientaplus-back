import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.pregunta_test import PreguntaTest

app = create_app()

preguntas_abiertas_ejemplo = [
    {
        "texto": "Con tus propias palabras: ¿Cuáles son las tres actividades que más disfrutas hacer en tu tiempo libre y por qué?",
        "bloque": 1,
        "dimension_riasec": "X" # Es un dummy, Gemini asignará los puntos RIASEC reales a todo
    },
    {
        "texto": "Imagina que en el futuro tuvieras el trabajo ideal, ¿cómo sería tu día a día en la rutina de esa profesión?",
        "bloque": 2,
        "dimension_riasec": "X"
    }
]

from sqlalchemy import text

with app.app_context():
    try:
        print("Iniciando inyección de preguntas abiertas dinámicas...")
        
        # Truco hacker: Modificar la estructura de la base de datos MySQL al vuelo
        db.session.execute(text("ALTER TABLE preguntas_test MODIFY COLUMN tipo ENUM('likert', 'opcion_multiple', 'abierta') NOT NULL DEFAULT 'likert';"))
        db.session.commit()
        print("✔Estructura de tabla actualizada para permitir 'abierta'.")
        
        # Eliminar las preguntas abiertas anteriores si existían
        PreguntaTest.query.filter_by(tipo='abierta').delete()
        
        for p in preguntas_abiertas_ejemplo:
            nueva_pregunta = PreguntaTest(
                bloque=p["bloque"],
                tipo="abierta",
                texto=p["texto"],
                dimension_riasec=p["dimension_riasec"],
                orden=99, # Asegura que salgan hasta el final de cada bloque numéricamente
                activo=True
            )
            db.session.add(nueva_pregunta)
            
        db.session.commit()
        print("¡Éxito! Base de datos actualizada con 2 preguntas abiertas intercaladas en el bloque 1 y 2.")
    except Exception as e:
        db.session.rollback()
        print(f"Error procesando: {str(e)}")
