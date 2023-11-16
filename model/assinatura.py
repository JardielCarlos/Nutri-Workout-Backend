from helpers.database import db

class Assinaturas(db.Model):
  __tablename__ = 'tb_assinaturas'

  id = db.Column(db.Integer, primary_key=True)
  id_AssinaturaStripe = db.Column(db.String, nullable=True)
  nome = db.Column(db.String, nullable=False)
  descricao = db.Column(db.String, nullable=False)
  intervalo = db.Column(db.Enum("day", "week", "month", "year", name='intervalo_plano'), nullable=False)
  valor = db.Column(db.Float, nullable=False)
  data_inicio = db.Column(db.DateTime, nullable=True)
  data_fim_teste = db.Column(db.DateTime, nullable=True)
  ativo = db.Column(db.Boolean, nullable=False, default=False)
  atleta_id = db.Column(db.Integer, db.ForeignKey('tb_atleta.usuario_id'), nullable=False)
  plano_id = db.Column(db.Integer ,db.ForeignKey("tb_planos.id"), nullable=False)

  def __init__(self):
    pass

  def __repr__(self):
    return f"<Assinatura {self.intervalo}>"
