from app.extensions import db


class Carrera(db.Model):
    __tablename__ = 'carreras'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    area_id = db.Column(db.Integer, db.ForeignKey('areas_profesionales.id'), nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    perfil_riasec = db.Column(db.String(6), nullable=False)
    campo_laboral = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'area_id': self.area_id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'perfil_riasec': self.perfil_riasec,
            'campo_laboral': self.campo_laboral,
            'activo': self.activo,
            'area_nombre': self.area.nombre if self.area else None
        }
