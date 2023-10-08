from flask import make_response
from flask_restful import marshal, Resource, reqparse
from helpers.logger import logger
from helpers.database import db
from helpers.auth.token_verifier import token_verify
from password_strength import PasswordPolicy
from validate_docbr import CPF
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from model.consumerRabbitmq import RabbitmqConsumer
from model.imgUsuarios import ImgUsuarios
from werkzeug.datastructures import FileStorage
from helpers.auth.token_verifier import token_verify
from io import BytesIO
from PIL import Image
from json import loads
import re

from model.mensagem import Message, msgFields, msgFieldsToken
from model.personalTrainer import PersonalTrainer, personalTrainerFieldsToken, personalTrainerPagination, personalTrainerAssociatedFieldsToken
from model.notificacaoPersonal import NotificacaoPersonal, notificacaoPersonalFields
from model.atleta import Atleta

parser = reqparse.RequestParser()
parserFiles = reqparse.RequestParser()

parser.add_argument("nome", type=str, help="Nome não informado", required=False)
parser.add_argument("sobrenome", type=str, help="Sobrenome não informado", required=False)
parser.add_argument("email", type=str, help="email não informado", required=False)
parser.add_argument("senha", type=str, help="senha não informado", required=False)
parser.add_argument("cpf", type=str, help="cpf não informado", required=False)
parser.add_argument("cref", type=str, help="cref não informado", required=False)
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
"290.297.910-04" #
"607.298.816-44"#
"167.167.991-17" #
"677.986.197-98"#

"123456-G/SP"
"654321-G/RJ"
"789012-G/ES"
"210987-G/BA"
"345678-P/RS"
"876543-P/SC"

class PersonaisTrainer(Resource):
  # @token_verify
  def get(self):
    # if tipo != 'Administrador':
    #   logger.error("Usuario sem autorizacao para acessar os Personais Trainer")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
    #   return marshal(codigo, msgFields), 403
    
    logger.info("Personais Trainer listados com sucesso")

    # personalTrainer = PersonalTrainer.query.get(2)
    # atletas = personalTrainer.atletas
    # print(atletas)
    personalTrainer = PersonalTrainer.query.all()
    data = {"personal": personalTrainer, "token": None}

    return marshal(data, personalTrainerFieldsToken), 200
  
  # @token_verify
  def post(self):
    # if tipo != 'Administrador' and tipo != 'Personal Trainer':
    #   logger.error("Usuario sem autorizacao para acessar os Personais Trainer")

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
        
        if not args['cref']:
          codigo = Message(1, "CREF não informada")
          return marshal(codigo, msgFields), 400
        
        if not re.match(r'\d{6}-G\/[A-Z]{2}', args['cref']):
          codigo = Message(1, "CREF no formato errado")
          return marshal(codigo, msgFields), 400

        personalTrainer = PersonalTrainer(args["nome"], args["sobrenome"], args["email"], args["senha"], args["cpf"], args["cref"])

        db.session.add(personalTrainer)
        db.session.flush()

        imgUsuario = ImgUsuarios(fotoPerfil, personalTrainer.usuario_id)

        db.session.add(imgUsuario)

      data = {"personal": personalTrainer, "token": None}

      logger.info(f"Personal Trainer de id: {personalTrainer.id} criado com sucesso")
      return marshal(data, personalTrainerFieldsToken), 201
    
    except IntegrityError as e:
      if "cpf" in str(e.orig):
        codigo = Message(1, "CPF já cadastrado no sistema")
        return marshal(codigo, msgFields), 400
      
      elif "email" in str(e.orig):
        codigo = Message(1, "Email já cadastrado no sistema")
        return marshal(codigo, msgFields), 400
      
      elif "cref" in str(e.orig):
        codigo = Message(1, "CREF já cadastrado no sistema")
        return marshal(codigo, msgFields), 400
    except:
      logger.error("Erro ao cadastrar o Personal Trainer")

      codigo = Message(2, "Erro ao cadastrar o Personal Trainer")
      return marshal(codigo, msgFields), 400
    
