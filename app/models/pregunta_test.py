from app.extensions import db


class PreguntaTest(db.Model):
    __tablename__ = 'preguntas_test'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bloque = db.Column(db.Integer, nullable=False, default=1)
    tipo = db.Column(db.Enum('likert', 'opcion_multiple', 'abierta'), nullable=False, default='likert')
    texto = db.Column(db.Text, nullable=False)
    opciones = db.Column(db.JSON, default=None)
    dimension_riasec = db.Column(db.String(1), nullable=False)
    orden = db.Column(db.Integer, nullable=False, default=0)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'bloque': self.bloque,
            'tipo': self.tipo,
            'texto': self.texto,
            'opciones': self.opciones,
            'dimension_riasec': self.dimension_riasec,
            'orden': self.orden
        }
