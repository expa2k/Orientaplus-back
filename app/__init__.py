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
    from app.routes.oferta_routes import oferta_bp
    from app.routes.test_routes import test_bp
    from app.routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(oferta_bp, url_prefix='/api/oferta')
    app.register_blueprint(test_bp, url_prefix='/api/test')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    with app.app_context():
        db.create_all()
        _seed_admin()
        _seed_areas_y_carreras()
        _seed_preguntas()

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


def _seed_areas_y_carreras():
    from app.models.area_profesional import AreaProfesional
    from app.models.carrera import Carrera

    if AreaProfesional.query.first():
        return

    areas_data = [
        {
            'nombre': 'Realista',
            'codigo_riasec': 'R',
            'descripcion': 'Trabajo práctico, manual, mecánico. Prefieren actividades al aire libre y el uso de herramientas.',
            'icono': 'build',
            'carreras': [
                {'nombre': 'Ingeniería Mecánica', 'perfil_riasec': 'RIE', 'descripcion': 'Diseño y mantenimiento de sistemas mecánicos.', 'campo_laboral': 'Industria automotriz, manufactura, energía'},
                {'nombre': 'Ingeniería Civil', 'perfil_riasec': 'RIC', 'descripcion': 'Diseño y construcción de infraestructura.', 'campo_laboral': 'Construcción, gobierno, consultoría'},
                {'nombre': 'Agronomía', 'perfil_riasec': 'RIS', 'descripcion': 'Producción agrícola y gestión de recursos naturales.', 'campo_laboral': 'Agroindustria, gobierno, investigación'},
            ]
        },
        {
            'nombre': 'Investigador',
            'codigo_riasec': 'I',
            'descripcion': 'Pensamiento analítico, científico, investigación. Disfrutan resolver problemas complejos.',
            'icono': 'science',
            'carreras': [
                {'nombre': 'Medicina', 'perfil_riasec': 'ISR', 'descripcion': 'Diagnóstico y tratamiento de enfermedades.', 'campo_laboral': 'Hospitales, clínicas, investigación médica'},
                {'nombre': 'Biología', 'perfil_riasec': 'IRA', 'descripcion': 'Estudio de los seres vivos y ecosistemas.', 'campo_laboral': 'Laboratorios, medio ambiente, docencia'},
                {'nombre': 'Ciencia de Datos', 'perfil_riasec': 'ICR', 'descripcion': 'Análisis de grandes volúmenes de datos para generar conocimiento.', 'campo_laboral': 'Tecnología, finanzas, salud, gobierno'},
            ]
        },
        {
            'nombre': 'Artístico',
            'codigo_riasec': 'A',
            'descripcion': 'Creatividad, expresión, originalidad. Valoran la estética y la innovación.',
            'icono': 'palette',
            'carreras': [
                {'nombre': 'Diseño Gráfico', 'perfil_riasec': 'AEI', 'descripcion': 'Comunicación visual y diseño de medios.', 'campo_laboral': 'Agencias, medios digitales, freelance'},
                {'nombre': 'Arquitectura', 'perfil_riasec': 'AIR', 'descripcion': 'Diseño de espacios y edificaciones.', 'campo_laboral': 'Despachos, construcción, gobierno'},
                {'nombre': 'Comunicación', 'perfil_riasec': 'AES', 'descripcion': 'Producción de contenido y medios de comunicación.', 'campo_laboral': 'Medios, relaciones públicas, marketing'},
            ]
        },
        {
            'nombre': 'Social',
            'codigo_riasec': 'S',
            'descripcion': 'Ayudar, enseñar, servir a otros. Disfrutan el contacto humano y el trabajo en equipo.',
            'icono': 'groups',
            'carreras': [
                {'nombre': 'Psicología', 'perfil_riasec': 'SIA', 'descripcion': 'Estudio del comportamiento humano y salud mental.', 'campo_laboral': 'Clínicas, escuelas, empresas, gobierno'},
                {'nombre': 'Educación', 'perfil_riasec': 'SAE', 'descripcion': 'Formación y desarrollo de procesos de enseñanza.', 'campo_laboral': 'Escuelas, universidades, capacitación'},
                {'nombre': 'Trabajo Social', 'perfil_riasec': 'SEC', 'descripcion': 'Intervención social para el bienestar comunitario.', 'campo_laboral': 'Gobierno, ONGs, instituciones sociales'},
            ]
        },
        {
            'nombre': 'Emprendedor',
            'codigo_riasec': 'E',
            'descripcion': 'Liderazgo, persuasión, toma de decisiones. Les gusta dirigir proyectos y equipos.',
            'icono': 'trending_up',
            'carreras': [
                {'nombre': 'Administración de Empresas', 'perfil_riasec': 'ECS', 'descripcion': 'Gestión y dirección de organizaciones.', 'campo_laboral': 'Empresas, emprendimiento, consultoría'},
                {'nombre': 'Derecho', 'perfil_riasec': 'ESI', 'descripcion': 'Estudio de leyes y sistema jurídico.', 'campo_laboral': 'Despachos jurídicos, gobierno, sector privado'},
                {'nombre': 'Marketing', 'perfil_riasec': 'EAS', 'descripcion': 'Estrategias de mercadotecnia y posicionamiento.', 'campo_laboral': 'Agencias, empresas, comercio digital'},
            ]
        },
        {
            'nombre': 'Convencional',
            'codigo_riasec': 'C',
            'descripcion': 'Orden, datos, procedimientos, atención al detalle. Prefieren ambientes estructurados.',
            'icono': 'calculate',
            'carreras': [
                {'nombre': 'Contaduría Pública', 'perfil_riasec': 'CEI', 'descripcion': 'Gestión contable y financiera.', 'campo_laboral': 'Despachos contables, empresas, gobierno'},
                {'nombre': 'Ingeniería en Sistemas', 'perfil_riasec': 'CIR', 'descripcion': 'Desarrollo de software y sistemas computacionales.', 'campo_laboral': 'Tecnología, banca, telecomunicaciones'},
                {'nombre': 'Economía', 'perfil_riasec': 'CES', 'descripcion': 'Análisis de mercados y política económica.', 'campo_laboral': 'Banca, gobierno, organismos internacionales'},
            ]
        }
    ]

    for area_data in areas_data:
        carreras_data = area_data.pop('carreras')
        area = AreaProfesional(**area_data)
        db.session.add(area)
        db.session.flush()

        for carrera_data in carreras_data:
            carrera = Carrera(area_id=area.id, **carrera_data)
            db.session.add(carrera)

    db.session.commit()


