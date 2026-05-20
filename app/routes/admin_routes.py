from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.models.sesion_test import SesionTest
from app.models.respuesta_test import RespuestaTest
from app.models.pregunta_test import PreguntaTest
from app.models.usuario import Usuario
from app.services.motor_adaptativo import obtener_top_dimensiones, calcular_afinidad_carrera
from app.models.carrera import Carrera
from functools import wraps

admin_bp = Blueprint('admin', __name__)


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        user_data = claims.get('user', {})
        if user_data.get('rol') != 'admin':
            return jsonify({'message': 'Acceso denegado'}), 403
        return fn(*args, **kwargs)
    return wrapper


@admin_bp.route('/resultados', methods=['GET'])
@admin_required
def get_resultados():
    estado = request.args.get('estado')
    query = SesionTest.query

    if estado:
        query = query.filter_by(estado=estado)

    sesiones = query.order_by(SesionTest.fecha_inicio.desc()).all()

    resultados = []
    for sesion in sesiones:
        usuario = Usuario.query.get(sesion.usuario_id)
        vector = sesion.vector_riasec or {}
        top_dims = obtener_top_dimensiones(vector, n=3) if vector else []

        resultados.append({
            'sesion': sesion.to_dict(),
            'estudiante': {
                'id': usuario.id,
                'nombre': f'{usuario.nombre} {usuario.apellido}',
                'correo': usuario.correo
            } if usuario else None,
            'top_dimensiones': [{'dimension': d, 'score': s} for d, s in top_dims],
            'perfil_dominante': top_dims[0][0] if top_dims else None
        })

    return jsonify(resultados), 200


@admin_bp.route('/resultados/<int:sesion_id>', methods=['GET'])
@admin_required
def get_resultado_detalle(sesion_id):
    sesion = SesionTest.query.get_or_404(sesion_id)
    usuario = Usuario.query.get(sesion.usuario_id)
    vector = sesion.vector_riasec or {}
    top_dims = obtener_top_dimensiones(vector, n=3) if vector else []

    respuestas = RespuestaTest.query.filter_by(sesion_id=sesion_id).all()
    respuestas_detalle = []
    for r in respuestas:
        pregunta = PreguntaTest.query.get(r.pregunta_id)
        respuestas_detalle.append({
            'pregunta_id': r.pregunta_id,
            'texto': pregunta.texto if pregunta else '',
            'dimension': pregunta.dimension_riasec if pregunta else '',
            'valor': r.valor,
            'fecha': r.fecha_respuesta.isoformat() if r.fecha_respuesta else None
        })

    # Prioridad a las recomendaciones guardadas
    if sesion.recomendaciones:
        recomendaciones_finales = sesion.recomendaciones
    else:
        carreras = Carrera.query.filter_by(activo=True).all()
        recomendaciones_finales = []
        for carrera in carreras:
            afinidad = calcular_afinidad_carrera(vector, carrera.perfil_riasec)
            recomendaciones_finales.append({
                'carrera': carrera.to_dict(),
                'afinidad': afinidad
            })
        recomendaciones_finales.sort(key=lambda x: x['afinidad'], reverse=True)
        recomendaciones_finales = recomendaciones_finales[:10]

    return jsonify({
        'sesion': sesion.to_dict(),
        'estudiante': {
            'id': usuario.id,
            'nombre': f'{usuario.nombre} {usuario.apellido}',
            'correo': usuario.correo
        } if usuario else None,
        'vector_riasec': vector,
        'top_dimensiones': [{'dimension': d, 'score': s} for d, s in top_dims],
        'respuestas': respuestas_detalle,
        'recomendaciones': recomendaciones_finales
    }), 200


@admin_bp.route('/estadisticas', methods=['GET'])
@admin_required
def get_estadisticas():
    from datetime import datetime, timedelta
    from collections import Counter

    total_sesiones = SesionTest.query.count()
    completadas = SesionTest.query.filter_by(estado='completada').count()
    en_progreso = SesionTest.query.filter_by(estado='en_progreso').count()
    abandonadas = SesionTest.query.filter_by(estado='abandonada').count()

    sesiones_completadas = SesionTest.query.filter_by(estado='completada').all()

    distribucion_riasec = {'R': 0, 'I': 0, 'A': 0, 'S': 0, 'E': 0, 'C': 0}
    suma_vector = {'R': 0.0, 'I': 0.0, 'A': 0.0, 'S': 0.0, 'E': 0.0, 'C': 0.0}
    duraciones = []
    carrera_counter = Counter()

    for sesion in sesiones_completadas:
        vector = sesion.vector_riasec or {}
        if vector:
            top = obtener_top_dimensiones(vector, n=1)
            if top:
                distribucion_riasec[top[0][0]] += 1
            for dim in 'RIASEC':
                suma_vector[dim] += vector.get(dim, 0.0)

        if sesion.fecha_inicio and sesion.fecha_fin:
            delta = (sesion.fecha_fin - sesion.fecha_inicio).total_seconds() / 60
            if 0 < delta < 120:
                duraciones.append(delta)

        if sesion.recomendaciones:
            for rec in sesion.recomendaciones:
                nombre = rec.get('carrera', {}).get('nombre')
                if nombre:
                    carrera_counter[nombre] += 1

    n = len(sesiones_completadas)
    vector_promedio = {dim: round(suma_vector[dim] / n, 2) for dim in 'RIASEC'} if n > 0 else {dim: 0.0 for dim in 'RIASEC'}
    tiempo_promedio = round(sum(duraciones) / len(duraciones), 1) if duraciones else 0

    carreras_top = [{'nombre': nombre, 'frecuencia': freq} for nombre, freq in carrera_counter.most_common(5)]

    ahora = datetime.utcnow()
    tests_por_mes = []
    for i in range(5, -1, -1):
        fecha_ref = ahora - timedelta(days=30 * i)
        mes_inicio = fecha_ref.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if mes_inicio.month == 12:
            mes_fin = mes_inicio.replace(year=mes_inicio.year + 1, month=1)
        else:
            mes_fin = mes_inicio.replace(month=mes_inicio.month + 1)
        count = SesionTest.query.filter(
            SesionTest.estado == 'completada',
            SesionTest.fecha_fin >= mes_inicio,
            SesionTest.fecha_fin < mes_fin
        ).count()
        tests_por_mes.append({
            'mes': mes_inicio.strftime('%b %Y'),
            'total': count
        })

    return jsonify({
        'total_sesiones': total_sesiones,
        'completadas': completadas,
        'en_progreso': en_progreso,
        'abandonadas': abandonadas,
        'tasa_completado': round((completadas / total_sesiones * 100), 1) if total_sesiones > 0 else 0,
        'distribucion_perfiles': distribucion_riasec,
        'vector_promedio': vector_promedio,
        'tiempo_promedio_minutos': tiempo_promedio,
        'carreras_top': carreras_top,
        'tests_por_mes': tests_por_mes
    }), 200
