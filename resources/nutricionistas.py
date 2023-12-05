import os
import re
from io import BytesIO

from flask import make_response
from flask_restful import Resource, marshal, reqparse
from password_strength import PasswordPolicy
from PIL import Image
from sqlalchemy.exc import IntegrityError
from validate_docbr import CPF
from werkzeug.datastructures import FileStorage
from werkzeug.security import generate_password_hash

from helpers.auth.token_verifier import token_verify
from helpers.database import db
from helpers.logger import logger
from model.atleta import Atleta
from model.imgUsuarios import ImgUsuarios
from model.mensagem import Message, msgFields, msgFieldsToken
from model.notificacaoNutricionista import (NotificacaoNutricionista,
                                            notificacaoNutricionistaFields)
from model.nutricionista import (Nutricionista,
                                 nutricionistaAssociatedFieldsToken,
                                 nutricionistaFieldsToken,
                                 nutricionistaPagination)

parser = reqparse.RequestParser()
parserState = reqparse.RequestParser()
parserFiles = reqparse.RequestParser()

parser.add_argument("nome", type=str, help="Nome não informado", required=False)
parser.add_argument("sobrenome", type=str, help="Sobrenome não informado", required=False)

parser.add_argument("email", type=str, help="email não informado", required=False)
parser.add_argument("senha", type=str, help="senha não informado", required=False)
parser.add_argument("cpf", type=str, help="cpf não informado", required=False)
parser.add_argument("crn", type=str, help="crn não informado", required=False)
parser.add_argument("novaSenha", type=str, help="nova senha não informado", required=False)

parserFiles.add_argument('fotoPerfil', type=FileStorage, location='files')

parserState.add_argument("situacao", type=str, help="situação não informado", required=True)
parserState.add_argument("idNotificacao", type=str, help="id da notificacao não informado", required=True)

"056.998.308-80"
"290.297.910-04"
"607.298.816-44"
"167.167.991-17"
"677.986.197-98"

"CRN1-1234"
"CRN2-5678"
"CRN3-9012"
"CRN4-3456"
"CRN5-7890"

cpfValidate = CPF()

padrao_email = r'^[\w\.-]+@[\w\.-]+\.\w+$'

policy = PasswordPolicy.from_names(
  length =8,
  uppercase = 1,
  numbers=1,
  special=1
)

class Nutricionistas(Resource):
  # @token_verify
  def get(self):
    # if tipo != 'Administrador':
    #   logger.error("Usuario sem autorizacao para acessar os nutricionistas")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
    #   return marshal(codigo, msgFields), 403

    logger.info("Nutricionistas listados com sucesso")
    nutricionista = Nutricionista.query.all()
    data = {"nutricionista": nutricionista, "token": None}

    return marshal(data, nutricionistaFieldsToken), 200

  # @token_verify
  def post(self):
    # if tipo != 'Administrador' and tipo != 'Nutricionista':
    #   logger.error("Usuario sem autorizacao para acessar os nutricionistas")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
    #   return marshal(codigo, msgFields), 403
    args = parser.parse_args()

    try:
      with db.session.begin():
        fotoPerfil = None
        if len(args["nome"]) == 0:
          logger.info("Nome não informado")

          codigo = Message(1, "Nome não informado")
          return marshal(codigo, msgFields), 400

        if len(args["sobrenome"]) == 0:
          logger.info("Sobrenome não informado")

          codigo = Message(1, "Sobrenome não informado")
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

        if not args['crn']:
          codigo = Message(1, "CRN não informada")
          return marshal(codigo, msgFields), 400

        if int(len((args['crn']))) <= 3:
          codigo = Message(1, "CRN invalido")
          return marshal(codigo, msgFields), 400

        nutricionista = Nutricionista(args["nome"], args["sobrenome"], args["email"], args["senha"], args["cpf"], args["crn"])

        db.session.add(nutricionista)
        db.session.flush()

        imgUsuario = ImgUsuarios(fotoPerfil, nutricionista.usuario_id)

        db.session.add(imgUsuario)

      data = {"nutricionista":nutricionista, "token": None}

      logger.info(f"Nutricionista de id: {nutricionista.id} criado com sucesso")
      return marshal(data, nutricionistaFieldsToken), 201

    except IntegrityError as e:
      if "cpf" in str(e.orig):
        codigo = Message(1, "CPF já cadastrado no sistema")
        return marshal(codigo, msgFields), 400

      elif "email" in str(e.orig):
        codigo = Message(1, "Email já cadastrado no sistema")
        return marshal(codigo, msgFields), 400

      elif "crn" in str(e.orig):
        codigo = Message(1, "CRN já cadastrado no sistema")
        return marshal(codigo, msgFields), 400
    except:
      logger.error("Erro ao cadastrar o Nutricionista")

      codigo = Message(2, "Erro ao cadastrar o Nutricionista")
      return marshal(codigo, msgFields), 400

