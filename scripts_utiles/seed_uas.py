import sys
import os

from app import create_app, db
from app.models.area_profesional import AreaProfesional
from app.models.carrera import Carrera

app = create_app()

area_riasec_map = {
    "ARQUITECTURA, DISEÑO Y URBANISMO": "ARE",
    "CIENCIAS AGROPECUARIAS": "IRE",
    "CIENCIAS DE LA EDUCACIÓN Y HUMANIDADES": "SEC",
    "CIENCIAS DE LA SALUD": "SIR",
    "CIENCIAS ECONÓMICO ADMINISTRATIVAS": "ESC",
    "CIENCIAS NATURALES Y EXACTAS": "IRC",
    "CIENCIAS SOCIALES": "SIA",
    "INGENIERÍA Y TECNOLOGÍA": "RIE"
}

uas_data = {
    "ARQUITECTURA, DISEÑO Y URBANISMO": [
        ("Lic. en Arquitectura", "ARE", "Diseño, planificación y construcción de espacios habitables y edificaciones."),
        ("Lic. en Diseño de Interiores y Ambientación", "AES", "Creación y optimización funcional y estética de espacios interiores."),
        ("Lic. en Diseño Gráfico Empresarial", "AEC", "Comunicación visual y creación de identidad gráfica para empresas."),
        ("Lic. en Diseño Industrial", "ARI", "Creación de productos y objetos utilitarios innovadores y ergonómicos."),
        ("Lic. en Diseño Urbano y del Paisaje", "ARE", "Planificación de espacios públicos y áreas verdes sostenibles."),
        ("Lic. en Diseño y Arte Multimedia", "AIE", "Creación de contenido digital interactivo, audiovisual y animación.")
    ],
    "CIENCIAS AGROPECUARIAS": [
        ("Lic. en Biología Acuícola", "IRE", "Estudio y cultivo de especies acuáticas comerciales y preservación."),
        ("Lic. en Biología Pesquera", "IRE", "Administración e investigación de los recursos pesqueros y marítimos."),
        ("Lic. en Gestión de Zona Costera", "REC", "Manejo sustentable y administración de ecosistemas y recursos costeros."),
        ("Lic. en Ingeniería Agronómica", "RIE", "Optimización de la producción agrícola, suelos y cultivos."),
        ("Lic. en Ingeniería en Agrobiotecnología", "IRE", "Aplicación de tecnología biológica para mejorar cultivos y alimentos."),
        ("Lic. en Ingeniería en Biotecnología Acuática", "IRE", "Uso de biotecnología aplicada a organismos acuáticos comerciales."),
        ("Lic. en Medicina Veterinaria y Zootecnia", "RIS", "Cuidado, salud y producción de animales domésticos y de granja.")
    ],
    "CIENCIAS DE LA EDUCACIÓN Y HUMANIDADES": [
        ("Lic. en Artes Escénicas", "ASE", "Actuación, danza, teatro y expresión corporal frente a audiencias."),
        ("Lic. en Artes Visuales", "ASI", "Creación de obras artísticas a través de pintura, escultura y medios visuales."),
        ("Lic. en Ciencias de la Educación", "SEC", "Investigación, planeación y evaluación de procesos de enseñanza."),
        ("Lic. en Educación Artística", "SAE", "Enseñanza de disciplinas artísticas en instituciones educativas."),
        ("Lic. en Educación Deportiva", "SRE", "Enseñanza y promoción de la cultura física y deportes."),
        ("Lic. en Educación Física", "SRE", "Instrucción de acondicionamiento físico y salud corporal."),
        ("Lic. en Educación Media en el Área de Español", "SEC", "Docencia especializada en lenguaje y gramática española para jóvenes."),
        ("Lic. en Enseñanza del Idioma Inglés", "SEC", "Enseñanza didáctica y profesional del idioma inglés."),
        ("Lic. en Filosofía", "IAS", "Análisis crítico, reflexión lógica y estudio del pensamiento humano."),
        ("Lic. en Fotografía y Producción de Video", "ARE", "Captura, edición y producción técnica de imágenes y material audiovisual."),
        ("Lic. en Lengua y Literatura Hispánicas", "AIS", "Estudio profundo de la gramática, escritura y literatura en español."),
        ("Lic. en Música", "ASE", "Composición, interpretación y estudio técnico de piezas y teoría musical."),
        ("Lic. en Música Popular Contemporánea", "ASE", "Creación e interpretación de géneros musicales modernos."),
        ("Lic. en Psicología", "SIA", "Estudio del comportamiento humano, salud mental y procesos cognitivos."),
        ("Lic. en Psicopedagogía", "SEC", "Atención a problemas de aprendizaje y estrategias didácticas personalizadas.")
    ],
    "CIENCIAS DE LA SALUD": [
        ("Lic. en Actividad Física para la Salud", "SRE", "Rehabilitación y mejora de la salud mediante prescripción de ejercicio."),
        ("Lic. en Biomedicina", "IRS", "Investigación biológica aplicada a problemas médicos y enfermedades."),
        ("Lic. en Cirujano Dentista", "SIR", "Diagnóstico, tratamiento y prevención de enfermedades bucodentales."),
        ("Lic. en Citotecnología", "IRC", "Análisis celular en laboratorio para detectar anomalías y enfermedades."),
        ("Lic. en Enfermería", "SIC", "Atención médica, cuidado y asistencia directa a pacientes y comunidades."),
        ("Lic. en Entrenamiento Deportivo", "SRE", "Preparación física y táctica para atletas de alto rendimiento."),
        ("Lic. en Fisioterapia", "SIR", "Rehabilitación física y tratamiento de lesiones mediante terapias."),
        ("Lic. en Gerontología", "SIC", "Estudio médico social y cuidado especializado para personas mayores."),
        ("Lic. en Imagenología", "RCI", "Uso de tecnología radiológica y escáneres para diagnósticos médicos."),
        ("Lic. en Médico General", "IRS", "Prevención, diagnóstico y tratamiento integral de enfermedades humanas."),
        ("Lic. en Nutrición", "SIE", "Diseño de planes alimenticios y fomento de hábitos de salud dietética."),
        ("Lic. en Optometría", "SIR", "Evaluación visual y prescripción para corregir problemas oculares."),
        ("Lic. en Podología", "SIR", "Diagnóstico y tratamiento clínico de enfermedades de los pies."),
        ("Lic. en Químico Farmacéutico Biólogo", "IRC", "Análisis clínicos de laboratorio clínico y desarrollo de medicamentos.")
    ],
    "CIENCIAS ECONÓMICO ADMINISTRATIVAS": [
        ("Lic. en Administración de Empresas", "ESC", "Dirección, organización y gestión de recursos en corporativos."),
        ("Lic. en Administración de Recursos Humanos", "ESC", "Gestión, contratación y desarrollo del talento en organizaciones."),
        ("Lic. en Comercio Internacional", "ECS", "Gestión de importaciones, exportaciones y transacciones aduaneras."),
        ("Lic. en Contaduría Pública", "CES", "Control fiscal, contable y auditoría de finanzas corporativas."),
        ("Lic. en Desarrollo Empresarial y de Negocios", "ECS", "Creación de estrategias comerciales y crecimiento de nuevas empresas."),
        ("Lic. en Economía", "IEC", "Análisis de mercados financieros, estadística y políticas de distribución."),
        ("Lic. en Gastronomía", "RAE", "Preparación técnica, diseño culinario y gestión de restaurantes."),
        ("Lic. en Ingeniería en Inteligencia y Analítica de Negocios", "CEI", "Análisis de datos (Big Data) para optimizar decisiones corporativas."),
        ("Lic. en Ingeniería Financiera", "CEI", "Diseño de estrategias de inversión, bolsas de valores y matemáticas financieras."),
        ("Lic. en Mercadotecnia", "EAC", "Estrategias de ventas, investigación de mercado y publicidad comercial."),
        ("Lic. en Negocios Agrotecnológicos", "ECR", "Comercialización y rentabilidad de productos e insumos de la agricultura."),
        ("Lic. en Negocios Internacionales", "ECS", "Dirección de empresas en mercados globales y multinacionales."),
        ("Lic. en Negocios y Comercio Internacional", "ECS", "Operación logística, aduanal y gestión comercial global."),
        ("Lic. en Relaciones Comerciales Internacionales", "ECS", "Negociación de tratados, acuerdos y diplomacia mercantil."),
        ("Lic. en Turismo", "ESC", "Gestión de servicios de viaje, hotelería y experiencias recreativas.")
    ],
    "CIENCIAS NATURALES Y EXACTAS": [
        ("Lic. en Astronomía", "IR", "Investigación física y matemática del universo, astros y galaxias."),
        ("Lic. en Biología", "IR", "Estudio científico de los seres vivos, genética y ecosistemas."),
        ("Lic. en Física", "IRC", "Estudio de las leyes fundamentales de la energía, materia y el espacio."),
        ("Lic. en Matemáticas", "ICR", "Desarrollo de teorías lógicas abstractas, cálculo y resolución de teoremas.")
    ],
    "CIENCIAS SOCIALES": [
        ("Lic. en Antropología Social", "ISA", "Investigación académica de culturas humanas, tradiciones y sociedades."),
        ("Lic. en Ciencias de la Comunicación", "EAS", "Producción de mensajes masivos, periodismo, radio y relaciones públicas."),
        ("Lic. en Criminalística y Ciencias Forenses", "IRC", "Análisis de escenas del crimen y evidencias mediante métodos científicos."),
        ("Lic. en Criminología", "IES", "Estudio de las causas del delito, psicología criminal y prevención penal."),
        ("Lic. en Derecho", "ESC", "Gestión de procesos legales, aplicación de leyes y defensa jurídica."),
        ("Lic. en Estudios Internacionales", "ESC", "Análisis geopolítico, diplomacia y relaciones entre distintas naciones."),
        ("Lic. en Historia", "IA", "Investigación documental y análisis crítico de hechos del pasado."),
        ("Lic. en Políticas Públicas", "ESI", "Diseño de estrategias gubernamentales y soluciones a problemas sociales."),
        ("Lic. en Trabajo Social", "SEC", "Intervención y apoyo directo a comunidades y grupos vulnerables.")
    ],
    "INGENIERÍA Y TECNOLOGÍA": [
        ("Lic. en Biotecnología Genómica", "IRC", "Manipulación genética y molecular para avances biomédicos y tecnológicos."),
        ("Lic. en Geoinformática", "IRC", "Procesamiento de datos satelitales y sistemas de información geográfica."),
        ("Lic. en Informática", "ICR", "Administración de redes, bases de datos y soporte tecnológico."),
        ("Lic. en Ingeniería Aeronáutica", "RIC", "Diseño, fabricación y mantenimiento de aeronaves y sistemas de vuelo."),
        ("Lic. en Ingeniería Bioquímica", "IRC", "Ingeniería aplicada a procesos biológicos industriales y alimentarios."),
        ("Lic. en Ingeniería Civil", "RIE", "Diseño estructural y construcción de carreteras, puentes y edificios."),
        ("Lic. en Ingeniería de Software", "ICR", "Arquitectura, programación y desarrollo estructurado de programas de computadora."),
        ("Lic. en Ingeniería Electrónica", "RIE", "Diseño de circuitos, microprocesadores y automatización de hardware."),
        ("Lic. en Ingeniería en Ciencia de Datos", "ICR", "Creación de algoritmos ML y análisis estadístico de conjuntos masivos de datos (Big Data)."),
        ("Lic. en Ingeniería en Energías Renovables", "RIE", "Diseño de tecnologías eólicas, solares y limpias para generación comercial."),
        ("Lic. en Ingeniería en Minas", "RE", "Extracción tecnificada de minerales terrestres y diseño de túneles."),
        ("Lic. en Ingeniería en Nanotecnología y Energías Renovables", "IRE", "Creación de materiales a nivel atómico para mejorar eficiencia energética."),
        ("Lic. en Ingeniería en Procesos Industriales", "RCE", "Optimización de eficiencia operacional en fábricas y calidad de manufactura."),
        ("Lic. en Ingeniería en Sistemas de Información", "ICR", "Diseño y administración de arquitectura tecnológica para empresas e instituciones."),
        ("Lic. en Ingeniería Geodésica", "RIC", "Medición avanzada y topografía satelital de la superficie de la Tierra."),
        ("Lic. en Ingeniería Mecatrónica", "RIE", "Diseño de robots, automatización industrial combinando mecánica y programación."),
        ("Lic. en Ingeniería Química", "IRC", "Diseño a escala industrial de procesos químicos para transformar materias primas.")
    ]
}

with app.app_context():
    try:
        print("Borrando carreras y áreas antiguas...")
        db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 0;'))
        Carrera.query.delete()
        AreaProfesional.query.delete()
        db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 1;'))
        db.session.commit()
        
        counter = 0
        for area_name, carreras_list in uas_data.items():
            area_code = area_riasec_map.get(area_name, "RIA")
            area = AreaProfesional(
                nombre=area_name,
                codigo_riasec=area_code,
                descripcion="Carreras pertenecientes al área de " + area_name.lower()
            )
            db.session.add(area)
            db.session.flush() # flush to get the ID for the area
            
            for c_name, riasec, desc in carreras_list:
                carrera = Carrera(
                    nombre=c_name,
                    descripcion=desc,
                    perfil_riasec=riasec,
                    area_id=area.id
                )
                db.session.add(carrera)
                counter += 1
                
        db.session.commit()
        print(f"\\n¡Éxito! Se inyectaron 8 Áreas y {counter} carreras oficiales de la UAS en la base de datos.")
        print("Cada carrera ya cuenta con su código RIASEC de 3 letras asignado mediante IA.}")
    except Exception as e:
        db.session.rollback()
        print(f"\\nError crítico: {str(e)}")
