from helpers.database import db
from flask_restful import fields

planosFields = {
  "id": fields.Integer,
  "nome": fields.String,
  "valor": fields.Float,
  "ativo": fields.Boolean,
}

class Plano(db.Model):
  __tablename__="tb_planos"

  id = db.Column(db.Integer, primary_key=True)
  id_PlanoStripe = db.Column(db.String, nullable=True)
  nome = db.Column(db.String, nullable=False)
  valor = db.Column(db.Float, nullable=False)
  intervalo = db.Column(db.Enum("day", "week", "month", "year", name='intervalo_plano'), nullable=False)
  ativo = db.Column(db.Boolean, nullable=False, default=False)

  produto_id = db.Column(db.Integer ,db.ForeignKey("tb_produtos.id"), nullable=True)

  assinaturas = db.relationship("Assinatura", backref="plano")

  def __init__(self, nome, intervalo, valor):
    self.nome = nome
    self.intervalo = intervalo
    self.valor = valor

  def __repr__(self):
    return f"<Plano {self.id}>"
