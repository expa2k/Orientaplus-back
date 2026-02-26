import os
import bcrypt
from flask import Flask
from config import Config
from app.extensions import db, jwt, cors


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r'/api/*': {'origins': 'http://localhost:4200'}})

    from app.routes.auth_routes import auth_bp
    from app.routes.user_routes import user_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')

    with app.app_context():
        db.create_all()
        _seed_admin()

    return app


def _seed_admin():
    from app.models.usuario import Usuario

    email = os.getenv('ADMIN_EMAIL', 'admin@orientaplus.com')
    if Usuario.query.filter_by(correo=email).first():
        return

    hashed = bcrypt.hashpw(
        os.getenv('ADMIN_PASSWORD', 'Admin123!').encode(),
        bcrypt.gensalt()
    ).decode()

    admin = Usuario(
        nombre=os.getenv('ADMIN_NOMBRE', 'Admin'),
        apellido=os.getenv('ADMIN_APELLIDO', 'Sistema'),
        correo=email,
        contrasena=hashed,
        rol='admin',
        activo=True
    )
    db.session.add(admin)
    db.session.commit()
