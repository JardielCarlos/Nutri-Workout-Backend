from flask_restful import fields
from helpers.database import db
from model.exercicioAtleta import ExercicioAtleta
from model.exercicioAtleta import exercicioFields

class DateField(fields.Raw):
  def format(self, value):
    return value.strftime('%d/%m/%Y')

tabelaTreinoFields = {
  "id": fields.Integer,
  "semanaInicio": DateField,
  "semanaFim": DateField,
  "exercicios": fields.List(fields.Nested(exercicioFields)),
  "atleta": fields.Integer,
  "personal": fields.Integer
}

class TabelaTreino(db.Model):
  __tablename__ = "tb_tabelaTreino"

  id = db.Column(db.Integer, primary_key=True)
  semanaInicio = db.Column(db.Date, nullable=False)
  semanaFim = db.Column(db.Date, nullable=False)

  exercicios = db.relationship("ExercicioAtleta", backref="tabelaTreino_backref", foreign_keys=[ExercicioAtleta.tabelaTreino])
  atleta = db.Column(db.Integer, db.ForeignKey('tb_atleta.usuario_id'), unique=True)
  personal = db.Column(db.Integer, db.ForeignKey('tb_personalTrainer.usuario_id'))

  def __init__(self, semanaInicio, semanaFim, atleta, personal):
    self.semanaInicio = semanaInicio
    self.semanaFim = semanaFim
    self.atleta = atleta
    self.personal = personal
    
  def __repr__(self):
    return f"<TabelaTreino >"



