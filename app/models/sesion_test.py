from datetime import datetime
from app.extensions import db


class SesionTest(db.Model):
    __tablename__ = 'sesiones_test'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    estado = db.Column(db.Enum('en_progreso', 'completada', 'abandonada'),
                       nullable=False, default='en_progreso')
    bloque_actual = db.Column(db.Integer, nullable=False, default=1)
    vector_riasec = db.Column(db.JSON, default=None)
    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_fin = db.Column(db.DateTime, default=None)

    respuestas = db.relationship('RespuestaTest', backref='sesion', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'estado': self.estado,
            'bloque_actual': self.bloque_actual,
            'vector_riasec': self.vector_riasec,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
            'total_respuestas': len(self.respuestas) if self.respuestas else 0
        }
