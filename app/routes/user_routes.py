import bcrypt
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.models.usuario import Usuario
from app.extensions import db

user_bp = Blueprint('users', __name__)


def admin_required(fn):
    from functools import wraps

    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        user_data = claims.get('user', {})
        if user_data.get('rol') != 'admin':
            return jsonify({'message': 'Acceso denegado'}), 403
        return fn(*args, **kwargs)

    return wrapper


@user_bp.route('', methods=['GET'])
@admin_required
def get_all():
    users = Usuario.query.order_by(Usuario.fecha_registro.desc()).all()
    return jsonify([u.to_dict() for u in users]), 200


@user_bp.route('', methods=['POST'])
@admin_required
def create():
    data = request.get_json()
    nombre = data.get('nombre', '').strip()
    apellido = data.get('apellido', '').strip()
    correo = data.get('correo', '').strip().lower()
    contrasena = data.get('contrasena', '')
    rol = data.get('rol', 'estudiante')

    if not all([nombre, apellido, correo, contrasena]):
        return jsonify({'message': 'Todos los campos son requeridos'}), 400

    if rol not in ('admin', 'estudiante'):
        return jsonify({'message': 'Rol inválido'}), 400

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
        rol=rol
    )
    db.session.add(user)
    db.session.commit()

    return jsonify(user.to_dict()), 201


@user_bp.route('/<int:user_id>', methods=['PUT'])
@admin_required
def update(user_id):
    user = Usuario.query.get_or_404(user_id)
    data = request.get_json()

    nombre = data.get('nombre', '').strip()
    apellido = data.get('apellido', '').strip()
    correo = data.get('correo', '').strip().lower()
    rol = data.get('rol', user.rol)

    if not all([nombre, apellido, correo]):
        return jsonify({'message': 'Nombre, apellido y correo son requeridos'}), 400

    if rol not in ('admin', 'estudiante'):
        return jsonify({'message': 'Rol inválido'}), 400

    existing = Usuario.query.filter_by(correo=correo).first()
    if existing and existing.id != user_id:
        return jsonify({'message': 'El correo ya está en uso'}), 409

    user.nombre = nombre
    user.apellido = apellido
    user.correo = correo
    user.rol = rol
    db.session.commit()

    return jsonify(user.to_dict()), 200


@user_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete(user_id):
    user = Usuario.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Usuario eliminado'}), 200


@user_bp.route('/<int:user_id>/toggle', methods=['PATCH'])
@admin_required
def toggle_active(user_id):
    user = Usuario.query.get_or_404(user_id)
    data = request.get_json()
    user.activo = bool(data.get('activo', not user.activo))
    db.session.commit()
    return jsonify(user.to_dict()), 200


@user_bp.route('/<int:user_id>/password', methods=['PATCH'])
@admin_required
def reset_password(user_id):
    user = Usuario.query.get_or_404(user_id)
    data = request.get_json()
    contrasena = data.get('contrasena', '')

    if len(contrasena) < 6:
        return jsonify({'message': 'Mínimo 6 caracteres'}), 400

    user.contrasena = bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt()).decode()
    db.session.commit()

    return jsonify({'message': 'Contraseña actualizada'}), 200
