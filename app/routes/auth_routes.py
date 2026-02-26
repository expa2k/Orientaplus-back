import bcrypt
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.usuario import Usuario
from app.extensions import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    correo = data.get('correo', '').strip().lower()
    contrasena = data.get('contrasena', '')

    if not correo or not contrasena:
        return jsonify({'message': 'Correo y contraseña son requeridos'}), 400

    user = Usuario.query.filter_by(correo=correo).first()

    if not user or not bcrypt.checkpw(contrasena.encode(), user.contrasena.encode()):
        return jsonify({'message': 'Credenciales incorrectas'}), 401

    if not user.activo:
        return jsonify({'message': 'Cuenta desactivada'}), 403

    token = create_access_token(
        identity=str(user.id),
        additional_claims={'user': user.to_dict()}
    )

    return jsonify({'token': token, 'user': user.to_dict()}), 200


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    nombre = data.get('nombre', '').strip()
    apellido = data.get('apellido', '').strip()
    correo = data.get('correo', '').strip().lower()
    contrasena = data.get('contrasena', '')

    if not all([nombre, apellido, correo, contrasena]):
        return jsonify({'message': 'Todos los campos son requeridos'}), 400

    if len(contrasena) < 6:
        return jsonify({'message': 'La contraseña debe tener mínimo 6 caracteres'}), 400

    if Usuario.query.filter_by(correo=correo).first():
        return jsonify({'message': 'El correo ya está registrado'}), 409

    hashed = bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt()).decode()

    user = Usuario(
        nombre=nombre,
        apellido=apellido,
        correo=correo,
        contrasena=hashed,
        rol='estudiante'
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(
        identity=str(user.id),
        additional_claims={'user': user.to_dict()}
    )

    return jsonify({'token': token, 'user': user.to_dict()}), 201


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = Usuario.query.get(user_id)
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    return jsonify(user.to_dict()), 200


@auth_bp.route('/me', methods=['PATCH'])
@jwt_required()
def update_me():
    user_id = get_jwt_identity()
    user = Usuario.query.get(user_id)
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    nombre = data.get('nombre', '').strip()
    apellido = data.get('apellido', '').strip()
    correo = data.get('correo', '').strip().lower()
    contrasena = data.get('contrasena', '')

    if not all([nombre, apellido, correo]):
        return jsonify({'message': 'Nombre, apellido y correo son requeridos'}), 400

    existing = Usuario.query.filter_by(correo=correo).first()
    if existing and str(existing.id) != str(user_id):
        return jsonify({'message': 'El correo ya está en uso'}), 409

    user.nombre = nombre
    user.apellido = apellido
    user.correo = correo

    if contrasena:
        if len(contrasena) < 6:
            return jsonify({'message': 'Mínimo 6 caracteres'}), 400
        user.contrasena = bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt()).decode()

    db.session.commit()

    new_token = create_access_token(
        identity=str(user.id),
        additional_claims={'user': user.to_dict()}
    )

    return jsonify({'token': new_token, 'user': user.to_dict()}), 200