class PersonalTrainerId(Resource):
  # @token_verify
  def get(self, id):
    # if tipo != 'Administrador' and tipo != 'Personal Trainer':
    #   logger.error("Usuario sem autorizacao para acessar os Personais Trainer")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
    #   return marshal(codigo, msgFields), 403
    
    personalTrainer = PersonalTrainer.query.get(id)

    if personalTrainer is None:
      logger.error(f"Personal Trainer de id: {id} nao encotrado")

      codigo = Message(1, f"Personal Trainer de id: {id} não encontrado")
      return marshal(codigo, msgFields), 404
    
    data = {"personal": personalTrainer, "token": None}
    logger.info(f"Personal Trainer de id: {id} listado com sucesso")
    return marshal(data, personalTrainerAssociatedFieldsToken), 200
  # @token_verify
  def put(self, id):
    # if tipo != 'Administrador' and tipo != 'Personal Trainer':
    #   logger.error("Usuario sem autorizacao para acessar os Personais Trainer")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
    #   return marshal(codigo, msgFields), 403
    
    args = parser.parse_args()
    try:
      personalTrainerBD = PersonalTrainer.query.get(id)

      if personalTrainerBD is None:
        logger.error(f"Personal Trainer de id: {id} nao encotrado")

        codigo = Message(1, f"Personal Trainer de id: {id} não encontrado")
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

      if not args['cref']:
        codigo = Message(1, "cref não informado")
        return marshal(codigo, msgFields), 400
      
      if not re.match(r'\d{6}-G\/[A-Z]{2}', args['cref']):
        codigo = Message(1, "CREF no formato errado")
        return marshal(codigo, msgFields), 400

      personalTrainerBD.nome = args["nome"]
      personalTrainerBD.sobrenome = args["sobrenome"]
      personalTrainerBD.email = args["email"]
      personalTrainerBD.cpf = args["cpf"]
      personalTrainerBD.cref = args["cref"]

      db.session.add(personalTrainerBD)
      db.session.commit()

      data = {"personal": personalTrainerBD, "token": None}

      logger.info(f"Personal Trainer de id: {id} atualizado com sucesso")
      return marshal(data, personalTrainerFieldsToken), 200
    
    except IntegrityError as e:
      if "cpf" in str(e.orig):
        codigo = Message(1, "CPF já cadastrado no sistema")
        return marshal(codigo, msgFields), 400
      
      elif "email" in str(e.orig):
        codigo = Message(1, "Email já cadastrado no sistema")
        return marshal(codigo, msgFields), 400
      
      elif "cref" in str(e.orig):
        codigo = Message(1, "CREF já cadastrado no sistema")
        return marshal(codigo, msgFields), 400
      
    except:
      logger.error("Erro ao cadastrar o Personal Trainer")

      codigo = Message(2, "Erro ao cadastrar o Personal Trainer")
      return marshal(codigo, msgFields), 400
    
  # @token_verify
  def patch(self, id):
    # if tipo != 'Administrador' and tipo != 'Personal Trainer':
    #   logger.error("Usuario sem autorizacao para acessar os Personais Trainer")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
      # return marshal(codigo, msgFields), 403
    
    args = parser.parse_args()
    try:
      personalTrainerBD = PersonalTrainer.query.get(id)

      if personalTrainerBD is None:
        logger.error(f"Personal Trainer de id: {id} nao encontrado")

        codigo = Message(1, f"Personal trainer de id: {id} nao encontrado")
        return marshal(codigo, msgFields), 404
      
      if not personalTrainerBD.verify_password(args['senha']):
        codigo = Message(1, "Senha incorreta ou inexistente")
        return marshal(codigo, msgFields), 404
      
      if not args['novaSenha']:
        codigo = Message(1, "nova senha não informada")
        return marshal(codigo, msgFields), 400
      
      verifySenha = policy.test(args['novaSenha'])
      if len(verifySenha) != 0:
        codigo = Message(1, "Senha no formato errado")
        return marshal(codigo, msgFields), 400
      
      personalTrainerBD.senha = generate_password_hash(args['novaSenha'])

      db.session.add(personalTrainerBD)
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
    # if tipo != 'Administrador' and tipo != 'Personal Trainer':
    #   logger.error("Usuario sem autorizacao para acessar os Personais Trainer")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
    #   return marshal(codigo, msgFields), 403
    
    personalTrainer = PersonalTrainer.query.get(id)

    if personalTrainer is None:
      logger.error(f"Personal Trainer de id: {id} nao encotrado")

      codigo = Message(1, f"Personal Trainer de id: {id} não encontrado")
      return marshal(codigo, msgFields), 404
    
    db.session.delete(personalTrainer)
    db.session.commit()

    logger.info(f"Personal Trainer de id: {id} deletado com sucesso")
    return {"token": None}, 200
  
