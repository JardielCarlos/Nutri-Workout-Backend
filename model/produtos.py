from helpers.database import db
from flask_restful import fields

from model.planos import Plano, planosFields

produtoPlanosFields ={
  "id": fields.Integer,
  "nome": fields.String,
  "descricao": fields.String,
  "ativo": fields.Boolean,
  "planos": fields.List(fields.Nested(planosFields))
}

produtoFields = {
  "id": fields.Integer,
  "nome": fields.String,
  "descricao": fields.String,
  "ativo": fields.Boolean,
}

class Produto(db.Model):
  __tablename__="tb_produtos"

  id = db.Column(db.Integer, primary_key=True)
  id_ProductStripe = db.Column(db.String, nullable=True)
  nome = db.Column(db.String, nullable=False)
  descricao = db.Column(db.String, nullable=False)
  ativo = db.Column(db.Boolean, nullable=False, default=False)

  planos = db.relationship("Plano", backref="produto")


  def __init__(self, nome, descricao):
    self.nome = nome
    self.descricao = descricao


  def __repr__(self):
    return f"<Produto {self.id}>"