class NutricionistaId(Resource):
  # @token_verify
  def get(self, id):
    # if tipo != 'Administrador' and tipo != 'Nutricionista':
    #   logger.error("Usuario sem autorizacao para acessar os nutricionistas")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
    #   return marshal(codigo, msgFields), 403

    nutricionista = Nutricionista.query.get(id)

    if nutricionista is None:
      logger.error(f"Nutricionista de id: {id} nao encotrado")

      codigo = Message(1, f"Nutricionista de id: {id} não encontrado")
      return marshal(codigo, msgFields), 404

    data = {"nutricionista": nutricionista, "token": None}

    logger.info(f"Nutricionista de id: {id} listado com sucesso")
    return marshal(data, nutricionistaAssociatedFieldsToken), 200

  # @token_verify
  def put(self, id):
    # if tipo != 'Administrador' and tipo != 'Nutricionista':
    #   logger.error("Usuario sem autorizacao para acessar os nutricionistas")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
    #   return marshal(codigo, msgFields), 403

    args = parser.parse_args()

    try:
      nutricionistaBD = Nutricionista.query.get(id)
      if nutricionistaBD is None:
        logger.error(f"Nutricionista de id: {id} nao encotrado")

        codigo = Message(1, f"Nutricionista de id: {id} não encontrado")
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

      if not args['crn']:
        codigo = Message(1, "CRN não informada")
        return marshal(codigo, msgFields), 400

      if int(len((args['crn']))) <= 3:
        codigo = Message(1, "CRN invalido")
        return marshal(codigo, msgFields), 400

      nutricionistaBD.nome = args["nome"]
      nutricionistaBD.sobrenome = args["sobrenome"]
      nutricionistaBD.email = args["email"]
      nutricionistaBD.cpf = args["cpf"]
      nutricionistaBD.crn = args["crn"]

      db.session.add(nutricionistaBD)
      db.session.commit()

      data = {"nutricionista": nutricionistaBD, "token": None}

      logger.info(f"Nutricionista de id: {id} atualizado com sucesso")
      return marshal(data, nutricionistaFieldsToken), 200

    except IntegrityError as e:
      if "cpf" in str(e.orig):
        codigo = Message(1, "CPF já cadastrado no sistema")
        return marshal(codigo, msgFields), 400

      elif "email" in str(e.orig):
        codigo = Message(1, "Email já cadastrado no sistema")
        return marshal(codigo, msgFields), 400

      elif "crn" in str(e.orig):
        codigo = Message(1, "CRN já cadastrado no sistema")
        return marshal(codigo, msgFields), 400
    except:
      logger.error("Erro ao cadastrar o Nutricionista")

      codigo = Message(2, "Erro ao cadastrar o Nutricionista")
      return marshal(codigo, msgFields), 400

  # @token_verify
  def patch(self, id):
    # if tipo != 'Administrador' and tipo != 'Nutricionista':
    #   logger.error("Usuario sem autorizacao para acessar os nutricionistas")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
    #   return marshal(codigo, msgFields), 403

    args = parser.parse_args()
    try:
      nutricionistaBD = Nutricionista.query.get(id)

      if nutricionistaBD is None:
        logger.error(f"Nutricionista de id: {id} nao encotrado")

        codigo = Message(1, f"Nutricionista de id: {id} não encontrado")
        return marshal(codigo, msgFields), 404

      if not nutricionistaBD.verify_password(args["senha"]):
        codigo = Message(1, "Senha incorreta ou inexistente")
        return marshal(codigo, msgFields), 404

      if not args['novaSenha']:
        codigo = Message(1, "nova senha não informada")
        return marshal(codigo, msgFields), 400

      verifySenha = policy.test(args['novaSenha'])
      if len(verifySenha) != 0:
        codigo = Message(1, "Senha no formato errado")
        return marshal(codigo, msgFields), 400

      nutricionistaBD.senha = generate_password_hash(args['novaSenha'])

      db.session.add(nutricionistaBD)
      db.session.commit()

      logger.info("Senha alterada com sucesso")
      codigo = Message(0, "Senha alterada com sucesso")

      data = {"msg": codigo, "token": None}
      return marshal(data, msgFieldsToken), 200

    except:
      logger.error("Erro ao atualizar a senha do Personal Trainer")
      codigo = Message(2, "Erro ao atualizar a senha do Personal Trainer")
      return marshal(codigo, msgFields), 400
  # @token_verify
  def delete(self, id):
    # if tipo != 'Administrador' and tipo != 'Nutricionista':
    #   logger.error("Usuario sem autorizacao para acessar os nutricionistas")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
    #   return marshal(codigo, msgFields), 403

    nutricionista = Nutricionista.query.get(id)

    if nutricionista is None:
        logger.error(f"Nutricionista de id: {id} nao encotrado")

        codigo = Message(1, f"Nutricionista de id: {id} não encontrado")
        return marshal(codigo, msgFields), 404

    for atleta in nutricionista.atletas:
      notificacaoAtleta = NotificacaoNutricionista.query.filter_by(atleta_id=atleta.usuario_id).first()
      notificacaoAtleta.solicitacao= False
      db.session.add(notificacaoAtleta)

    db.session.delete(nutricionista)
    db.session.commit()

    logger.info(f"Nutricionista de id: {id} deletado com sucesso")
    return {"token": None}, 200

