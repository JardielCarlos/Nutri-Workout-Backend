from helpers.database import db
from flask_restful import fields

cartaoCreditoFields = {
  "id": fields.Integer,
  "nomeTitular": fields.String,
  "bandeira": fields.String,
  "mesVencimento": fields.String,
  "anoVencimento": fields.String,
  "finalCartao": fields.String,
  "pagamentoPadrao": fields.String,
  "atleta_id": fields.Integer
}

class CartaoCredito(db.Model):
  __tablename__ = "tb_cartaoCredito"

  id = db.Column(db.Integer, primary_key=True)
  id_cartaoCredito = db.Column(db.String, nullable=False)
  nomeTitular = db.Column(db.String, nullable=False)
  bandeira = db.Column(db.String, nullable=False)
  mesVencimento = db.Column(db.String, nullable=False)
  anoVencimento = db.Column(db.String, nullable=False)
  finalCartao = db.Column(db.String, nullable=False)
  pagamentoPadrao = db.Column(db.String, nullable=True)
  atleta_id = db.Column(db.Integer ,db.ForeignKey("tb_atleta.usuario_id", ondelete='CASCADE'), nullable=False)

  def __init__(self, atleta_id):
    self.atleta_id = atleta_id

  def __repr__(self):
    return f"<CartaoCredito {self.id}>"

