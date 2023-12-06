from helpers.database import db
from flask_restful import fields

class DateField(fields.Raw):
  def format(self, value):
    return value.strftime('%Y-%m-%d')

assinaturaFields = {
  "id": fields.Integer,
  "nome": fields.String,
  "intervalo": fields.String,
  "valor": fields.Float,
  "data_inicio": DateField,
  "data_fim": DateField,
  "data_inicio_teste": DateField,
  "data_fim_teste": DateField,
  "status": fields.String,
  "atleta_id": fields.Integer,
  "plano_id": fields.Integer
}

class Assinatura(db.Model):
  __tablename__ = 'tb_assinaturas'

  id = db.Column(db.Integer, primary_key=True)
  id_AssinaturaStripe = db.Column(db.String, nullable=True)
  nome = db.Column(db.String, nullable=False)
  intervalo = db.Column(db.Enum("day", "week", "month", "year", name='intervalo_planoAssinatura'), nullable=False)
  valor = db.Column(db.Float, nullable=False)
  data_inicio = db.Column(db.DateTime, nullable=True)
  data_fim = db.Column(db.DateTime, nullable=True)
  data_inicio_teste = db.Column(db.DateTime, nullable=True)
  data_fim_teste = db.Column(db.DateTime, nullable=True)
  status = db.Column(db.String, nullable=True)
  atleta_id = db.Column(db.Integer, db.ForeignKey('tb_atleta.usuario_id', ondelete='CASCADE'), nullable=False, unique=True)
  plano_id = db.Column(db.Integer ,db.ForeignKey("tb_planos.id"), nullable=False)

  def __init__(self):
    pass

  def __repr__(self):
    return f"<Assinatura {self.intervalo}>"
