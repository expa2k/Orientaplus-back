from app import create_app
from flask_cors import CORS

app = create_app()

# Habilitar CORS para permitir peticiones desde tu frontend (Vercel, etc.)
CORS(app)

if __name__ == '__main__':
    app.run(debug=True, port=5001)