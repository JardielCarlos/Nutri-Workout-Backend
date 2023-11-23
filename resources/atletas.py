import os
import re
from io import BytesIO

from flask import make_response
from flask_restful import Resource, marshal, reqparse, request
from password_strength import PasswordPolicy
from PIL import Image
from sqlalchemy.exc import IntegrityError
from validate_docbr import CPF
from werkzeug.datastructures import FileStorage
from werkzeug.security import generate_password_hash
from helpers.stripe_config import stripe

from helpers.auth.token_verifier import token_verify
from helpers.database import db
from helpers.logger import logger
from model.atleta import Atleta, atletaFieldsToken, atletasFieldsPagination
from model.imgUsuarios import ImgUsuarios
from model.mensagem import Message, msgFields, msgFieldsToken
from model.notificacaoNutricionista import NotificacaoNutricionista
from model.notificacaoPersonal import NotificacaoPersonal
from model.tabelaTreino import TabelaTreino, tabelaTreinoFields
from model.cardapio import Cardapio, cardapioFields

parser = reqparse.RequestParser()
parserFiles = reqparse.RequestParser()
# rabbitmqPublisher = RabbitmqPublisher()


parser.add_argument("nome", type=str, help="Nome não informado", required=False)
parser.add_argument("sobrenome", type=str, help="Sobrenome não informado", required=False)
parser.add_argument("email", type=str, help="email não informado", required=False)
parser.add_argument("senha", type=str, help="senha não informado", required=False)
parser.add_argument("cpf", type=str, help="cpf não informado", required=False)
parser.add_argument("novaSenha", type=str, help="nova senha não informado", required=False)
parserFiles.add_argument('fotoPerfil', type=FileStorage, location='files')

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
  # @token_verify
  def get(self):
    # if tipo != 'Administrador':
    #   logger.error("Usuario sem autorizacao para acessar os atletas")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
    #   return marshal(codigo, msgFields), 403

    atleta = Atleta.query.all()
    data = {"atleta": atleta, "token": None}
    logger.info("Atletas listados com sucesso")
    return marshal(data, atletaFieldsToken), 200

  # @token_verify
  def post(self):
    # if tipo != 'Administrador' and tipo != 'Atleta':
    #   logger.error("Usuario sem autorizacao para acessar os atletas")

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

        clienteStripe = stripe.Customer.create(
          name=args["nome"]+" "+args["sobrenome"],
          email=args["email"],
        )

        atleta = Atleta(args["nome"], args["sobrenome"], args["email"], args["senha"], args["cpf"])
        atleta.stripe_id = clienteStripe.id

        db.session.add(atleta)
        db.session.flush()

        imgUsuario = ImgUsuarios(fotoPerfil, atleta.usuario_id)

        db.session.add(imgUsuario)

      data = {"atleta": atleta, "token": None}

      logger.info(f"Atleta de id: {atleta.usuario_id} criado com sucesso")
      return marshal(data, atletaFieldsToken), 201

    except IntegrityError as e:
      if 'cpf' in str(e.orig):
        codigo = Message(1, "CPF já cadastrado no sistema")
        return marshal(codigo, msgFields), 400

      elif 'email' in str(e.orig):
        codigo = Message(1, "Email já cadastrado no sistema")
        return marshal(codigo, msgFields), 400

    # except:
    #   logger.error("Erro ao cadastrar o Atleta")

    #   codigo = Message(2, "Erro ao cadastrar o Atleta")
    #   return marshal(codigo, msgFields), 400

