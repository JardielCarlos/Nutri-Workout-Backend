from flask_restful import fields

from helpers.database import db
from model.atleta import Atleta, atletaAssociatedFields
from model.usuario import Usuario

personalTrainerFields = {
  "id": fields.Integer,
  "nome": fields.String,
  "sobrenome": fields.String,
  "email": fields.String,
  "cpf": fields.String,
  "tipo": fields.String,
  "cref": fields.String,
  "personalImg": fields.Url("personalimg", absolute=True)
}

personalTrainerAssociatedFields = {
  "id": fields.Integer,
  "nome": fields.String,
  "email": fields.String,
  "cpf": fields.String,
  "tipo": fields.String,
  "cref": fields.String,
  "personalImg": fields.Url("personalimg", absolute=True),
  "atletas": fields.List(fields.Nested(atletaAssociatedFields))
}

personalTrainerFieldsToken = {
  "personal": fields.Nested(personalTrainerFields),
  "token": fields.String
}

personalTrainerAssociatedFieldsToken = {
  "personal": fields.Nested(personalTrainerAssociatedFields),
  "token": fields.String
}

personalTrainerPagination = {
  "personais": fields.Nested(personalTrainerFieldsToken),
  "totalPersonais": fields.Integer
}

class PersonalTrainer(Usuario):
  __tablename__="tb_personalTrainer"

  usuario_id = db.Column(db.Integer ,db.ForeignKey("tb_usuario.id"), primary_key=True)
  cref = db.Column(db.String, nullable=False, unique=True)

  atletas = db.relationship("Atleta", backref="personal", foreign_keys=[Atleta.personal_trainer_id])

  __mapper_args__ = {"polymorphic_identity": "Personal Trainer"}


  def __init__(self, nome, sobrenome, email, senha, cpf, cref):
    super().__init__(nome, sobrenome, email, senha, cpf)
    self.cref = cref

  def __repr__(self):
    return f"<PersonalTrainer {self.nome}>"
