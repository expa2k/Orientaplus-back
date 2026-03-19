from app.extensions import db


class AreaProfesional(db.Model):
    __tablename__ = 'areas_profesionales'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    codigo_riasec = db.Column(db.String(6), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    icono = db.Column(db.String(50))
    activo = db.Column(db.Boolean, default=True, nullable=False)

    carreras = db.relationship('Carrera', backref='area', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'codigo_riasec': self.codigo_riasec,
            'descripcion': self.descripcion,
            'icono': self.icono,
            'activo': self.activo,
            'total_carreras': len(self.carreras) if self.carreras else 0
        }
