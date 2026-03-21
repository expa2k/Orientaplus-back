import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.pregunta_test import PreguntaTest
from sqlalchemy import text

app = create_app()

def seed_preguntas_v2():
    with app.app_context():
        # Nos aseguramos de purgar cualquier respuesta o pregunta vieja
        db.session.execute(text('SET FOREIGN_KEY_CHECKS = 0;'))
        db.session.execute(text('TRUNCATE TABLE respuestas_test;'))
        db.session.execute(text('TRUNCATE TABLE preguntas_test;'))
        db.session.execute(text('SET FOREIGN_KEY_CHECKS = 1;'))

        opciones_likert = {
            '1': 'Muy en desacuerdo',
            '2': 'En desacuerdo',
            '3': 'Neutral',
            '4': 'De acuerdo',
            '5': 'Muy de acuerdo'
        }
        
        # EL EMBUDO ESTA DISEÑADO EN 3 BLOQUES
        # Bloque 1: General (Todo el espectro, se evaluan las 6 letras)
        # Bloque 2: Intermedio (Se detectaron top 3 dimensiones, enfocamos aquí)
        # Bloque 3: Laser (Diferenciación estricta de sub-carreras: ej. SoftEng vs Biología vs Civil)

        preguntas = [
            # -------------------------------------------------------------
            # BLOQUE 1 - EXPLORACION AMPLIA (Hobbies, Vida Cotidiana)
            # -------------------------------------------------------------
            {"texto": "Hacer actividades al aire libre, deportes o usar mis manos para crear cosas.", "riasec": "R", "bloque": 1, "tipo": "likert"},
            {"texto": "Usar herramientas para construir o reparar objetos dañados en la casa.", "riasec": "R", "bloque": 1, "tipo": "likert"},
            {"texto": "Aprender con curiosidad cómo funcionan las cosas (naturaleza, química o tecnología).", "riasec": "I", "bloque": 1, "tipo": "likert"},
            {"texto": "Resolver acertijos, rompecabezas de lógica pura o disfrutar las matemáticas.", "riasec": "I", "bloque": 1, "tipo": "likert"},
            {"texto": "Dibujar, expresarme con música, diseño creativo o disfrutar del arte.", "riasec": "A", "bloque": 1, "tipo": "likert"},
            {"texto": "Escribir historias, leer literatura o interesarme por la expresión visual.", "riasec": "A", "bloque": 1, "tipo": "likert"},
            {"texto": "Ayudar a otras personas a resolver sus problemas o enseñarles algo nuevo.", "riasec": "S", "bloque": 1, "tipo": "likert"},
            {"texto": "Cuidar del bienestar de los demás, escucharlos y darles consejos amigables.", "riasec": "S", "bloque": 1, "tipo": "likert"},
            {"texto": "Organizar eventos escolares, ser el líder de un grupo o pensar en emprendimientos.", "riasec": "E", "bloque": 1, "tipo": "likert"},
            {"texto": "Convencer a otros de mis ideas, debatir o vender productos/servicios.", "riasec": "E", "bloque": 1, "tipo": "likert"},
            {"texto": "Mantener mis cosas muy ordenadas, hacer listas y seguir reglas precisas.", "riasec": "C", "bloque": 1, "tipo": "likert"},
            {"texto": "Tener control estricto de mis gastos, ordenar datos o disfrutar el papeleo.", "riasec": "C", "bloque": 1, "tipo": "likert"},
            
            # Abierta Bloque 1
            {"texto": "Con tus propias palabras: ¿Cuáles son las tres grandes actividades, materias o hobbies que más disfrutas hacer en tu tiempo libre y por qué?", "riasec": "X", "bloque": 1, "tipo": "abierta"},

            # -------------------------------------------------------------
            # BLOQUE 2 - ENFOQUE TECNICO MODERADO (Áreas Profesionales)
            # -------------------------------------------------------------
            {"texto": "Involucrarme en la construcción, observar planos o entender arquitectura civil.", "riasec": "R", "bloque": 2, "tipo": "likert"},
            {"texto": "Entender cómo funcionan los motores físicos, máquinas electrónicas o la robótica.", "riasec": "R", "bloque": 2, "tipo": "likert"},
            {"texto": "Trabajar en la naturaleza de forma profesional, tratar con plantas o animales.", "riasec": "R", "bloque": 2, "tipo": "likert"},
            
            {"texto": "Aprender sobre computadoras, crear programas, apps o explorar el mundo tecnológico.", "riasec": "I", "bloque": 2, "tipo": "likert"},
            {"texto": "Hacer experimentos médicos, investigar enferemedades o estar en un laboratorio de biología.", "riasec": "I", "bloque": 2, "tipo": "likert"},
            {"texto": "Analizar misterios del universo, física moderna o resolver teorías complejas.", "riasec": "I", "bloque": 2, "tipo": "likert"},
            
            {"texto": "Crear contenido multimedia web, editar videos atractivos o crear animaciones 3D.", "riasec": "A", "bloque": 2, "tipo": "likert"},
            {"texto": "Dedicarme a escribir profesionalmente guiones, artículos o libros literarios.", "riasec": "A", "bloque": 2, "tipo": "likert"},
            {"texto": "Actuar en un escenario, dirigir obras de teatro o dedicarme a la música formal.", "riasec": "A", "bloque": 2, "tipo": "likert"},

            {"texto": "Estudiar la mente humana para trabajar como terapeuta o psicólogo profesional.", "riasec": "S", "bloque": 2, "tipo": "likert"},
            {"texto": "Formar parte de un hospital trabajando bajo presión para salvar vidas o rehabilitar.", "riasec": "S", "bloque": 2, "tipo": "likert"},
            {"texto": "Defender a personas vulnerables, conocer de derechos y trabajar de abogado.", "riasec": "S", "bloque": 2, "tipo": "likert"},

            {"texto": "Administrar un negocio propio enorme, dirigir empleados y tomar decisiones clave.", "riasec": "E", "bloque": 2, "tipo": "likert"},
            {"texto": "Hablar en público para ganar debates políticos o gestionar relaciones institucionales.", "riasec": "E", "bloque": 2, "tipo": "likert"},
            {"texto": "Crear campañas comerciales atractivas, manejar presupuestos y decidir inversiones.", "riasec": "E", "bloque": 2, "tipo": "likert"},

            {"texto": "Asegurarme de que las reglas informáticas o leyes se cumplan al margen de la letra.", "riasec": "C", "bloque": 2, "tipo": "likert"},
            {"texto": "Llevar la contabilidad de una empresa, revisar impuestos y grandes tablas de Excel.", "riasec": "C", "bloque": 2, "tipo": "likert"},
            {"texto": "Supervisar normas sanitarias y orgánicas en el control de calidad de una fábrica.", "riasec": "C", "bloque": 2, "tipo": "likert"},

            # Abiertas Bloque 2 (Dinámicas según las dimensiones altas)
            {"texto": "¿Qué tipo de herramientas manuales, estructuras o proyectos de la naturaleza te atraería conocer al máximo y trabajar en ello?", "riasec": "R", "bloque": 2, "tipo": "abierta"},
            {"texto": "Si pudieras investigar a fondo un tema durante años: ¿Te irías por explorar la tecnología de software, las ciencias de la salud, o los números abstractos? Explica un poco.", "riasec": "I", "bloque": 2, "tipo": "abierta"},
            {"texto": "¿Podrías vivir feliz si tu trabajo fuera puramente crear artes, música, escritos creativos o diseños gráficos? Explica tu respuesta.", "riasec": "A", "bloque": 2, "tipo": "abierta"},
            {"texto": "Imagina que tienes que ayudar todos los días a gente que sufre enfermedades, o alumnos, o personas con problemas legales. ¿A quiénes preferirías ayudar y cómo?", "riasec": "S", "bloque": 2, "tipo": "abierta"},
            {"texto": "¿Si fundaras una empresa increíblemente millonaria, de qué tipo de cosas se trataría y qué rol de líder directo jugarías tú?", "riasec": "E", "bloque": 2, "tipo": "abierta"},
            {"texto": "Háblame de cómo gestionas tu orden: ¿te atrae la idea de controlar bases de datos llenas de información clasificada o administrar archivos financieros millonarios?", "riasec": "C", "bloque": 2, "tipo": "abierta"},

            # -------------------------------------------------------------
            # BLOQUE 3 - TOMA DE DESICION FINAL (Carreras en acción)
            # -------------------------------------------------------------
            {"texto": "Supervisar que un edificio o carretera cumpla estrictamente con la ingeniería estructural necesaria.", "riasec": "R", "bloque": 3, "tipo": "likert"},
            {"texto": "Tener labores técnicas avanzadas como controlar redes eléctricas de telecomunicaciones o aeronáutica.", "riasec": "R", "bloque": 3, "tipo": "likert"},
            {"texto": "Aplicar tratamientos y tecnología especial para mejorar cultivos de la tierra, bosques o pesca.", "riasec": "R", "bloque": 3, "tipo": "likert"},

            {"texto": "Escribir código y diseñar la lógica oculta detrás de una página web profesional o sistema de software.", "riasec": "I", "bloque": 3, "tipo": "likert"},
            {"texto": "Examinar tejidos y virus microscópicos para entender genética y enfermedades serias.", "riasec": "I", "bloque": 3, "tipo": "likert"},
            {"texto": "Estudiar la literatura muerta y ruinas antiguas para analizar críticamente los hechos de la Historia.", "riasec": "I", "bloque": 3, "tipo": "likert"},

            {"texto": "Enfocarme en el diseño estético de ciudades sostenibles modernas o de interiores en casas de lujo.", "riasec": "A", "bloque": 3, "tipo": "likert"},
            {"texto": "Participar en la dirección visual para efectos y modelado renderizado de una gran obra cinematográfica.", "riasec": "A", "bloque": 3, "tipo": "likert"},
            {"texto": "Ser quien diseña visualmente el logo y los colores atractivos (branding) para empresas u organizaciones.", "riasec": "A", "bloque": 3, "tipo": "likert"},

            {"texto": "Trabajar asistiendo pacientes pediátricos, quirófanos de cirugías o dando consultas médicas especializadas.", "riasec": "S", "bloque": 3, "tipo": "likert"},
            {"texto": "Trabajar dictaminando veredictos y revisando crímenes de corporaciones frente a leyes constitucionales.", "riasec": "S", "bloque": 3, "tipo": "likert"},
            {"texto": "Especializarme en ayudar a la salud humana específicamente mediante nutrición especializada o medicina deportiva.", "riasec": "S", "bloque": 3, "tipo": "likert"},

            {"texto": "Entender la exportación marítima aduanal e importación internacional de millones de mercancías.", "riasec": "E", "bloque": 3, "tipo": "likert"},
            {"texto": "Promover grandes leyes, estar en relaciones públicas, la política del estado y las gestiones gubernamentales.", "riasec": "E", "bloque": 3, "tipo": "likert"},
            {"texto": "Diseñar las tácticas perfectas para que toda la universidad conozca tu nueva aplicación web de IA.", "riasec": "E", "bloque": 3, "tipo": "likert"},

            {"texto": "Vigilar rigurosamente que las líneas de código de una app no contengan ningún error de seguridad informático.", "riasec": "C", "bloque": 3, "tipo": "likert"},
            {"texto": "Elaborar una declaración estricta con cientos de facturas bajo las leyes de comercio y tributación mexicanas.", "riasec": "C", "bloque": 3, "tipo": "likert"},
            {"texto": "Controlar e inspeccionar minuciosamente toda la calidad biológica e higiene en una fábrica industrial.", "riasec": "C", "bloque": 3, "tipo": "likert"},
            
            # Abiertas Finales Bloque 3 (Desempate definitivo)
            {"texto": "¿Sentirías mayor vocación siendo tú mismo quien crea el software de computadora o siendo alguien que investiga a fondo una reacción química en salud? Desarrolla tu respuesta.", "riasec": "I", "bloque": 3, "tipo": "abierta"},
            {"texto": "De frente al mundo empresarial, describe cómo te atrae la parte del control estricto de números o bases de datos comparado contra otras tareas.", "riasec": "C", "bloque": 3, "tipo": "abierta"},
            {"texto": "Sinceramente, describe si en tu fututo te ves aportando de manera lógica con código, o si prefieres aportar valor de forma puramente artística o dibujada.", "riasec": "A", "bloque": 3, "tipo": "abierta"},
        ]

        print("Inyectando 60+ preguntas hiper-focalizadas de IA...")
        for i, p in enumerate(preguntas, 1):
            nueva_preg = PreguntaTest(
                bloque=p['bloque'],
                tipo=p['tipo'],
                texto=p['texto'],
                opciones=opciones_likert if p['tipo'] == 'likert' else None,
                dimension_riasec=p['riasec'],
                orden=i
            )
            db.session.add(nueva_preg)

        db.session.commit()
        print("Éxito: Se ha restaurado el Banco de Preguntas V2 con embudos de alta precisión para ML.")

if __name__ == '__main__':
    seed_preguntas_v2()
