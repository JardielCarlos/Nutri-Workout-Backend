from helpers.database import db
from flask_restful import fields

from model.usuario import Usuario
from model.atleta import Atleta

personalTrainerFields = {
  "id": fields.Integer,
  "nome": fields.String,
  "email": fields.String,
  "cpf": fields.String,
  "tipo": fields.String,
  "cref": fields.String
}

personalTrainerFieldsToken = {
  "personal": fields.Nested(personalTrainerFields),
  "token": fields.String
}

personalTrainerPagination = {
  "personais": fields.Nested(personalTrainerFields),
  "totalPersonais": fields.Integer
}

class PersonalTrainer(Usuario):
  __tablename__="tb_personalTrainer"

  usuario_id = db.Column(db.Integer ,db.ForeignKey("tb_usuario.id"), primary_key=True)
  cref = db.Column(db.String, nullable=False, unique=True)

  atletas = db.relationship("Atleta", backref="personal_trainer", foreign_keys=[Atleta.usuario_id])

  __mapper_args__ = {"polymorphic_identity": "Personal Trainer"}


  def __init__(self, nome, email, senha, cpf, cref):
    super().__init__(nome, email, senha, cpf)
    self.cref = cref

  def __repr__(self):
    return f"<PersonalTrainer {self.nome}>"