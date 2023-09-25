from flask_restful import Resource, reqparse, marshal
from helpers.logger import logger

from model.mensagem import Message, msgFields
from model.usuario import Usuario

from helpers.auth.token_handler import token_creator

parser = reqparse.RequestParser()

parser.add_argument("email", type=str, help="Email não informado", required=True)
parser.add_argument("senha", type=str, help="Senha não informada", required=True)


class Login(Resource):
  def post(self):
    args = parser.parse_args()
    user = Usuario.query.filter_by(email=args["email"]).first()
    if user is None:
      logger.error("Email incorreto ou inexistente")

      codigo = Message(1, "Email incorreto ou inexistente")
      return marshal(codigo, msgFields), 404

    if not user.verify_password(args['senha']):
      codigo = Message(1, "Senha Incorreta ou inexistente")
      return marshal(codigo, msgFields), 404

    token = token_creator.create(user.tipo)


    return {"token": token, "tipo":user.tipo}, 200