class AtletaId(Resource):
  # @token_verify
  def get(self, id):
    # if tipo != 'Administrador' and tipo != 'Atleta':
    #   logger.error("Usuario sem autorizacao para acessar os atletas")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
    #   return marshal(codigo, msgFields), 403

    atleta = Atleta.query.get(id)

    if atleta is None:
      logger.error(f"Atleta de id: {id} nao encotrado")

      codigo = Message(1, f"Atleta de id: {id} não encontrado")
      return marshal(codigo, msgFields), 404

    data = {"atleta": atleta, "token": None}

    logger.info(f"Atleta de id: {id} listado com sucesso")
    return marshal(data, atletaFieldsToken), 200

  # @token_verify
  def put(self, id):
    # if tipo != 'Administrador' or tipo != 'Atleta':
    #   logger.error("Usuario sem autorizacao para acessar os atletas")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
    #   return marshal(codigo, msgFields), 403

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

      atletaBD.nome = args["nome"]
      atletaBD.email = args["email"]
      atletaBD.cpf = args["cpf"],
      atletaBD.sobrenome = args["sobrenome"]

      db.session.add(atletaBD)
      db.session.commit()

      data = {"atleta": atletaBD, "token": None}

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

  # @token_verify
  def patch(self, id):
    # if tipo != 'Administrador' or tipo != 'Atleta':
    #   logger.error("Usuario sem autorizacao para acessar os atletas")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
    #   return marshal(codigo, msgFields), 403

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
      data = {"msg": codigo, "token": None}
      return marshal(data, msgFieldsToken), 200
    except:
      logger.error("Erro ao atualizar a senha do atleta")
      codigo = Message(2, "Erro ao atualizar a senha do atleta")
      return marshal(codigo, msgFields), 400

  # @token_verify
  def delete(self, id):
    # if tipo != 'Administrador' and tipo != 'Atleta':
    #   logger.error("Usuario sem autorizacao para acessar os atletas")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
    #   return marshal(codigo, msgFields), 403
    atleta = Atleta.query.get(id)

    if atleta is None:
      logger.error(f"Atleta de id: {id} nao encotrado")

      codigo = Message(1, f"Atleta de id: {id} não encontrado")
      return marshal(codigo, msgFields), 404

    stripe.Customer.delete(atleta.stripe_id)
    db.session.delete(atleta)
    db.session.commit()

    logger.info(f"Atleta de id: {id} deletado com sucesso")
    return {"token": None}, 200

class AtletaImg(Resource):
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

      maxSizeImage = 2 * 1024 * 1024
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

      logger.info("Foto do atleta atualizada com sucesso")

      db.session.add(userDB)
      db.session.commit()

      return {}, 204
    except:
      logger.error("Erro ao atualizar a imagem do atleta")

      codigo = Message(2, "Erro ao atualizar a imagem do atleta")
      return marshal(codigo, msgFields), 400

  def delete(self, id):
    userDB = ImgUsuarios.query.filter_by(usuario_id=id).first()

    if userDB is None:
      logger.error(f'Imagem do atleta de id: {id} nao encontrada')
      codigo = Message(1, f"Imagem do atleta de id: {id} nao encontrada")
      return marshal(codigo, msgFields), 404

    userDB.fotoPerfil= None

    db.session.add(userDB)
    db.session.commit()

    return {}, 200

class TabelaAtleta(Resource):
  @token_verify
  def get(self, tipo, refreshToken, user_id):
    if tipo != "Atleta":
      logger.error("Usuario sem autorizacao para acessar a tabela do atleta")

      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    atleta = Atleta.query.get(user_id)

    if atleta is None:
      logger.error(f"Atleta de id: {user_id} nao encontrado")

      codigo = Message(1,f"Atleta de id: {user_id} não encontrado")
      return marshal(codigo, msgFields), 400

    tabelaTreino = TabelaTreino.query.filter_by(atleta=atleta.usuario_id).first()
    if tabelaTreino is None:
      logger.error(f"Atleta de id: {atleta.usuario_id} nao possui uma tabela de treino")

      codigo = Message(1,"Você não possui uma tabela de treino")
      return marshal(codigo, msgFields), 404

    return marshal(tabelaTreino, tabelaTreinoFields), 200

class CardapioAtleta(Resource):
  @token_verify
  def get(self, tipo, refreshToken, user_id):
    if tipo != "Atleta":
      logger.error("Usuario sem autorizacao para acessar a tabela do atleta")

      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    atleta = Atleta.query.get(user_id)

    if atleta is None:
      logger.error(f"Atleta de id: {user_id} nao encontrado")

      codigo = Message(1,f"Atleta de id: {user_id} não encontrado")
      return marshal(codigo, msgFields), 400

    cardapio = Cardapio.query.filter_by(atleta=atleta.usuario_id).first()
    if cardapio is None:
      logger.error(f"Atleta de id: {atleta.usuario_id} nao possui um cardapio")

      codigo = Message(1,"Você não possui um cardapio")
      return marshal(codigo, msgFields), 404

    return marshal(cardapio, cardapioFields), 200

class AtletaNome(Resource):
  # @token_verify
  def get(self, nome):
    # if tipo != 'Administrador':
    #   logger.error("Usuario sem autorizacao para acessar os atletas")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
    #   return marshal(codigo, msgFields), 403

    atletaNome = Atleta.query.filter(Atleta.nome.ilike(f"%{nome}%")).all()

    data = {"atleta": atletaNome, "token": None}

    logger.info(f"Atletas com nomes: {nome} listados com sucesso")
    return marshal(data, atletaFieldsToken), 200

