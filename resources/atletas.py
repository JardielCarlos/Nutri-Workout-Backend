from flask_restful import Resource, marshal, reqparse
from helpers.logger import logger
from helpers.database import db
from werkzeug.security import generate_password_hash
from helpers.auth.token_verifier import token_verify
from sqlalchemy.exc import IntegrityError
from password_strength import PasswordPolicy
from validate_docbr import CPF
import re

from model.atleta import Atleta, atletaFieldsToken
from model.mensagem import Message, msgFields, msgFieldsToken

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

class Atletas(Resource):
  @token_verify
  def get(self, tipo, refreshToken):
    if tipo != 'Administrador':
      logger.error("Usuario sem autorizacao para acessar os atletas")

      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    
    atleta = Atleta.query.all()
    data = {"atleta": atleta, "token": refreshToken}
    logger.info("Atletas listados com sucesso")
    return marshal(data, atletaFieldsToken), 200
  
  @token_verify
  def post(self, tipo, refreshToken):
    if tipo != 'Administrador' and tipo != 'Atleta':
      logger.error("Usuario sem autorizacao para acessar os atletas")

      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
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
      
      atleta = Atleta(args["nome"], args["email"], args["senha"], args["cpf"])

      db.session.add(atleta)
      db.session.commit()

      data = {"atleta": atleta, "token": refreshToken}

      logger.info(f"Atleta de id: {atleta.id} criado com sucesso")
      return marshal(data, atletaFieldsToken), 201
    
    except IntegrityError as e:
      if 'cpf' in str(e.orig):
        codigo = Message(1, "CPF já cadastrado no sistema")
        return marshal(codigo, msgFields), 400
      
      elif 'email' in str(e.orig):
        codigo = Message(1, "Email já cadastrado no sistema")
        return marshal(codigo, msgFields), 400

    except:
      logger.error("Erro ao cadastrar o Atleta")

      codigo = Message(2, "Erro ao cadastrar o Atleta")
      return marshal(codigo, msgFields), 400
    
class AtletaId(Resource):
  @token_verify
  def get(self, tipo, refreshToken, id):
    if tipo != 'Administrador' and tipo != 'Atleta':
      logger.error("Usuario sem autorizacao para acessar os atletas")

      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    
    atleta = Atleta.query.get(id)

    if atleta is None:
      logger.error(f"Atleta de id: {id} nao encotrado")

      codigo = Message(1, f"Atleta de id: {id} não encontrado")
      return marshal(codigo, msgFields), 404
    
    data = {"atleta": atleta, "token": refreshToken}

    logger.info(f"Atleta de id: {id} listado com sucesso")
    return marshal(data, atletaFieldsToken), 200
  
  @token_verify
  def put(self, tipo, refreshToken, id):
    if tipo != 'Administrador' or tipo != 'Atleta':
      logger.error("Usuario sem autorizacao para acessar os atletas")

      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    
    args = parser.parse_args()

    try:
      atletaBD = Atleta.query.get(id)
      if atletaBD is None:
        logger.error(f"Atleta de id: {id} nao encotrado")

        codigo = Message(1, f"Atleta de id: {id} não encontrado")
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

      atletaBD.nome = args["nome"]
      atletaBD.email = args["email"]
      atletaBD.cpf = args["cpf"],

      db.session.add(atletaBD)
      db.session.commit()
      
      data = {"atleta": atletaBD, "token": refreshToken}

      logger.info(f"Atleta de id: {id} atualizado com sucesso")
      return marshal(data, atletaFieldsToken), 200
    
    except IntegrityError as e:
      if 'cpf' in str(e.orig):
        codigo = Message(1, "CPF já cadastrado no sistema")
        return marshal(codigo, msgFields), 400
      
      elif 'email' in str(e.orig):
        codigo = Message(1, "Email já cadastrado no sistema")
        return marshal(codigo, msgFields), 400
    
    except:
      logger.error("Erro ao atulizar o atleta")
      codigo = Message(2, "Erro ao atualizar o atleta")
      return marshal(codigo, msgFields), 400
    
  @token_verify
  def patch(self, tipo, refreshToken, id):
    if tipo != 'Administrador' or tipo != 'Atleta':
      logger.error("Usuario sem autorizacao para acessar os atletas")

      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    
    args = parser.parse_args()
    
    try:
      atleta = Atleta.query.get(id)
      if atleta is None:
        logger.error(f"Atleta de id: {id} nao encotrado")

        codigo = Message(1, f"Atleta de id: {id} não encontrado")
        return marshal(codigo, msgFields), 404

      if not atleta.verify_password(args["senha"]):
        codigo = Message(1, "Senha incorreta ou inexistente")
        return marshal(codigo, msgFields), 404
      
      if not args['novaSenha']:
        codigo = Message(1, "nova senha não informada")
        return marshal(codigo, msgFields), 400
      
    
      atleta.senha = generate_password_hash(args["novaSenha"])

      db.session.add(atleta)
      db.session.commit()

      logger.info("Senha alterada com sucesso")
      codigo = Message(0, "Senha alterada com sucesso")
      data = {"msg": codigo, "token": refreshToken}
      return marshal(data, msgFieldsToken), 200
    except:
      logger.error("Erro ao atualizar a senha do atleta")
      codigo = Message(2, "Erro ao atualizar a senha do atleta")
      return marshal(codigo, msgFields), 400

  @token_verify
  def delete(self, tipo, refreshToken, id):
    if tipo != 'Administrador' and tipo != 'Atleta':
      logger.error("Usuario sem autorizacao para acessar os atletas")

      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    atleta = Atleta.query.get(id)

    if atleta is None:
      logger.error(f"Atleta de id: {id} nao encotrado")

      codigo = Message(1, f"Atleta de id: {id} não encontrado")
      return marshal(codigo, msgFields), 404
    
    db.session.delete(atleta)
    db.session.commit()

    logger.info(f"Atleta de id: {id} deletado com sucesso")
    return {"token": refreshToken}, 200
  
class AtletaNome(Resource):
  @token_verify
  def get(self, tipo, refreshToken, nome):
    if tipo != 'Administrador':
      logger.error("Usuario sem autorizacao para acessar os atletas")

      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    
    atletaNome = Atleta.query.filter(Atleta.nome.ilike(f"%{nome}%")).all()

    data = {"atleta": atletaNome, "token": refreshToken}

    logger.info(f"Atletas com nomes: {nome} listados com sucesso")
    return marshal(data, atletaFieldsToken), 200
