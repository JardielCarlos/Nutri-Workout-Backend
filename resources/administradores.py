from flask import make_response
from flask_restful import Resource, marshal, reqparse
from helpers.logger import logger
from helpers.database import db
from werkzeug.security import generate_password_hash
from helpers.auth.token_verifier import token_verify
from sqlalchemy.exc import IntegrityError
from password_strength import PasswordPolicy
from validate_docbr import CPF
from io import BytesIO
from PIL import Image
from werkzeug.datastructures import FileStorage
from model.imgUsuarios import ImgUsuarios
import re
import os

from model.mensagem import Message, msgFields, msgFieldsToken
from model.administrador import Administrador, administradorFieldsToken

parser = reqparse.RequestParser()
parserFiles = reqparse.RequestParser()

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

class Administradores(Resource):
  # @token_verify
  def get(self): #tipo, refreshToken
    # if tipo != 'Administrador':
    #   logger.error("Usuario sem autorizacao para acessar os administradores")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
    #   return marshal(codigo, msgFields), 403
    
    administrador = Administrador.query.all()
    data = {"administrador": administrador, "token": None}

    logger.info("Administradores listado com sucesso")
    return marshal(data, administradorFieldsToken), 200
  
  # @token_verify
  def post(self):
    # if tipo != 'Administrador':
    #   logger.error("Usuario sem autorizacao para acessar os administ")

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
        
        administrador = Administrador(args["nome"], args["sobrenome"], args["email"], args["senha"], args["cpf"])
        
        db.session.add(administrador)
        db.session.flush()

        imgUsuario = ImgUsuarios(fotoPerfil, administrador.usuario_id)

        db.session.add(imgUsuario)

      data = {"administrador": administrador, "token": None}

      logger.info(f"Administrador de id: {administrador.id} criado com sucesso")
      return marshal(data, administradorFieldsToken), 201
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
  # @token_verify
  def get(self, id): #tipo, refreshToken, id
    # if tipo != 'Administrador':
    #   logger.error("Usuario sem autorizacao para acessar os administ")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
    #   return marshal(codigo, msgFields), 403
    
    administrador = Administrador.query.get(id)

    if administrador is None:
      logger.info(f"Administrador de id: {id} nao encontrado")

      codigo = Message(1, f"Administrador de id: {id} nao encontrado")
      return marshal(codigo, msgFields), 400
    
    data = {"administrador": administrador, "token": None}

    logger.info(f"Administrador de id: {id} listado com sucesso")
    return marshal(data, administradorFieldsToken), 200

  # @token_verify
  def put(self, id):
    # if tipo != 'Administrador':
    #   logger.error("Usuario sem autorizacao para acessar os administ")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
    #   return marshal(codigo, msgFields), 403

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
      
      administradorBD.nome = args["nome"]
      administradorBD.sobrenome = args["sobrenome"]
      administradorBD.email = args["email"]
      administradorBD.cpf = args["cpf"],

      db.session.add(administradorBD)
      db.session.commit()

      data = {"administrador": administradorBD, "token": None}
      logger.info(f"Administrador de id: {id} atualizado com sucesso")

      return marshal(data, administradorFieldsToken), 200
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
  # @token_verify
  def patch(self, id):
    # if tipo != 'Administrador':
    #   logger.error("Usuario sem autorizacao para acessar os administ")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
    #   return marshal(codigo, msgFields), 403

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

      data = {"msg": codigo, "token": None}
      return marshal(data, msgFieldsToken), 200
    except:
      logger.error("Erro ao atualizar a senha do Administrador")
      codigo = Message(2, "Erro ao atualizar a senha do Administrador")
      return marshal(codigo, msgFieldsToken), 400
  
  # @token_verify
  def delete(self, id):
    # if tipo != 'Administrador':
    #   logger.error("Usuario sem autorizacao para acessar os administ")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
    #   return marshal(codigo, msgFields), 403

    administrador = Administrador.query.get(id)
    if administrador is None:
      logger.error(f"Administrador de id: {id} nao encotrado")

      codigo = Message(1, f"Administrador de id: {id} não encontrado")
      return marshal(codigo, msgFields), 404
    
    db.session.delete(administrador)
    db.session.commit()
    
    logger.info(f"Administrador de id: {id} deletado com sucesso")
    return {'token': None}, 200

class AdministradorImg(Resource):
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

      logger.info("Foto do administrador atualizada com sucesso")

      db.session.add(userDB)
      db.session.commit()

      return {}, 204
    except:
      logger.error("Erro ao atualizar a imagem do administrador")

      codigo = Message(2, "Erro ao atualizar a imagem do administrador")
      return marshal(codigo, msgFields), 400

  def delete(self, id):
    userDB = ImgUsuarios.query.filter_by(usuario_id=id).first()

    if userDB is None:
      logger.error(f'Imagem do administrador de id: {id} nao encontrada')
      codigo = Message(1, f"Imagem do administrador de id: {id} nao encontrada")
      return marshal(codigo, msgFields), 404
    
    userDB.fotoPerfil= None

    db.session.add(userDB)
    db.session.commit()

    return {}, 200
class AdministradorNome(Resource):
  # @token_verify
  def get(self, nome):
    # if tipo != 'Administrador':
    #   logger.error("Usuario sem autorizacao para acessar os administ")

    #   codigo = Message(1, "Usuario sem autorização suficiente!")
    #   return marshal(codigo, msgFields), 403
    administradorNome = Administrador.query.filter(Administrador.nome.ilike(f"%{nome}%")).all()

    data = {"administrador": administradorNome, "token": None}
    logger.info(f"Administrador com nomes: {nome} listado com sucesso")
    return marshal(data, administradorFieldsToken), 200