from flask_restful import Resource, marshal, reqparse
from helpers.logger import logger
from helpers.database import db
from werkzeug.security import generate_password_hash
from helpers.auth.token_verifier import token_verify
from sqlalchemy.exc import IntegrityError
from password_strength import PasswordPolicy
from validate_docbr import CPF
import re

from model.mensagem import Message, msgFields
from model.administrador import Administrador, administradorFields

parser = reqparse.RequestParser()

parser.add_argument("nome", type=str, help="Nome não informado", required=False)
parser.add_argument("email", type=str, help="email não informado", required=False)
parser.add_argument("senha", type=str, help="senha não informado", required=False)
parser.add_argument("cpf", type=str, help="cpf não informado", required=False)
parser.add_argument("novaSenha", type=str, help="nova senha não informado", required=False)

padrao_email = r'^[\w\.-]+@[\w\.-]+\.\w+$'
policy = PasswordPolicy.from_names(
  length =8,
  uppercase = 1,
  numbers=1,
  special=1
)

cpfValidate = CPF()

"056.998.308-80"
"290.297.910-04"
"607.298.816-44"
"167.167.991-17"
"677.986.197-98"

class Administradores(Resource):
  @token_verify
  def get(self, tipo, refreshToken):
    if tipo != 'Administrador':
      logger.error("Usuario sem autorizacao para acessar os gestores")

      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    
    logger.info("Administradores listado com sucesso")
    return marshal(Administrador.query.all(), administradorFields), 200
  
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
      
      if not args["cpf"]:
        codigo = Message(1, "cpf não informado")
        return marshal(codigo, msgFields), 400
      
      if not cpfValidate.validate(args["cpf"]):
        logger.error(f"CPF {args['cpf']} não valido")

        codigo = Message(1, f"CPF {args['cpf']} não valido")
        return marshal(codigo, msgFields), 400
      
      if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', args["cpf"]):
        logger.error(f"CPF {args['cpf']} no formato errado")

        codigo = Message(1, "CPF no formato errado")
        return marshal(codigo, msgFields), 400

      if not args['senha']:
        codigo = Message(1, "Senha não informada")
        return marshal(codigo, msgFields), 400
      
      verifySenha = policy.test(args['senha'])
      if len(verifySenha) != 0:
        codigo = Message(1, "Senha no formato errado")
        return marshal(codigo, msgFields), 400
      
      administrador = Administrador(args["nome"], args["email"], args["senha"], args["cpf"])
      
      db.session.add(administrador)
      db.session.commit()

      logger.info(f"Administrador de id: {administrador.id} criado com sucesso")
      return marshal(administrador, administradorFields), 201
    except IntegrityError as e:
      if 'cpf' in str(e.orig):
        codigo = Message(1, "CPF já cadastrado no sistema")
        return marshal(codigo, msgFields), 400
      
      elif 'email' in str(e.orig):
        codigo = Message(1, "Email já cadastrado no sistema")
        return marshal(codigo, msgFields), 400

    except:
      logger.error("Erro ao cadastrar o Administrador")

      codigo = Message(2, "Erro ao cadastrar o Administrador")
      return marshal(codigo, msgFields), 400

class AdministradorId(Resource):
  def get(self, id):
    administrador = Administrador.query.get(id)

    if administrador is None:
      logger.info(f"Administrador de id: {id} nao encontrado")

      codigo = Message(1, f"Administrador de id: {id} nao encontrado")
      return marshal(codigo, msgFields), 400
    
    logger.info(f"Administrador de id: {id} listado com sucesso")
    return marshal(administrador, administradorFields), 200

  def put(self, id):
    args = parser.parse_args()

    try:
      administradorBD = Administrador.query.get(id)

      if administradorBD is None:
        logger.error(f"Administrador de id: {id} nao encotrado")

        codigo = Message(1, f"Administrador de id: {id} não encontrado")
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
      
      if not args["cpf"]:
        codigo = Message(1, "cpf não informado")
        return marshal(codigo, msgFields), 400
      
      if not cpfValidate.validate(args["cpf"]):
        logger.error(f"CPF {args['cpf']} não valido")

        codigo = Message(1, f"CPF {args['cpf']} não valido")
        return marshal(codigo, msgFields), 400
      
      if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', args["cpf"]):
        logger.error(f"CPF {args['cpf']} no formato errado")

        codigo = Message(1, "CPF no formato errado")
        return marshal(codigo, msgFields), 400
      
      administradorBD.nome = args["nome"]
      administradorBD.email = args["email"]
      administradorBD.cpf = args["cpf"],

      db.session.add(administradorBD)
      db.session.commit()
      
      logger.info(f"Administrador de id: {id} atualizado com sucesso")
      return marshal(administradorBD, administradorFields), 200
    
    except IntegrityError as e:
      if 'cpf' in str(e.orig):
        codigo = Message(1, "CPF já cadastrado no sistema")
        return marshal(codigo, msgFields), 400
      
      elif 'email' in str(e.orig):
        codigo = Message(1, "Email já cadastrado no sistema")
        return marshal(codigo, msgFields), 400
    except:
      logger.error("Erro ao atulizar o Administrador")
      codigo = Message(2, "Erro ao atualizar o Administrador")
      return marshal(codigo, msgFields), 400
    
  def patch(self, id):
    args = parser.parse_args()
    try:
      administrador = Administrador.query.get(id)
      if administrador is None:
        logger.error(f"Administrador de id: {id} nao encotrado")

        codigo = Message(1, f"Administrador de id: {id} não encontrado")
        return marshal(codigo, msgFields), 404
      
      if not administrador.verify_password(args["senha"]):
        codigo = Message(1, "Senha incorreta ou inexistente")
        return marshal(codigo, msgFields), 404
      
      if not args['novaSenha']:
        codigo = Message(1, "nova senha não informada")
        return marshal(codigo, msgFields), 400
      
      verifySenha = policy.test(args['novaSenha'])
      if len(verifySenha) != 0:
        codigo = Message(1, "Senha no formato errado")
        return marshal(codigo, msgFields), 400
      
      administrador.senha = generate_password_hash(args["novaSenha"])

      db.session.add(administrador)
      db.session.commit()

      logger.info("Senha alterada com sucesso")
      codigo = Message(0, "Senha alterada com sucesso")
      return marshal(codigo, msgFields), 200
    except:
      logger.error("Erro ao atualizar a senha do Administrador")
      codigo = Message(2, "Erro ao atualizar a senha do Administrador")
      return marshal(codigo, msgFields), 400

  def delete(self, id):
    administrador = Administrador.query.get(id)

    if administrador is None:
      logger.error(f"Administrador de id: {id} nao encotrado")

      codigo = Message(1, f"Administrador de id: {id} não encontrado")
      return marshal(codigo, msgFields), 404
    
    db.session.delete(administrador)
    db.session.commit()
    
    logger.info(f"Administrador de id: {id} deletado com sucesso")
    return {}, 200

class AdministradorNome(Resource):
  def get(self, nome):
    administradorNome = Administrador.query.filter(Administrador.nome.ilike(f"%{nome}%")).all()
    logger.info(f"Administrador com nomes: {nome} listado com sucesso")
    return marshal(administradorNome, administradorFields), 200