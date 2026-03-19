from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.pregunta_test import PreguntaTest
from app.models.sesion_test import SesionTest
from app.models.respuesta_test import RespuestaTest
from app.models.carrera import Carrera
from app.services.motor_adaptativo import (
    calcular_vector_riasec,
    decidir_siguiente_bloque,
    obtener_top_dimensiones,
    calcular_afinidad_carrera
)
from app.extensions import db

test_bp = Blueprint('test', __name__)


@test_bp.route('/iniciar', methods=['POST'])
@jwt_required()
def iniciar_test():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    forzar_nuevo = data.get('forzar_nuevo', False)

    sesion_activa = SesionTest.query.filter_by(
        usuario_id=user_id, estado='en_progreso'
    ).first()

    if sesion_activa and not forzar_nuevo:
        preguntas = PreguntaTest.query.filter_by(
            bloque=sesion_activa.bloque_actual, activo=True
        ).order_by(PreguntaTest.orden).all()

        respondidas = [r.pregunta_id for r in sesion_activa.respuestas]
        respuestas_guardadas = {r.pregunta_id: r.valor for r in sesion_activa.respuestas}

        return jsonify({
            'sesion': sesion_activa.to_dict(),
            'preguntas': [p.to_dict() for p in preguntas],
            'respondidas': respondidas,
            'respuestas_guardadas': respuestas_guardadas,
            'tiene_sesion_activa': True,
            'mensaje': 'Tienes un test en progreso'
        }), 200

    if sesion_activa and forzar_nuevo:
        sesion_activa.estado = 'abandonada'
        sesion_activa.fecha_fin = datetime.utcnow()
        db.session.commit()

    sesion = SesionTest(
        usuario_id=user_id,
        estado='en_progreso',
        bloque_actual=1,
        vector_riasec={'R': 0, 'I': 0, 'A': 0, 'S': 0, 'E': 0, 'C': 0}
    )
    db.session.add(sesion)
    db.session.commit()

    preguntas = PreguntaTest.query.filter_by(
        bloque=1, activo=True
    ).order_by(PreguntaTest.orden).all()

    return jsonify({
        'sesion': sesion.to_dict(),
        'preguntas': [p.to_dict() for p in preguntas],
        'respondidas': [],
        'tiene_sesion_activa': False,
        'mensaje': 'Test iniciado'
    }), 201


@test_bp.route('/abandonar/<int:sesion_id>', methods=['POST'])
@jwt_required()
def abandonar_test(sesion_id):
    user_id = get_jwt_identity()

    sesion = SesionTest.query.get(sesion_id)
    if not sesion or str(sesion.usuario_id) != str(user_id):
        return jsonify({'message': 'Sesion no encontrada'}), 404

    if sesion.estado != 'en_progreso':
        return jsonify({'message': 'Esta sesion ya fue cerrada'}), 400

    sesion.estado = 'abandonada'
    sesion.fecha_fin = datetime.utcnow()
    db.session.commit()

    return jsonify({'message': 'Sesion abandonada'}), 200


@test_bp.route('/responder', methods=['POST'])
@jwt_required()
def responder():
    user_id = get_jwt_identity()
    data = request.get_json()

    sesion_id = data.get('sesion_id')
    respuestas_data = data.get('respuestas', [])

    if not sesion_id or not respuestas_data:
        return jsonify({'message': 'Sesión y respuestas son requeridas'}), 400

    sesion = SesionTest.query.get(sesion_id)
    if not sesion or str(sesion.usuario_id) != str(user_id):
        return jsonify({'message': 'Sesión no encontrada'}), 404

    if sesion.estado != 'en_progreso':
        return jsonify({'message': 'Esta sesión ya fue completada'}), 400

    for resp in respuestas_data:
        pregunta_id = resp.get('pregunta_id')
        valor = str(resp.get('valor', ''))

        if not pregunta_id or not valor:
            continue

        existente = RespuestaTest.query.filter_by(
            sesion_id=sesion_id, pregunta_id=pregunta_id
        ).first()

        if existente:
            existente.valor = valor
        else:
            nueva = RespuestaTest(
                sesion_id=sesion_id,
                pregunta_id=pregunta_id,
                valor=valor
            )
            db.session.add(nueva)

    db.session.flush()

    todas_respuestas = RespuestaTest.query.filter_by(sesion_id=sesion_id).all()
    pares = []
    for r in todas_respuestas:
        pregunta = PreguntaTest.query.get(r.pregunta_id)
        if pregunta:
            pares.append((pregunta.dimension_riasec, r.valor))

    vector = calcular_vector_riasec(pares)
    sesion.vector_riasec = vector

    db.session.commit()

    return jsonify({
        'sesion': sesion.to_dict(),
        'vector_riasec': vector,
        'total_respuestas': len(todas_respuestas)
    }), 200


