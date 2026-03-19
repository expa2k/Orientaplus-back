from datetime import datetime
from app.extensions import db


class RespuestaTest(db.Model):
    __tablename__ = 'respuestas_test'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sesion_id = db.Column(db.Integer, db.ForeignKey('sesiones_test.id'), nullable=False)
    pregunta_id = db.Column(db.Integer, db.ForeignKey('preguntas_test.id'), nullable=False)
    valor = db.Column(db.String(10), nullable=False)
    fecha_respuesta = db.Column(db.DateTime, default=datetime.utcnow)

    pregunta = db.relationship('PreguntaTest', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('sesion_id', 'pregunta_id', name='uq_respuesta_unica'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'sesion_id': self.sesion_id,
            'pregunta_id': self.pregunta_id,
            'valor': self.valor,
            'fecha_respuesta': self.fecha_respuesta.isoformat() if self.fecha_respuesta else None
        }
