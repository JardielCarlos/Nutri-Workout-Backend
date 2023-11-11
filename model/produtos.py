from helpers.database import db
from flask_restful import fields

produtoFields ={
  "nome": fields.String,
  "descricao": fields.String,
  "ativo": fields.Boolean
}

class Produto(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  id_ProductStripe = db.Column(db.Integer, nullable=False)
  nome = db.Column(db.String, nullable=False)
  descricao = db.Column(db.String, nullable=False)
  ativo = db.Column(db.Boolean, nullable=False)

  def __init__(self, id_ProductStripe, nome, descricao, ativo):
    self.id_ProductStripe = id_ProductStripe
    self.nome = nome
    self.descricao = descricao
    self.ativo = ativo

  def __repr__(self):
    return f"<Produto {self.id}>"
