from flask_restful import Resource, marshal
from helpers.logger import logger

from model.usuario import Usuario, userFields

class Usuarios(Resource):
  def get(self):
    usuarios = Usuario.query.all()
    logger.info("Usuarios listados com sucesso")
    return marshal(usuarios, userFields), 200