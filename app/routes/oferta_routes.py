from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.models.area_profesional import AreaProfesional
from app.models.carrera import Carrera
from app.extensions import db

oferta_bp = Blueprint('oferta', __name__)


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


@oferta_bp.route('/areas', methods=['GET'])
def get_areas():
    areas = AreaProfesional.query.filter_by(activo=True).order_by(AreaProfesional.nombre).all()
    return jsonify([a.to_dict() for a in areas]), 200


@oferta_bp.route('/areas/<int:area_id>', methods=['GET'])
def get_area(area_id):
    area = AreaProfesional.query.get_or_404(area_id)
    return jsonify(area.to_dict()), 200


@oferta_bp.route('/areas', methods=['POST'])
@admin_required
def create_area():
    data = request.get_json()
    nombre = data.get('nombre', '').strip()
    codigo = data.get('codigo_riasec', '').strip().upper()
    descripcion = data.get('descripcion', '').strip()
    icono = data.get('icono', '').strip()

    if not nombre or not codigo:
        return jsonify({'message': 'Nombre y código RIASEC son requeridos'}), 400

    if AreaProfesional.query.filter_by(codigo_riasec=codigo).first():
        return jsonify({'message': 'Ya existe un área con ese código RIASEC'}), 409

    area = AreaProfesional(
        nombre=nombre,
        codigo_riasec=codigo,
        descripcion=descripcion,
        icono=icono or None
    )
    db.session.add(area)
    db.session.commit()
    return jsonify(area.to_dict()), 201


@oferta_bp.route('/areas/<int:area_id>', methods=['PUT'])
@admin_required
def update_area(area_id):
    area = AreaProfesional.query.get_or_404(area_id)
    data = request.get_json()

    nombre = data.get('nombre', '').strip()
    codigo = data.get('codigo_riasec', '').strip().upper()
    descripcion = data.get('descripcion', '').strip()
    icono = data.get('icono', '').strip()

    if not nombre or not codigo:
        return jsonify({'message': 'Nombre y código RIASEC son requeridos'}), 400

    existing = AreaProfesional.query.filter_by(codigo_riasec=codigo).first()
    if existing and existing.id != area_id:
        return jsonify({'message': 'Ya existe un área con ese código RIASEC'}), 409

    area.nombre = nombre
    area.codigo_riasec = codigo
    area.descripcion = descripcion
    area.icono = icono or None
    db.session.commit()
    return jsonify(area.to_dict()), 200


@oferta_bp.route('/areas/<int:area_id>', methods=['DELETE'])
@admin_required
def delete_area(area_id):
    area = AreaProfesional.query.get_or_404(area_id)
    if area.carreras:
        return jsonify({'message': 'No se puede eliminar un área con carreras asociadas'}), 400
    db.session.delete(area)
    db.session.commit()
    return jsonify({'message': 'Área eliminada'}), 200


@oferta_bp.route('/carreras', methods=['GET'])
def get_carreras():
    area_id = request.args.get('area_id', type=int)
    query = Carrera.query.filter_by(activo=True)
    if area_id:
        query = query.filter_by(area_id=area_id)
    carreras = query.order_by(Carrera.nombre).all()
    return jsonify([c.to_dict() for c in carreras]), 200


@oferta_bp.route('/carreras/<int:carrera_id>', methods=['GET'])
def get_carrera(carrera_id):
    carrera = Carrera.query.get_or_404(carrera_id)
    return jsonify(carrera.to_dict()), 200


@oferta_bp.route('/carreras', methods=['POST'])
@admin_required
def create_carrera():
    data = request.get_json()
    area_id = data.get('area_id')
    nombre = data.get('nombre', '').strip()
    descripcion = data.get('descripcion', '').strip()
    perfil = data.get('perfil_riasec', '').strip().upper()
    campo = data.get('campo_laboral', '').strip()

    if not all([area_id, nombre, perfil]):
        return jsonify({'message': 'Área, nombre y perfil RIASEC son requeridos'}), 400

    if not AreaProfesional.query.get(area_id):
        return jsonify({'message': 'Área no encontrada'}), 404

    carrera = Carrera(
        area_id=area_id,
        nombre=nombre,
        descripcion=descripcion,
        perfil_riasec=perfil,
        campo_laboral=campo
    )
    db.session.add(carrera)
    db.session.commit()
    return jsonify(carrera.to_dict()), 201


@oferta_bp.route('/carreras/<int:carrera_id>', methods=['PUT'])
@admin_required
def update_carrera(carrera_id):
    carrera = Carrera.query.get_or_404(carrera_id)
    data = request.get_json()

    area_id = data.get('area_id', carrera.area_id)
    nombre = data.get('nombre', '').strip()
    descripcion = data.get('descripcion', '').strip()
    perfil = data.get('perfil_riasec', '').strip().upper()
    campo = data.get('campo_laboral', '').strip()

    if not all([area_id, nombre, perfil]):
        return jsonify({'message': 'Área, nombre y perfil RIASEC son requeridos'}), 400

    if not AreaProfesional.query.get(area_id):
        return jsonify({'message': 'Área no encontrada'}), 404

    carrera.area_id = area_id
    carrera.nombre = nombre
    carrera.descripcion = descripcion
    carrera.perfil_riasec = perfil
    carrera.campo_laboral = campo
    db.session.commit()
    return jsonify(carrera.to_dict()), 200


@oferta_bp.route('/carreras/<int:carrera_id>', methods=['DELETE'])
@admin_required
def delete_carrera(carrera_id):
    carrera = Carrera.query.get_or_404(carrera_id)
    db.session.delete(carrera)
    db.session.commit()
    return jsonify({'message': 'Carrera eliminada'}), 200
