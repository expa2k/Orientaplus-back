from app.extensions import db
from datetime import datetime

class MercadoRegional(db.Model):
    __tablename__ = 'mercado_regional'

    id = db.Column(db.Integer, primary_key=True)
    carrera_id = db.Column(db.Integer, db.ForeignKey('carreras.id', ondelete='CASCADE'), nullable=False)
    estado = db.Column(db.String(50), nullable=False, default='Sinaloa')
    salario_promedio = db.Column(db.Integer, nullable=True)
    demanda_laboral = db.Column(db.Enum('Baja', 'Media', 'Alta'), nullable=False, default='Media')
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    carrera = db.relationship('Carrera', backref=db.backref('datos_mercado', lazy=True, cascade='all, delete-orphan'))

    def to_dict(self):
        return {
            'id': self.id,
            'carrera_id': self.carrera_id,
            'estado': self.estado,
            'salario_promedio': self.salario_promedio,
            'demanda_laboral': self.demanda_laboral
        }
