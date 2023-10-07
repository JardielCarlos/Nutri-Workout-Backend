from flask import make_response

from flask_restful import Resource, marshal, reqparse, request
from sqlalchemy.exc import IntegrityError
from helpers.logger import logger
from helpers.database import db

from helpers.auth.token_verifier import token_verify
from werkzeug.security import generate_password_hash

from password_strength import PasswordPolicy
from validate_docbr import CPF
import re

from model.publisherRabbitmq import RabbitmqPublisher


from model.notificacaoPersonal import NotificacaoPersonal
from model.atleta import Atleta, atletaFieldsToken, atletasFieldsPagination
from model.mensagem import Message, msgFields, msgFieldsToken

from io import BytesIO
from PIL import Image
from werkzeug.datastructures import FileStorage
from model.imgUsuarios import ImgUsuarios

parser = reqparse.RequestParser()
parserFiles = reqparse.RequestParser()
# rabbitmqPublisher = RabbitmqPublisher()

# parser.add_argument('fotoPerfil', type=FileStorage, location='files')

parser.add_argument("nome", type=str, help="Nome não informado", required=False)
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
        # foto = args['fotoPerfil']
        fotoPerfil = None

        # if foto:
        #   foto.stream.seek(0)
        #   fotoPerfil = foto.stream.read()

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
        db.session.flush()

        imgUsuario = ImgUsuarios(fotoPerfil, atleta.usuario_id)

        db.session.add(imgUsuario)

      data = {"atleta": atleta, "token": None}

      logger.info(f"Atleta de id: {atleta.id} criado com sucesso")
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
    
    db.session.delete(atleta)
    db.session.commit()

    logger.info(f"Atleta de id: {id} deletado com sucesso")
    return {"token": None}, 200
  
class AtletaImg(Resource):
  parser = reqparse.RequestParser()
  parser.add_argument('fotoPerfil', type=FileStorage, location='files')

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
      
      fotoPerfil = None
      if newFoto:
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
  
class RequestPersonal(Resource):
  def post(self, id):
    atleta = Atleta.query.get(id)

    if atleta is None:
      logger.error(f"Atleta de id: {id} nao encontrado")

      codigo = Message(1, f"Atleta de id: {id} não encontrado")
      return marshal(codigo, msgFields), 404
    
    msg = f"O atleta {atleta.nome} esta solicitando um personal trainer, você gostaria de aceitar?"

    notificacao = NotificacaoPersonal(atleta.nome, atleta.email, msg, atleta)
    # rabbitmqPublisher.send_message({
    #   "id": atleta.id,
    #   "nome": atleta.nome,
    #   "email": atleta.email,
    #   "mensagem": f"O atleta {atleta.nome} esta solicitando um personal trainer, você gostaria de aceitar?"
    # })
    db.session.add(notificacao)
    db.session.commit()

    logger.info(f"Solicitação de personal realizada com sucesso pelo usuario de id: {id} ")
    codigo = Message(0, "Solicitação realizada com sucesso")
    return marshal(codigo, msgFields), 201
  
class AtletaPagination(Resource):
  def get(self, id):
    atletas = Atleta.query.all()
    atletasPagination = Atleta.query.paginate(page=id, per_page=10, error_out=False)
    
    data = {"atletas": atletasPagination.items, "totalAtletas":len(atletas)}
    
    logger.info("Atletas listados com sucesso")
    return marshal(data, atletasFieldsPagination), 200


