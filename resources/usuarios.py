from flask_restful import Resource, marshal, reqparse
from helpers.logger import logger
from helpers.database import db
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from password_strength import PasswordPolicy
import re

from model.usuario import Usuario, userFields
from model.mensagem import Message, msgFields

parser = reqparse.RequestParser()

parser.add_argument("nome", type=str, help="Nome não informado", required=False)
parser.add_argument("email", type=str, help="email não informado", required=False)
parser.add_argument("senha", type=str, help="senha não informado", required=False)
parser.add_argument("novaSenha", type=str, help="nova senha não informado", required=False)

padrao_email = r'^[\w\.-]+@[\w\.-]+\.\w+$'
policy = PasswordPolicy.from_names(
  length =8,
  uppercase = 1,
  numbers=1,
  special=1
)

class Usuarios(Resource):
  def get(self):
    return marshal(Usuario.query.all(), userFields), 200
  
  def post(self):
    args = parser.parse_args()

    try:
      if len(args["nome"]) == 0:
        logger.info("Nome não informado")

        codigo = Message(1, "Nome não informado")
        return marshal(codigo, msgFields), 400
      
      if not args['email']:
        codigo = Message(1, "email não informada")
        return marshal(codigo, msgFields), 400
      
      if re.match(padrao_email, args['email']) == None:
        codigo = Message(1, "Email no formato errado")
        return marshal(codigo, msgFields), 400
      
      if not args['senha']:
        codigo = Message(1, "Senha não informada")
        return marshal(codigo, msgFields), 400
      
      verifySenha = policy.test(args['senha'])
      if len(verifySenha) != 0:
        codigo = Message(1, "Senha no formato errado")
        return marshal(codigo, msgFields), 400
      
      usuario = Usuario(args["nome"], args["email"], args["senha"])

      db.session.add(usuario)
      db.session.commit()

      logger.info(f"Usuario de id: {usuario.id} criado com sucesso")
      return marshal(usuario, userFields), 201
    
    except IntegrityError:
      codigo = Message(1, "Email ja cadastrado no sistema")
      return marshal(codigo, msgFields), 400

    except:
      logger.error("Erro ao cadastrar o Usuario")

      codigo = Message(2, "Erro ao cadastrar o Usuario")
      return marshal(codigo, msgFields), 400
    
class UsuarioId(Resource):
  def get(self, id):
    usuario = Usuario.query.get(id)

    if usuario is None:
      logger.error(f"Usuario de id: {id} nao encotrado")

      codigo = Message(1, f"Usuario de id: {id} não encontrado")
      return marshal(codigo, msgFields), 404
    
    logger.info(f"Usuario de id: {id} listado com sucesso")
    return marshal(usuario, userFields), 200
  
  def put(self, id):
    args = parser.parse_args()

    try:
      usuarioBD = Usuario.query.get(id)
      if usuarioBD is None:
        logger.error(f"Usuario de id: {id} nao encotrado")

        codigo = Message(1, f"Usuario de id: {id} não encontrado")
        return marshal(codigo, msgFields), 404
      
      if len(args['nome']) == 0:
        logger.info("Nome nao informado")

        codigo = Message(1, "Nome nao informado")
        return marshal(codigo, msgFields), 400
      
      if not args['email']:
        codigo = Message(1, "email não informado")
        return marshal(codigo, msgFields), 400
      
      if re.match(padrao_email, args['email']) == None:
        codigo = Message(1, "Email no formato errado")
        return marshal(codigo, msgFields), 400
      
      usuarioBD.nome = args["nome"]
      usuarioBD.email = args["email"]

      db.session.add(usuarioBD)
      db.session.commit()
      
      logger.info(f"Usuario de id: {id} atualizado com sucesso")
      return marshal(usuarioBD, userFields), 200
    
    except IntegrityError:
      codigo = Message(1, "Email ja cadastrado no sistema")
      return marshal(codigo, msgFields), 400
    
    except:
      logger.error("Erro ao atulizar o usuario")
      codigo = Message(2, "Erro ao atualizar o usuario")
      return marshal(codigo, msgFields), 400
    
  def patch(self, id):
    args = parser.parse_args()
    
    try:
      usuario = Usuario.query.get(id)
      if usuario is None:
        logger.error(f"Usuario de id: {id} nao encotrado")

        codigo = Message(1, f"Usuario de id: {id} não encontrado")
        return marshal(codigo, msgFields), 404

      if not usuario.verify_password(args["senha"]):
        codigo = Message(1, "Senha Incorreta ou inexistente")
        return marshal(codigo, msgFields), 404
      
      if not args['novaSenha']:
        codigo = Message(1, "nova senha não informada")
        return marshal(codigo, msgFields), 400
      
      verifySenha = policy.test(args['novaSenha'])
      if len(verifySenha) != 0:
        codigo = Message(1, "Senha no formato errado")
        return marshal(codigo, msgFields), 400
    
      usuario.senha = generate_password_hash(args["novaSenha"])

      db.session.add(usuario)
      db.session.commit()

      logger.info("Senha alterada com sucesso")
      codigo = Message(0, "Senha alterada com sucesso")
      return marshal(codigo, msgFields), 200
    except:
      logger.error("Erro ao atualizar a senha do usuario")
      codigo = Message(2, "Erro ao atualizar a senha do usuario")
      return marshal(codigo, msgFields), 400


  def delete(self, id):
    usuario = Usuario.query.get(id)

    if usuario is None:
      logger.error(f"Usuario de id: {id} nao encotrado")

      codigo = Message(1, f"Usuario de id: {id} não encontrado")
      return marshal(codigo, msgFields), 404
    
    db.session.delete(usuario)
    db.session.commit()

    logger.info(f"Usuario de id: {id} deletado com sucesso")
    return {}, 200
