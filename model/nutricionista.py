from helpers.database import db
from flask_restful import fields

from model.usuario import Usuario

nutricionistaFields = {
  "id": fields.Integer,
  "nome": fields.String,
  "email": fields.String,
  "cpf": fields.String,
  "tipo": fields.String,
  "crn": fields.String,
  "nutricionistaImg": fields.Url('nutricionistaimg', absolute=True)
}

nutricionistaFieldsToken = {
  "nutricionista": fields.Nested(nutricionistaFields),
  "token": fields.String
}

nutricionistaPagination = {
  "nutricionistas": fields.Nested(nutricionistaFields),
  "totalNutricionistas": fields.Integer
}

class Nutricionista(Usuario):
  __tablename__= "tb_nutricionista"

  usuario_id = db.Column(db.Integer ,db.ForeignKey("tb_usuario.id"), primary_key=True)
  crn = db.Column(db.String, nullable=False, unique=True)

  __mapper_args__ = {"polymorphic_identity": "Nutricionista"}

  def __init__(self, nome, email, senha, cpf, crn):
    super().__init__(nome, email, senha, cpf)
    self.crn = crn

  def __repr__(self):
    return f"<Nutricionista {self.nome}>"