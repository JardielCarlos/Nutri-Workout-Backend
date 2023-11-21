from functools import wraps
from flask_restful import request, marshal
from jwt import decode
from model.atleta import Atleta
from helpers.logger import logger
from model.mensagem import Message, msgFields

def subscribe_verifier(function: callable) -> callable:
  @wraps(function)
  def decorated(*args, **kwargs):
    rawToken = request.headers["Authorization"]
    token = rawToken.split()[1]
    informationToken = decode(token, key="1234", algorithms="HS256")
    tipo = informationToken['tipo']
    id = informationToken['id']

    if tipo == "Atleta":
      atleta = Atleta.query.get(id)
      print(atleta.statusPagamento)
      if atleta.statusPagamento != 'active' and atleta.statusPagamento != 'trialing':
        logger.error("Atleta sem assinatura ou com pendencia na assinatura")
        codigo = Message(1, "Atleta sem assinatura ou com pendências na assinatura")
        return marshal(codigo, msgFields), 403

    return function(*args, **kwargs)

  return decorated

