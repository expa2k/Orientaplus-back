import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from sqlalchemy import text

app = create_app()

def fix_column():
    with app.app_context():
        # Cambiamos la longitud de String(10) a TEXT directamente en MySQL
        db.session.execute(text("ALTER TABLE respuestas_test MODIFY COLUMN valor TEXT NOT NULL;"))
        db.session.commit()
        print("Éxito: La columna 'valor' en 'respuestas_test' ha sido ampliada a TEXT para aceptar respuestas largas.")

if __name__ == '__main__':
    fix_column()