@test_bp.route('/siguiente/<int:sesion_id>', methods=['GET'])
@jwt_required()
def siguiente_bloque(sesion_id):
    user_id = get_jwt_identity()

    sesion = SesionTest.query.get(sesion_id)
    if not sesion or str(sesion.usuario_id) != str(user_id):
        return jsonify({'message': 'Sesión no encontrada'}), 404

    if sesion.estado != 'en_progreso':
        return jsonify({'message': 'Esta sesión ya fue completada'}), 400

    decision = decidir_siguiente_bloque(
        sesion.vector_riasec or {},
        sesion.bloque_actual
    )

    if decision['accion'] == 'finalizar':
        return jsonify({
            'accion': 'finalizar',
            'vector_riasec': sesion.vector_riasec,
            'mensaje': 'Test listo para finalizar'
        }), 200

    siguiente = decision['siguiente_bloque']
    dimensiones_foco = decision['dimensiones_foco']

    query = PreguntaTest.query.filter_by(bloque=siguiente, activo=True)
    if dimensiones_foco:
        query = query.filter(PreguntaTest.dimension_riasec.in_(dimensiones_foco))

    preguntas = query.order_by(PreguntaTest.orden).all()

    sesion.bloque_actual = siguiente
    db.session.commit()

    return jsonify({
        'accion': 'continuar',
        'sesion': sesion.to_dict(),
        'preguntas': [p.to_dict() for p in preguntas],
        'dimensiones_foco': dimensiones_foco,
        'perfil_claro': decision['perfil_claro']
    }), 200


@test_bp.route('/finalizar/<int:sesion_id>', methods=['POST'])
@jwt_required()
def finalizar_test(sesion_id):
    user_id = get_jwt_identity()

    sesion = SesionTest.query.get(sesion_id)
    if not sesion or str(sesion.usuario_id) != str(user_id):
        return jsonify({'message': 'Sesión no encontrada'}), 404

    if sesion.estado != 'en_progreso':
        return jsonify({'message': 'Esta sesión ya fue completada'}), 400

    vector = sesion.vector_riasec or {}
    top_dims = obtener_top_dimensiones(vector, n=3)

    carreras = Carrera.query.filter_by(activo=True).all()
    recomendaciones = []

    for carrera in carreras:
        afinidad = calcular_afinidad_carrera(vector, carrera.perfil_riasec)
        recomendaciones.append({
            'carrera': carrera.to_dict(),
            'afinidad': afinidad
        })

    recomendaciones.sort(key=lambda x: x['afinidad'], reverse=True)

    sesion.estado = 'completada'
    sesion.fecha_fin = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'sesion': sesion.to_dict(),
        'vector_riasec': vector,
        'top_dimensiones': [{'dimension': d, 'score': s} for d, s in top_dims],
        'recomendaciones': recomendaciones[:10],
        'mensaje': 'Test completado exitosamente'
    }), 200


@test_bp.route('/historial', methods=['GET'])
@jwt_required()
def historial():
    user_id = get_jwt_identity()

    sesiones = SesionTest.query.filter_by(
        usuario_id=user_id
    ).order_by(SesionTest.fecha_inicio.desc()).all()

    return jsonify([s.to_dict() for s in sesiones]), 200


@test_bp.route('/sesion/<int:sesion_id>', methods=['GET'])
@jwt_required()
def get_sesion(sesion_id):
    user_id = get_jwt_identity()

    sesion = SesionTest.query.get(sesion_id)
    if not sesion or str(sesion.usuario_id) != str(user_id):
        return jsonify({'message': 'Sesión no encontrada'}), 404

    return jsonify(sesion.to_dict()), 200


@test_bp.route('/preguntas', methods=['GET'])
@jwt_required()
def get_preguntas():
    bloque = request.args.get('bloque', type=int)
    query = PreguntaTest.query.filter_by(activo=True)
    if bloque:
        query = query.filter_by(bloque=bloque)
    preguntas = query.order_by(PreguntaTest.bloque, PreguntaTest.orden).all()
    return jsonify([p.to_dict() for p in preguntas]), 200
