from flask_restful import Resource, marshal, reqparse
from helpers.logger import logger
from helpers.database import db
from sqlalchemy.exc import IntegrityError
from password_strength import PasswordPolicy
from werkzeug.security import generate_password_hash
from validate_docbr import CPF

from model.usuario import Usuario, userFields, usuarioFieldsPagination
from model.mensagem import msgFields, Message
import re

parser = reqparse.RequestParser()

parser.add_argument("nome", type=str, help="Nome não informado", required=False)
parser.add_argument("sobrenome", type=str, help="Sobrenome não informado", required=False)
parser.add_argument("email", type=str, help="email não informado", required=False)
parser.add_argument("cpf", type=str, help="Cpf não informado", required=False)
parser.add_argument("senha", type=str, help="senha não informado", required=False)
parser.add_argument("novaSenha", type=str, help="nova senha não informado", required=False)

padrao_email = r'^[\w\.-]+@[\w\.-]+\.\w+$'
policy = PasswordPolicy.from_names(
  length =8,
  uppercase = 1,
  numbers=1,
  special=1
)

cpfValidate = CPF()

class Usuarios(Resource):
  def get(self):
    usuarios = Usuario.query.all()
    logger.info("Usuarios listados com sucesso")
    return marshal(usuarios, userFields), 200

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
        logger.error(f"Usuario de id: {id} nao encontrado")

        codigo = Message(f"Usuario de id: {id} não encontrado")
        return marshal(codigo, msgFields), 404

      if len(args['nome']) == 0:
        logger.info("Nome nao informado")

        codigo = Message(1, "Nome nao informado")
        return marshal(codigo, msgFields), 400

      if len(args["sobrenome"]) == 0:
        logger.info("Sobrenome não informado")

        codigo = Message(1, "Sobrenome não informado")
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

      usuarioBD.nome = args["nome"]
      usuarioBD.sobrenome = args["sobrenome"]
      usuarioBD.email = args["email"]
      usuarioBD.cpf = args["cpf"]

      db.session.add(usuarioBD)
      db.session.commit()

      logger.info(f"Usuario de id: {id} atualizado com sucesso")
      return marshal(usuarioBD, userFields), 200
    except IntegrityError as e:
      if 'cpf' in str(e.orig):
        codigo = Message(1, "CPF já cadastrado no sistema")
        return marshal(codigo, msgFields), 400

      elif 'email' in str(e.orig):
        codigo = Message(1, "Email já cadastrado no sistema")
        return marshal(codigo, msgFields), 400

    except:
      logger.error("Erro ao atulizar o usuario")
      codigo = Message(2, "Erro ao atualizar o usuario")
      return marshal(codigo, msgFields), 400

  def patch(self, id):
    args = parser.parse_args()

    try:
      usuarioBD = Usuario.query.get(id)
      if usuarioBD is None:
        logger.error(f"Usuario de id: {id} nao encotrado")

        codigo = Message(1, f"Usuario de id: {id} não encontrado")
        return marshal(codigo, msgFields), 404

      if not usuarioBD.verify_password(args["senha"]):
        codigo = Message(1, "Senha incorreta ou inexistente")
        return marshal(codigo, msgFields), 404

      if not args['novaSenha']:
        codigo = Message(1, "nova senha não informada")
        return marshal(codigo, msgFields), 400

      usuarioBD.senha = generate_password_hash(args["novaSenha"])

      db.session.add(usuarioBD)
      db.session.commit()

      logger.info("Senha alterada com sucesso")
      codigo = Message(0, "Senha alterada com sucesso")
      return marshal(codigo, msgFields), 200
    except:
      logger.error("Erro ao atualizar a senha do usuario")
      codigo = Message(2, "Erro ao atualizar a senha do usuario")
      return marshal(codigo, msgFields), 400

  def delete(self, id):
    usuarioBD = Usuario.query.get(id)

    if usuarioBD is None:
      logger.error(f"Usuario de id: {id} nao encotrado")

      codigo = Message(1, f"Usuario de id: {id} não encontrado")
      return marshal(codigo, msgFields), 404

    db.session.delete(usuarioBD)
    db.session.commit()

    logger.info(f"Usuario de id: {id} deletado com sucesso")
    return {}, 200

class UsuarioNome(Resource):
  def get(self, nome):
    usuarioNome = Usuario.query.filter(Usuario.nome.ilike(f"%{nome}%")).all()

    logger.info(f"usuario com nomes: {nome} listados com sucesso")
    return marshal(usuarioNome, userFields), 200

class UsuarioPagination(Resource):
  def get(self, id):
    usuarios = Usuario.query.all()
    usuarioPagination = Usuario.query.paginate(page=id, per_page=10, error_out=False)

    data = {"usuarios": usuarioPagination.items, "totalAtletas": len(usuarios)}

    logger.info("Usuarios listados com sucesso")
    return marshal(data, usuarioFieldsPagination), 200