class PersonalImg(Resource):
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
      
      newFoto = args['fotoPerfil']
      if newFoto is None:
        logger.error("campo fotoPerfil nao informado")
        codigo = Message(1, "campo fotoPerfil nao informado")
        return marshal(codigo, msgFields), 404
      
      if newFoto:
        newFoto.stream.seek(0)
        fotoPerfil = newFoto.stream.read()

      userDB.fotoPerfil = fotoPerfil

      logger.info("Foto do personal trainer atualizada com sucesso")

      db.session.add(userDB)
      db.session.commit()

      return {}, 204
    except:
      logger.error("Erro ao atualizar a imagem do personal trainer")

      codigo = Message(2, "Erro ao atualizar a imagem do personal trainer")
      return marshal(codigo, msgFields), 400
  
  def delete(self, id):
    userDB = ImgUsuarios.query.filter_by(usuario_id=id).first()

    if userDB is None:
      logger.error(f'Imagem do personal trainer de id: {id} nao encontrada')
      codigo = Message(1, f"Imagem do personal trainer de id: {id} nao encontrada")
      return marshal(codigo, msgFields), 404
    
    userDB.fotoPerfil= None

    db.session.add(userDB)
    db.session.commit()

    return {}, 200

  
class PersonalTrainerNome(Resource):
  # @token_verify
  def get(self, nome):
    # if tipo != 'Administrador':
    #   logger.error("Usuario sem autorizacao para acessar os Personais Trainer")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
    #   return marshal(codigo, msgFields), 403
    
    personalTrainer = PersonalTrainer.query.filter(PersonalTrainer.nome.ilike(f"%{nome}%")).all()

    data = {"personal": personalTrainer, "token": None}
    logger.info(f"Personais Trainer com nomes: {nome} listados com sucesso")
    return marshal(data, personalTrainerFieldsToken), 200
  
class PersonalNotificacoes(Resource):
  def get(self):
    notificacoes = NotificacaoPersonal.query.filter_by(solicitacao=False).all()

    logger.info(f"Notificacoes dos personais listadas com sucesso")
    return marshal(notificacoes, notificacaoPersonalFields)
  
class PersonalNotificacoesId(Resource):
  def get(self, id):
    notificacao = NotificacaoPersonal.query.filter_by(solicitacao=False, id=id).first()

    if notificacao is None:
      logger.error(f"Notificacao de id: {id} nao encontrada")

      codigo = Message(1, f"Notificacao de id: {id} nao encontrada")
      return marshal(codigo, msgFields), 404

    logger.info(f"Notificacao de id: {id} listado com sucesso")
    return marshal(notificacao, notificacaoPersonalFields)
  @token_verify
  def patch(self, tipo, refreshToken, user_id, id):
    notificacao = NotificacaoPersonal.query.filter_by(solicitacao=False, id=id).first()
    if notificacao is None:
      logger.error(f"Notificacao de id: {id} nao encontrada")

      codigo = Message(1, f"Notificacao de id: {id} nao encontrada")
      return marshal(codigo, msgFields), 404
    
    personal = PersonalTrainer.query.get(user_id)
    atleta = Atleta.query.get(notificacao.atleta_id)

    personal.atletas.append(atleta)
    atleta.personal_trainer_id = personal.usuario_id
    notificacao.solicitacao = True

    db.session.add(notificacao)
    db.session.add(personal)
    db.session.add(atleta)
    db.session.commit()

    logger.info(f"O personal aceitou o atleta: {notificacao.nome} como seu aluno")
    codigo = Message(0, f"Voce aceitou o atleta: {notificacao.nome} como seu aluno")
    return marshal(codigo, msgFields), 200
  
  def delete(self, id):
    notificacao = NotificacaoPersonal.query.get(id)

    if notificacao is None:
      logger.error(f"Notificacao de id: {id} nao encontrada")

      codigo = Message(1, f"Notificacao de id: {id} nao encontrada")
      return marshal(codigo, msgFields), 404
    
    db.session.delete(notificacao)
    db.session.commit()

    logger.info(f"Notificacao de id: {id} deletado com sucesso")
    return {}, 200
  
class PersonalTrainerPagination(Resource):
  def get(self, id):
    personais = PersonalTrainer.query.all()
    personaisPagination = PersonalTrainer.query.paginate(page=id, per_page=10, error_out=False)

    data = {"personais": personaisPagination.items, "totalPersonais": len(personais)}
    logger.info("Personais listados com sucesso")
    return marshal(data, personalTrainerPagination), 200
