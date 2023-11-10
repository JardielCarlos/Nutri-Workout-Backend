from helpers.database import db
from flask_restful import fields

from model.refeicao import Refeicao, refeicaoFields

cardapioFields = {
  "id": fields.Integer,
  "nome": fields.String,
  "refeicoes": fields.List(fields.Nested(refeicaoFields)),
  "atleta": fields.Integer,
  "nutricionista": fields.Integer
}

from model.refeicao import Refeicao

class Cardapio(db.Model):
  __tablename__ = 'tb_cardapio'

  id = db.Column(db.Integer, primary_key=True)
  nome = db.Column(db.String, nullable=False)

  refeicoes = db.relationship("Refeicao", backref="refeicao_backref", foreign_keys=[Refeicao.cardapio])

  atleta = db.Column(db.Integer, db.ForeignKey('tb_atleta.usuario_id', ondelete='CASCADE'), unique=True)
  nutricionista = db.Column(db.Integer, db.ForeignKey('tb_nutricionista.usuario_id'))

  def __init__(self, nome, atleta):
    self.nome = nome,
    self.atleta = atleta,

  def __repr__(self):
    return f"<Cardapio {self.id}>"
