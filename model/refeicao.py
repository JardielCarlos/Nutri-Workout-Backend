from helpers.database import db
from flask_restful import fields

from model.ingrediente import Ingrediente, ingredienteFields

refeicaoFields = {
  "id": fields.Integer,
  "nome": fields.String,
  "diaSemana": fields.String,
  "tipoRefeicao": fields.String,
  "ingredientes": fields.List(fields.Nested(ingredienteFields))
}

class Refeicao(db.Model):
  __tablename__ = 'tb_refeicao'

  id = db.Column(db.Integer, primary_key=True)
  nome = db.Column(db.String, nullable=False)
  diaSemana = db.Column(db.Enum('segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo', name='dia_da_semana'), nullable=False)
  tipoRefeicao = db.Column(db.Enum('cafeManha', 'lancheManha', 'almoco', 'lancheTarde', 'janta', 'lancheNoite', name='tipo_refeicao'), nullable=False)

  ingredientes = db.relationship("Ingrediente", backref="ingrediente_backref", foreign_keys=[Ingrediente.refeicao], cascade="all,delete")

  cardapio = db.Column(db.Integer, db.ForeignKey("tb_cardapio.id", ondelete='CASCADE'), nullable=False)

  __table_args__ = (db.UniqueConstraint('diaSemana', 'tipoRefeicao', 'cardapio', name='unique_refeicao_por_dia'),)

  def __init__(self, nome, diaSemana, tipoRefeicao):
    self.nome = nome
    self.diaSemana = diaSemana
    self.tipoRefeicao = tipoRefeicao

  def __repr__(self):
    return f"<Refeicao {self.id}>"
