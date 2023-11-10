from helpers.database import db
from flask_restful import fields

exercicioFields = {
  "id": fields.Integer,
  "musculoTrabalhado": fields.String,
  "nomeExercicio": fields.String,
  "series": fields.Integer,
  "kg": fields.Integer,
  "repeticao": fields.Integer,
  "descanso": fields.Integer,
  "unidadeDescanso": fields.String,
  "observacoes": fields.String,
}

class ExercicioAtleta(db.Model):
  __tablename__= "tb_exercicioAtleta"

  id = db.Column(db.Integer, primary_key=True)
  musculoTrabalhado = db.Column(db.String, nullable=False)
  nomeExercicio = db.Column(db.String, nullable=False)
  series = db.Column(db.Integer, nullable=False)
  kg = db.Column(db.Integer, nullable=False)
  repeticao = db.Column(db.Integer, nullable=False)
  descanso = db.Column(db.Integer, nullable=False)
  unidadeDescanso = db.Column(db.String, nullable=False)
  observacoes = db.Column(db.String, nullable=True)

  tabelaTreino = db.Column(db.Integer, db.ForeignKey("tb_tabelaTreino.id", ondelete='CASCADE'), nullable=False)

  def __init__(self, tabelaTreino, musculoTrabalhado, nomeExercicio, series, repeticao, kg, descanso, unidadeDescanso, observacoes):
    self.tabelaTreino = tabelaTreino
    self.musculoTrabalhado = musculoTrabalhado
    self.nomeExercicio = nomeExercicio
    self.series = series
    self.repeticao= repeticao
    self.kg = kg
    self.descanso = descanso
    self.unidadeDescanso = unidadeDescanso
    self.observacoes = observacoes

  def __repr__(self):
    return f"<ExercioAtleta >"