def _seed_preguntas():
    from app.models.pregunta_test import PreguntaTest

    if PreguntaTest.query.first():
        return

    preguntas = [
        {'bloque': 1, 'tipo': 'likert', 'texto': 'Disfruto trabajar con herramientas, máquinas o hacer actividades manuales.', 'dimension_riasec': 'R', 'orden': 1},
        {'bloque': 1, 'tipo': 'likert', 'texto': 'Me siento cómodo realizando tareas físicas o al aire libre.', 'dimension_riasec': 'R', 'orden': 2},
        {'bloque': 1, 'tipo': 'likert', 'texto': 'Me gusta investigar, analizar datos y resolver problemas complejos.', 'dimension_riasec': 'I', 'orden': 3},
        {'bloque': 1, 'tipo': 'likert', 'texto': 'Disfruto leer artículos científicos o aprender sobre descubrimientos.', 'dimension_riasec': 'I', 'orden': 4},
        {'bloque': 1, 'tipo': 'likert', 'texto': 'Disfruto expresarme a través del arte, la música, la escritura o el diseño.', 'dimension_riasec': 'A', 'orden': 5},
        {'bloque': 1, 'tipo': 'likert', 'texto': 'Prefiero trabajar en ambientes donde pueda usar mi creatividad.', 'dimension_riasec': 'A', 'orden': 6},
        {'bloque': 1, 'tipo': 'likert', 'texto': 'Me gusta ayudar a otros, enseñar o trabajar en equipo.', 'dimension_riasec': 'S', 'orden': 7},
        {'bloque': 1, 'tipo': 'likert', 'texto': 'Me interesa contribuir al bienestar de las personas.', 'dimension_riasec': 'S', 'orden': 8},
        {'bloque': 1, 'tipo': 'likert', 'texto': 'Me gusta liderar proyectos, tomar decisiones y convencer a otros.', 'dimension_riasec': 'E', 'orden': 9},
        {'bloque': 1, 'tipo': 'likert', 'texto': 'Me veo dirigiendo mi propio negocio o equipo de trabajo.', 'dimension_riasec': 'E', 'orden': 10},
        {'bloque': 1, 'tipo': 'likert', 'texto': 'Me siento cómodo siguiendo procedimientos, organizando información y trabajando con números.', 'dimension_riasec': 'C', 'orden': 11},
        {'bloque': 1, 'tipo': 'likert', 'texto': 'Prefiero ambientes de trabajo estructurados y organizados.', 'dimension_riasec': 'C', 'orden': 12},

        {'bloque': 2, 'tipo': 'likert', 'texto': 'Me gustaría aprender a operar maquinaria pesada o equipos especializados.', 'dimension_riasec': 'R', 'orden': 1},
        {'bloque': 2, 'tipo': 'likert', 'texto': 'Disfruto armar, desarmar o reparar cosas.', 'dimension_riasec': 'R', 'orden': 2},
        {'bloque': 2, 'tipo': 'likert', 'texto': 'Me atraen las actividades relacionadas con la naturaleza o la agricultura.', 'dimension_riasec': 'R', 'orden': 3},
        {'bloque': 2, 'tipo': 'likert', 'texto': 'Me gustaría participar en un proyecto de investigación científica.', 'dimension_riasec': 'I', 'orden': 4},
        {'bloque': 2, 'tipo': 'likert', 'texto': 'Disfruto resolver acertijos, rompecabezas lógicos o ecuaciones.', 'dimension_riasec': 'I', 'orden': 5},
        {'bloque': 2, 'tipo': 'likert', 'texto': 'Me interesa entender cómo funcionan las cosas a nivel profundo.', 'dimension_riasec': 'I', 'orden': 6},
        {'bloque': 2, 'tipo': 'likert', 'texto': 'Me gustaría dedicarme profesionalmente a una actividad creativa.', 'dimension_riasec': 'A', 'orden': 7},
        {'bloque': 2, 'tipo': 'likert', 'texto': 'Valoro más la originalidad que seguir reglas establecidas.', 'dimension_riasec': 'A', 'orden': 8},
        {'bloque': 2, 'tipo': 'likert', 'texto': 'Me inspiro fácilmente al ver obras de arte, películas o diseños innovadores.', 'dimension_riasec': 'A', 'orden': 9},
        {'bloque': 2, 'tipo': 'likert', 'texto': 'Me sentiría bien trabajando en una organización que ayude a comunidades.', 'dimension_riasec': 'S', 'orden': 10},
        {'bloque': 2, 'tipo': 'likert', 'texto': 'Tengo facilidad para escuchar y aconsejar a otras personas.', 'dimension_riasec': 'S', 'orden': 11},
        {'bloque': 2, 'tipo': 'likert', 'texto': 'Me gustaría dedicarme a la enseñanza o la capacitación.', 'dimension_riasec': 'S', 'orden': 12},
        {'bloque': 2, 'tipo': 'likert', 'texto': 'Me gusta competir y ser el mejor en lo que hago.', 'dimension_riasec': 'E', 'orden': 13},
        {'bloque': 2, 'tipo': 'likert', 'texto': 'Disfruto negociar, vender ideas y convencer a los demás.', 'dimension_riasec': 'E', 'orden': 14},
        {'bloque': 2, 'tipo': 'likert', 'texto': 'Me atrae la idea de generar ingresos y manejar recursos financieros.', 'dimension_riasec': 'E', 'orden': 15},
        {'bloque': 2, 'tipo': 'likert', 'texto': 'Me gusta clasificar, ordenar y sistematizar información.', 'dimension_riasec': 'C', 'orden': 16},
        {'bloque': 2, 'tipo': 'likert', 'texto': 'Disfruto trabajar con hojas de cálculo, bases de datos o archivos.', 'dimension_riasec': 'C', 'orden': 17},
        {'bloque': 2, 'tipo': 'likert', 'texto': 'Me siento cómodo siguiendo instrucciones detalladas paso a paso.', 'dimension_riasec': 'C', 'orden': 18},
    ]

    for p in preguntas:
        db.session.add(PreguntaTest(**p))

    db.session.commit()
