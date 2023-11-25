from flask_restful import Resource, reqparse, marshal
from password_strength import PasswordPolicy
from jwt import decode, ExpiredSignatureError, InvalidSignatureError
from model.atleta import Atleta
from helpers.logger import logger
from model.mensagem import Message, msgFields
from werkzeug.security import generate_password_hash
from helpers.database import db
parser = reqparse.RequestParser()

parser.add_argument("novaSenha", type=str, help="Nova senha é obrigatória", required=False)

policy = PasswordPolicy.from_names(
  length =8,
  uppercase = 1,
  numbers=1,
  special=1
)

class NewSenha(Resource):
  def patch(self, token):
    try:
      args = parser.parse_args()
      payload = decode(token, "1234", algorithms="HS256")
      atleta = Atleta.query.filter_by(email=payload["email"]).first()

      if atleta is None:
        logger.error(f"Atleta nao encontrado")
        codigo = Message(1, "Atleta não encontrado")
        return marshal(codigo, msgFields), 404
      if args["novaSenha"] is None:
        logger.error(f"nova senha nao informado")
        codigo = Message(1, "nova senha não informada")
        return marshal(codigo, msgFields), 400
      
      atleta.senha = generate_password_hash(args["novaSenha"])
      db.session.add(atleta)
      db.session.commit()

      logger.info("Senha atualizada com sucesso")
      codigo = Message(0, "Senha atualizada com sucesso")
      return marshal(codigo, msgFields), 200

    except ExpiredSignatureError:
      logger.error("Token expirado")
      codigo = Message(1, "Token expirado")
      return marshal(codigo, msgFields), 401
    except InvalidSignatureError:
      logger.error("Token invalido")
      codigo = Message(1, "Token invalido")
      return marshal(codigo, msgFields), 401
    except:
      logger.error("Error ao atualizar a senha")
      codigo = Message(2, "Error ao atualizar a senha")
      return marshal(codigo, msgFields), 400
