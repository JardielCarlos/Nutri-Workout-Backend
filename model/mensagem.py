from flask_restful import fields

msgFields = {
  "codigo": fields.Integer,
  "descricao": fields.String
}

msgFieldsToken = {
  "msg": fields.Nested(msgFields),
  "token": fields.String
}

class Message:
  def __init__(self, codigo, descricao):
    self.codigo = codigo
    self.descricao = descricao