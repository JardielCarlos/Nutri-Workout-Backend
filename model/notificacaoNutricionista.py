from flask_restful import fields
from helpers.database import db

notificacaoNutricionistaFields = {
  "id": fields.Integer,
  "atleta_id": fields.Integer,
  "nome": fields.String,
  "email": fields.String,
  "mensagem": fields.String
}

nutricionista_rejeitado = db.Table('nutricionista_rejeitado',
  db.Column('notificacao_id', db.Integer, db.ForeignKey('tb_notificacaoNutricionista.id')),
  db.Column('nutricionista_id', db.Integer, db.ForeignKey('tb_nutricionista.usuario_id'))
)

class NotificacaoNutricionista(db.Model):
  __tablename__ = 'tb_notificacaoNutricionista'

  id = db.Column(db.Integer, primary_key=True)
  nome = db.Column(db.String, nullable=False)
  email = db.Column(db.String, nullable=False, unique=True)
  mensagem = db.Column(db.String, nullable=False)
  solicitacao = db.Column(db.Boolean, nullable=False, default=False)

  atleta_id = db.Column(db.Integer, db.ForeignKey('tb_atleta.usuario_id'), unique=True) 
  atleta = db.relationship('Atleta', backref=db.backref("notificacoes_nutricionista", cascade="all,delete"), foreign_keys=[atleta_id]) 

  nutricionistas_rejeitados = db.relationship('Nutricionista', secondary=nutricionista_rejeitado, backref=db.backref('notificacoes_rejeitadas'))

  def __init__(self, nome, email, mensagem, atleta):
    self.nome = nome
    self.email = email
    self.mensagem = mensagem
    self.atleta = atleta
  
  def __repr__(self):
    return "<NotificacaoPersonal>"