class RequestNutricionista(Resource):
  @token_verify
  def post(self, tipo, refreshToken, user_id):
    if tipo != "Atleta":
      logger.error("Usuario sem autorizacao para acessar a requisição de nutricionista")

      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    try:
      atleta = Atleta.query.get(user_id)

      msg = f"O atleta {atleta.nome} esta solicitando um(a) nutricionista, você gostaria de aceitar?"

      if atleta.nutricionista_id is not None:
        logger.error("Atleta ja possui um nutricionista")
        codigo = Message(1, "Atleta já possui um nutricionista")
        return marshal(codigo, msgFields), 400

      notificacao = NotificacaoNutricionista(atleta.nome, atleta.email, msg, atleta)

      db.session.add(notificacao)
      db.session.commit()

      logger.info(f"Solicitação de nutricionista realizada com sucesso pelo atleta de id: {atleta.usuario_id} ")
      codigo = Message(0, "Solicitação realizada com sucesso")
      return marshal(codigo, msgFields), 201
    except IntegrityError:
      logger.error("O atleta ja tem um nutricionista ou ainda nao foi aceito por algum nutricionista")

      codigo = Message(1, "Você já solicitou um nutricionista")
      return marshal(codigo, msgFields), 400

    except:
      logger.error("Erro ao solicita o nutricionista")
      codigo = Message(2, "Erro ao solicita o nutricionista")

  @token_verify
  def delete(self, tipo, refreshToken, user_id):
    if tipo != "Atleta":
      logger.error("Usuario sem autorizacao para acessar a requisição de nutricionista")

      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    atleta = Atleta.query.get(user_id)

    notificacao = NotificacaoNutricionista.query.filter_by(atleta=atleta).first()

    if notificacao is None:
      logger.error(f"Notificacao do usuario de id: {atleta.usuario_id} nao encontrada")

      codigo = Message(1, "Você não possui solicitações de nutricionista")
      return marshal(codigo, msgFields), 404

    db.session.delete(notificacao)
    db.session.commit()

    logger.info("Solicitacao de nutricionista cancelada com sucesso")
    codigo = Message(0, "Solicitação de nutricionista cancelada com sucesso")
    return marshal(codigo, msgFields), 200

class RequestPersonal(Resource):

  @token_verify
  def post(self, tipo, refreshToken, user_id):
    if tipo != "Atleta":
      logger.error("Usuario sem autorizacao para acessar a requisição de personal")

      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    try:
      atleta = Atleta.query.get(user_id)

      msg = f"O atleta {atleta.nome} esta solicitando um personal trainer, você gostaria de aceitar?"

      if atleta.personal_trainer_id is not None:
        logger.error("Atleta ja possui um Personal")
        codigo = Message(1, "Atleta já possui um Personal")
        return marshal(codigo, msgFields), 400

      notificacao = NotificacaoPersonal(atleta.nome, atleta.email, msg, atleta)
      db.session.add(notificacao)
      db.session.commit()

      logger.info(f"Solicitação de personal realizada com sucesso pelo atleta de id: {atleta.usuario_id} ")
      codigo = Message(0, "Solicitação realizada com sucesso")
      return marshal(codigo, msgFields), 201
    except IntegrityError:
      logger.error("O atleta ja tem um personal ou ainda nao foi aceito por algum personal")

      codigo = Message(1, "Você já solicitou um personal trainer")
      return marshal(codigo, msgFields), 400

    except:
      logger.error("Erro ao solicitar o personal")
      codigo = Message(2, "Erro ao solicitar o personal")
      return marshal(codigo, msgFields), 400

  @token_verify
  def delete(self, tipo, refreshToken, user_id):
    if tipo != "Atleta":
      logger.error("Usuario sem autorizacao para acessar a requisição de personal")

      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    atleta = Atleta.query.get(user_id)

    notificacao = NotificacaoPersonal.query.filter_by(atleta=atleta).first()

    if notificacao is None:
      logger.error(f"Notificacao do usuario de id: {atleta.usuario_id} nao encontrada")

      codigo = Message(1, "Você não possui solicitações do personal")
      return marshal(codigo, msgFields), 404

    db.session.delete(notificacao)
    db.session.commit()

    logger.info("Solicitacao do personal cancelada com sucesso")
    codigo = Message(0, "Solicitação do personal cancelada com sucesso")
    return marshal(codigo, msgFields), 200

class AtletaPagination(Resource):
  def get(self, id, max_itens):
    atletas = Atleta.query.all()
    atletasPagination = Atleta.query.paginate(page=id, per_page=max_itens, error_out=False)

    data = {"atletas": atletasPagination.items, "totalAtletas":len(atletas)}

    logger.info("Atletas listados com sucesso")
    return marshal(data, atletasFieldsPagination), 200


