from flask_restful import Resource, marshal
from helpers.logger import logger

from helpers.auth.token_verifier import token_verify

from model.mensagem import Message, msgFields
from model.nutricionista import Nutricionista
from model.atleta import atletaAssociatedFields

class NutricionistaAtleta(Resource):
  @token_verify
  def get(self, tipo, refreshToken, user_id):
    if tipo != "Nutricionista":
      logger.error("Usuario sem autorizacao para acessar os atletas associados ao nutricionista")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    
    nutricionista = Nutricionista.query.get(user_id)
    return marshal(nutricionista.atletas, atletaAssociatedFields), 200
  

class NutricionistaAtletaId(Resource):
  def put(self, id):
    pass