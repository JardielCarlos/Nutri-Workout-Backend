from flask_restful import fields
from helpers.database import db

class TabelaTreino(db.Model):
  __tablename__ = "tb_tabelaTreino"

  id = db.Column(db.Integer, primary_key=True)
  diaSemana = db.Column(db.Date, nullable=False)
  musculoTrabalhado = db.Column(db.String, nullable=False)
  nomeExercicio = db.Column(db.String, nullable=False)
  series = db.Column(db.Integer, nullable=False)
  repeticao = db.Column(db.Integer, nullable=False)
  kg = db.Column(db.Integer, nullable=False)
  descanso = db.Column(db.Integer, nullable=False)
  unidadeDescanso = db.Column(db.String, nullable=False)
  observacoes = db.Column(db.String, nullable=False)
  concluido = db.Column(db.Boolean, nullable=False, default=False)

  def __init__(self, diaSemana, musculoTrabalhado, nomeExercicio, series, repeticao, kg, descanso, unidadeDescanso, observacoes):
    self.diaSemana = diaSemana
    self.musculoTrabalhado = musculoTrabalhado
    self.nomeExercicio = nomeExercicio
    self.series = series
    self.repeticao= repeticao
    self.kg = kg
    self.descanso = descanso
    self.unidadeDescanso = unidadeDescanso
    self.observacoes = observacoes
    
  def __repr__(self):
    return f"<TabelaTreino >"



