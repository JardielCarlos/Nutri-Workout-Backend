from flask import url_for
from helpers.database import db
from flask_restful import fields
from werkzeug.security import generate_password_hash, check_password_hash

userFields = {
  "id": fields.Integer,
  "nome": fields.String,
  "sobrenome": fields.String,
  "email": fields.String,
  "cpf": fields.String,
  "tipo": fields.String,
  "sigla": fields.String(attribute=lambda x: x.get_sigla()),
  "urlImg": fields.String(attribute=lambda x: x.get_url())
}

usuarioFieldsPagination = {
  "usuarios": fields.Nested(userFields),
  "totalUsuarios": fields.Integer
}

class Usuario(db.Model):
  __tablename__= "tb_usuario"

  id = db.Column(db.Integer, primary_key=True)
  nome = db.Column(db.String, nullable=False)
  sobrenome = db.Column(db.String, nullable=False)
  email = db.Column(db.String, nullable=False, unique=True)
  senha = db.Column(db.String, nullable=False)
  cpf = db.Column(db.String, nullable=False, unique=True)
  tipo = db.Column(db.String, nullable=False)

  imagem = db.relationship("ImgUsuarios", back_populates="usuario", uselist=False, cascade="all, delete-orphan")

  __mapper_args__ = {
    'polymorphic_identity': 'usuario',
    'polymorphic_on': tipo
  }

  def __init__(self, nome, sobrenome, email, senha, cpf):
    self.nome = nome
    self.sobrenome = sobrenome
    self.email = email
    self.senha = generate_password_hash(senha)
    self.cpf = cpf

  def verify_password(self, senha):
    return check_password_hash(self.senha, senha)

  def get_sigla(self):
    return self.nome[0] + self.sobrenome[0]

  def get_url(self):
    if self.tipo == 'Atleta':
      return url_for('atletaimg', id=self.id, _external=True)

    elif self.tipo == 'Personal':
      return url_for('personalimg', id=self.id, _external=True)

    elif self.tipo == 'Nutricionista':
      return url_for('nutricionistaimg', id=self.id, _external=True)

    elif self.tipo == 'Administrador':
      return url_for('administradorimg', id=self.id, _external=True)
    else:
      return None


  def __repr__(self):
    return f"<User {self.nome}>"
