from helpers.database import db
from flask_restful import fields
from model.usuario import Usuario

atletaFields = {
  "id": fields.Integer,
  "nome": fields.String,
  "email": fields.String,
  "cpf": fields.String,
  "tipo": fields.String,
  "massaMagra": fields.Float,
  "massaGorda": fields.Float,
  "altura": fields.Float,
  "peso": fields.Float,
  "imc": fields.Float,
  "statusPagamento": fields.Boolean,
  "atletaImg": fields.Url("atletaimg", absolute=True)
}

atletaFieldsToken = {
  "atleta": fields.Nested(atletaFields),
  "token": fields.String
}

atletasFieldsPagination = {
  "atletas": fields.Nested(atletaFields),
  "totalAtletas": fields.Integer
}

atletaAssociatedPersonalFields = {
  "id": fields.Integer,
  "nome": fields.String,
  "email": fields.String,
  "cpf": fields.String,
  "tipo": fields.String,
}

class Atleta(Usuario):
  __tablename__ = 'tb_atleta'
  
  usuario_id = db.Column(db.Integer ,db.ForeignKey("tb_usuario.id"), primary_key=True)
  massaMagra = db.Column(db.Float, nullable=True)
  massaGorda = db.Column(db.Float, nullable=True)
  altura = db.Column(db.Float, nullable=True)
  peso = db.Column(db.Float, nullable=True)
  imc = db.Column(db.Float, nullable=True)
  statusPagamento = db.Column(db.Boolean, nullable=False, default=True)

  personal_trainer_id = db.Column(db.Integer ,db.ForeignKey("tb_personalTrainer.usuario_id"), nullable=True)
  
  __mapper_args__ = {"polymorphic_identity": "Atleta"}

  def __init__(self, nome, email, senha, cpf):
    super().__init__(nome, email, senha, cpf)

  def __repr__(self):
    return f"<Atleta {self.nome}>"