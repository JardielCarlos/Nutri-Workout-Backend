from helpers.database import db
from flask_restful import fields

from model.usuario import Usuario

administradorFields = {
  "id": fields.Integer,
  "nome": fields.String,
  "sobrenome": fields.String,
  "email": fields.String,
  "cpf": fields.String,
  "tipo": fields.String,
  "administradorImg": fields.Url('administradorimg', absolute=True)
}

administradorFieldsToken = {
  "administrador": fields.Nested(administradorFields),
  "token": fields.String
}

class Administrador(Usuario):
  __tablename__= "tb_administrador"

  usuario_id = db.Column(db.Integer ,db.ForeignKey("tb_usuario.id"), primary_key=True)

  __mapper_args__ = {"polymorphic_identity": "Administrador"}

  def __init__(self, nome, sobrenome, email, senha, cpf):
    super().__init__(nome, sobrenome, email, senha, cpf)

  def __repr__(self):
    return f"<Administrador {self.nome}>"
