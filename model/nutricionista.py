from flask_restful import fields

from helpers.database import db
from model.atleta import Atleta, atletaAssociatedFields
from model.usuario import Usuario

nutricionistaFields = {
  "id": fields.Integer,
  "nome": fields.String,
  "sobrenome": fields.String,
  "email": fields.String,
  "cpf": fields.String,
  "tipo": fields.String,
  "crn": fields.String,
  "nutricionistaImg": fields.Url('nutricionistaimg', absolute=True)
}

nutricionistaAssociatedFields = {
  "id": fields.Integer,
  "nome": fields.String,
  "sobrenome": fields.String,
  "email": fields.String,
  "cpf": fields.String,
  "tipo": fields.String,
  "crn": fields.String,
  "nutricionistaImg": fields.Url('nutricionistaimg', absolute=True),
  "atletas": fields.List(fields.Nested(atletaAssociatedFields))
}
nutricionistaFieldsToken = {
  "nutricionista": fields.Nested(nutricionistaFields),
  "token": fields.String
}
nutricionistaAssociatedFieldsToken = {
  "nutricionista": fields.Nested(nutricionistaAssociatedFields),
  "token": fields.String
}

nutricionistaPagination = {
  "nutricionistas": fields.Nested(nutricionistaFields),
  "totalNutricionistas": fields.Integer
}

nutricionistaAtletasPaginationFields = {
  "atletasNutricionista": fields.Nested(atletaAssociatedFields),
  "totalAtletas": fields.Integer
}

class Nutricionista(Usuario):
  __tablename__= "tb_nutricionista"

  usuario_id = db.Column(db.Integer ,db.ForeignKey("tb_usuario.id"), primary_key=True)
  crn = db.Column(db.String, nullable=False, unique=True)

  atletas = db.relationship("Atleta", backref="nutricionista", foreign_keys=[Atleta.nutricionista_id])

  __mapper_args__ = {"polymorphic_identity": "Nutricionista"}

  def __init__(self, nome, sobrenome, email, senha, cpf, crn):
    super().__init__(nome, sobrenome, email, senha, cpf)
    self.crn = crn

  def __repr__(self):
    return f"<Nutricionista {self.nome}>"
