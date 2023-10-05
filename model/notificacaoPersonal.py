from flask_restful import fields
from helpers.database import db

notificacaoPersonalFields = {
  "id": fields.Integer,
  "atleta_id": fields.Integer,
  "nome": fields.String,
  "email": fields.String,
  "mensagem": fields.String
}

class NotificacaoPersonal(db.Model):
  __tablename__ = 'tb_notificacaoPersonal'

  id = db.Column(db.Integer, primary_key=True)
  nome = db.Column(db.String, nullable=False)
  email = db.Column(db.String, nullable=False, unique=True)
  mensagem = db.Column(db.String, nullable=False)
  solicitacao = db.Column(db.Boolean, nullable=False, default=False)

  personal_id = db.Column(db.Integer, db.ForeignKey('tb_personalTrainer.usuario_id'), nullable=True)
  personal = db.relationship('PersonalTrainer', backref='notificacoes')
  
  atleta_id = db.Column(db.Integer, db.ForeignKey('tb_atleta.usuario_id'), unique=True) 
  atleta = db.relationship('Atleta') 

  def __init__(self, nome, email, mensagem, atleta):
    self.nome = nome
    self.email = email
    self.mensagem = mensagem
    self.atleta = atleta
  
  def __repr__(self):
    return "<NotificacaoPersonal>"