class NutricionistaImg(Resource):
  def get(self, id):
    img_io = BytesIO()

    usuario = ImgUsuarios.query.filter_by(usuario_id=id).first()

    if usuario is None:
      logger.error(f"Usuario de id: {id} nao encontrado")
      codigo = Message(1, f"Usuario de id: {id} nao encontrado")
      return marshal(codigo, msgFields), 404

    if usuario.fotoPerfil is None: return None, 200

    fotoPerfil = Image.open(BytesIO(usuario.fotoPerfil))
    fotoPerfil.save(img_io, 'PNG')
    img_io.seek(0)
    response = make_response(img_io.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response

  def put(self, id):
    args = parserFiles.parse_args()

    try:
      userDB = ImgUsuarios.query.filter_by(usuario_id=id).first()
      if userDB is None:
        logger.error(f'Usuario de id: {id} nao encontrado')
        codigo = Message(1, f"Usuario de id: {id} nao encontrado")
        return marshal(codigo, msgFields), 404

      maxSizeImage = 2 *1024 * 1024
      newFoto = args['fotoPerfil']
      if newFoto is None:
        logger.error("campo fotoPerfil nao informado")
        codigo = Message(1, "campo fotoPerfil nao informado")
        return marshal(codigo, msgFields), 404

      try:
        Image.open(newFoto)
      except IOError:
        logger.error("O arquivo nao e uma imagem")
        codigo = Message(1, "O arquivo não é uma imagem")
        return marshal(codigo, msgFields), 404

      newFoto.stream.seek(0, os.SEEK_END)
      fileSize = newFoto.stream.tell()
      if fileSize > maxSizeImage:
        logger.error("O arquivo e muito grande")
        codigo = Message(1, "O arquivo é muito grande")
        return marshal(codigo, msgFields), 400

      newFoto.stream.seek(0)
      fotoPerfil = newFoto.stream.read()

      userDB.fotoPerfil = fotoPerfil

      logger.info("Foto do nutricionista atualizada com sucesso")

      db.session.add(userDB)
      db.session.commit()

      return {}, 204
    except:
      logger.error("Erro ao atualizar a imagem do nutricionista")

      codigo = Message(2, "Erro ao atualizar a imagem do nutricionista")
      return marshal(codigo, msgFields), 400

  def delete(self, id):
    userDB = ImgUsuarios.query.filter_by(usuario_id=id).first()

    if userDB is None:
      logger.error(f'Imagem do nutricionista de id: {id} nao encontrada')
      codigo = Message(1, f"Imagem do nutricionista de id: {id} nao encontrada")
      return marshal(codigo, msgFields), 404

    userDB.fotoPerfil= None

    db.session.add(userDB)
    db.session.commit()

    return {}, 200

class NutricionistaNotificacoes(Resource):
  @token_verify
  def get(self, tipo, refreshToken, user_id):
    notificacoes = NotificacaoNutricionista.query.filter(
      NotificacaoNutricionista.solicitacao==False,
      ~NotificacaoNutricionista.nutricionistas_rejeitados.any(Nutricionista.usuario_id==user_id)
      # ~ operador de negação
    ).all()

    logger.info(f"Notificacoes dos nutricionista listado com sucesso")
    return marshal(notificacoes, notificacaoNutricionistaFields)

class NutricionistaNotificacoesId(Resource):
  @token_verify
  def get(self, tipo, refreshToken, user_id, id):
    nutricionista = Nutricionista.query.get(user_id)
    if nutricionista is None:
      logger.error(f"Nutricionista de id: {user_id} nao encontrado")

      codigo = Message(1, f"Nutricionista de id: {user_id} nao encontrado")
      return marshal(codigo, msgFields), 404

    notificacao = NotificacaoNutricionista.query.filter(
      NotificacaoNutricionista.solicitacao==False,
      NotificacaoNutricionista.id==id,
      ~NotificacaoNutricionista.nutricionistas_rejeitados.any(Nutricionista.usuario_id==user_id)
      # ~ operador de negação
    ).first()

    if notificacao is None:
      logger.error(f"Notificacao de id: {id} nao encontrada")

      codigo = Message(1, f"Notificacao de id: {id} nao encontrada")
      return marshal(codigo, msgFields), 404

    logger.info(f"Notificacao de id: {id} listado com sucesso")
    return marshal(notificacao, notificacaoNutricionistaFields)

  def delete(self, id):
    notificacao = NotificacaoNutricionista.query.get(id)

    if notificacao is None:
      logger.error(f"Notificacao de id: {id} nao encontrada")

      codigo = Message(1, f"Notificacao de id: {id} nao encontrada")
      return marshal(codigo, msgFields), 404

    db.session.delete(notificacao)
    db.session.commit()

    logger.info(f"Notificacao de id: {id} deletado com sucesso")
    return {}, 200

class NutricionistaNotificacaoState(Resource):
  @token_verify
  def patch(self, tipo, refreshToken, user_id):
    args = parserState.parse_args()
    notificacao = NotificacaoNutricionista.query.filter(
      NotificacaoNutricionista.solicitacao==False,
      NotificacaoNutricionista.id==args["idNotificacao"],
      ~NotificacaoNutricionista.nutricionistas_rejeitados.any(Nutricionista.usuario_id==user_id)
    ).first()

    if notificacao is None:
      logger.error(f"Notificacao de id: {id} nao encontrada")

      codigo = Message(1, f"Notificacao de id: {id} nao encontrada")
      return marshal(codigo, msgFields), 404

    nutricionista = Nutricionista.query.get(user_id)

    if args["situacao"] == "aceitar":
      atleta = Atleta.query.get(notificacao.atleta_id)

      nutricionista.atletas.append(atleta)
      atleta.nutricionista_id = nutricionista.usuario_id
      notificacao.solicitacao = True

      db.session.add(notificacao)
      db.session.add(nutricionista)
      db.session.add(atleta)
      db.session.commit()

      logger.info(f"O nutricionista aceitou o atleta: {notificacao.nome} como seu aluno")
      codigo = Message(0, f"Voce aceitou o atleta: {notificacao.nome} como seu aluno")
      return marshal(codigo, msgFields), 200

    elif args["situacao"] == "rejeitar":
      notificacao.nutricionistas_rejeitados.append(nutricionista)

      db.session.add(notificacao)
      db.session.commit()

      logger.info(f"O nutriconista rejeitou o atleta: {notificacao.nome}")
      codigo = Message(0, f"Você rejeitou o atleta: {notificacao.nome}")
      return marshal(codigo, msgFields), 200

class NutricionistaNome(Resource):
  # @token_verify
  def get(self, nome):
    # if tipo != 'Administrador':
    #   logger.error("Usuario sem autorizacao para acessar os nutricionistas")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
      # return marshal(codigo, msgFields), 403

    nutricionista = Nutricionista.query.filter(Nutricionista.nome.ilike(f"%{nome}%")).all()

    data = {"nutricionista": nutricionista, "token": None}

    logger.info(f"Nutricionista como nomes: {nome} listado com sucesso")
    return marshal(data, nutricionistaFieldsToken), 200

class NutricionistaPagination(Resource):
  def get(self, id, max_itens):
    nutricionistas = Nutricionista.query.all()
    nutricionistasPagination = Nutricionista.query.paginate(page=id, per_page=max_itens, error_out=False)

    data = {"nutricionistas":nutricionistasPagination.items, "totalNutricionistas": len(nutricionistas)}

    logger.info("Nutricionistas listados com sucesso")
    return marshal(data, nutricionistaPagination), 200
