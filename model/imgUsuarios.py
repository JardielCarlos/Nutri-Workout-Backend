from helpers.database import db

class ImgUsuarios(db.Model):
  __tablename__ = 'tb_imgUsuarios'

  id = db.Column(db.Integer, primary_key=True)
  fotoPerfil = db.Column(db.LargeBinary, nullable=True)
  usuario_id = db.Column(db.Integer, db.ForeignKey("tb_usuario.id"))

  usuario = db.relationship("Usuario", back_populates="imagem")

  def __init__(self, fotoPerfil, usuario_id):
    self.fotoPerfil = fotoPerfil
    self.usuario_id = usuario_id

  def __repr__(self):
    return f"<ImgUsuarios {self.fotoPerfil}"

