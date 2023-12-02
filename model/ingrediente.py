from helpers.database import db
from flask_restful import fields

ingredienteFields = {
  "id": fields.Integer,
  "nome": fields.String,
  "quantidade": fields.String,
}

ingredienteFieldsPagination = {
  "ingredientes": fields.Nested(ingredienteFields),
  "total": fields.Integer,
}

class Ingrediente(db.Model):
  __tablename__ = "tb_ingrediente"

  id = db.Column(db.Integer, primary_key=True)
  nome = db.Column(db.String, nullable=False)
  quantidade = db.Column(db.String, nullable=False)

  refeicao = db.Column(db.Integer, db.ForeignKey("tb_refeicao.id", ondelete='CASCADE'), nullable=False)

  def __init__(self, nome, quantidade):
    self.nome = nome
    self.quantidade = quantidade

  def __repr__(self):
    return f"<Ingrediente {self.id}>"
