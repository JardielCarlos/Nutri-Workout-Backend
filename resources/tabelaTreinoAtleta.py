from flask_restful import Resource, marshal, reqparse

from sqlalchemy.exc import IntegrityError

from helpers.auth.token_verifier import token_verify
from helpers.logger import logger
from helpers.database import db

from datetime import datetime

from model.mensagem import Message, msgFields
from model.personalTrainer import PersonalTrainer
from model.atleta import Atleta
from model.tabelaTreino import TabelaTreino, tabelaTreinoFields

parser = reqparse.RequestParser()

def parse_date(date_string):
  return datetime.strptime(date_string, '%d/%m/%Y')

parser.add_argument("semanaInicio", type=parse_date, help="semana de inicio não informada", required=True)
parser.add_argument("semanaFim", type=parse_date, help="semana fim não informada", required=True)
parser.add_argument("atleta", type=int, help="atleta não informado", required=False)

class TabelaTreinoAtleta(Resource):

  @token_verify
  def get(self, tipo, refreshToken, user_id):
    if tipo != "Personal Trainer":
      logger.error("Usuario sem autorizacao para acessar a tabela de treino")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    
    tabelaTreino = TabelaTreino.query.filter_by(personal=user_id).all()
    return marshal(tabelaTreino, tabelaTreinoFields),200
  @token_verify
  def post(self, tipo, refreshToken, user_id):
    args = parser.parse_args()
    if tipo != "Personal Trainer":
      logger.error("Usuario sem autorizacao para acessar a tabela de treino")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    try:
      personal = PersonalTrainer.query.get(user_id)

      if args["atleta"] is None:
        logger.error("atleta nao informado")
        
        codigo = Message(1, "Atleta não informado")
        return marshal(codigo, msgFields), 400
      
      atleta = Atleta.query.get(args["atleta"])
      if atleta is None:
        logger.error(f"Atleta de id: {args['atleta']} nao encotrado")

        codigo = Message(1, f"Atleta de id: {args['atleta']} não encontrado")
        return marshal(codigo, msgFields), 404
      
      if atleta not in personal.atletas:
        logger.error(f"Atleta de id: {atleta.usuario_id} nao esta associado ao personal trainer de id: {user_id}")
        
        codigo = Message(1, f"Atleta de id: {atleta.usuario_id} não está associado ao personal trainer de id: {user_id}")
        return marshal(codigo, msgFields), 403
      
      tabelaTreino = TabelaTreino(args["semanaInicio"], args["semanaFim"], args["atleta"], personal.usuario_id)

      db.session.add(tabelaTreino)
      db.session.commit()

      logger.info(f"tabela de treino do atleta de id: {atleta.usuario_id} criado com sucesso")
      return marshal(tabelaTreino, tabelaTreinoFields), 201
    
    except IntegrityError:
      logger.error(f"O atleta ja tem uma tabela de treino associada")
      codigo = Message(1, "O atleta já tem uma tabela de treino associada")
      return marshal(codigo, msgFields), 400
    except:
      logger.error(f"Erro ao cadastra a tabela de treino do atleta: {atleta.id}")
      codigo = Message(2, f"Erro ao cadastra a tabela de treino do atleta: {atleta.id}")
      return marshal(codigo, msgFields), 400
    
class TabelaTreinoAtletaId(Resource):
  @token_verify
  def put(self, tipo, refreshToken, user_id, id):
    args = parser.parse_args()
    if tipo != "Personal Trainer":
      logger.error("Usuario sem autorizacao para acessar a tabela de treino")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    try:
      tabelaTreino = TabelaTreino.query.get(id)

      if tabelaTreino is None:
        logger.error(f"tabela de treino de id: {id} nao encontrada")

        codigo = Message(1, f"Tabela de treino de id: {id} não encontrada")
        return marshal(codigo, msgFields), 400
      
      tabelaTreino.semanaInicio = args["semanaInicio"]
      tabelaTreino.semanaFim = args["semanaFim"]

      logger.info(f"Tabela de treino de id: {id} atualizada com sucesso")
      return marshal(tabelaTreino, tabelaTreinoFields), 200
    except:
      logger.error("Erro ao atualizar a tabela de treino")

      codigo = Message(2, "Erro ao atualizar a tabela de treino")
      return marshal(codigo, msgFields), 400
  
  @token_verify
  def delete(self, tipo, refreshToken, user_id, id):
    if tipo != "Personal Trainer":
      logger.error("Usuario sem autorizacao para acessar a tabela de treino")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    
    tabelaTreino = TabelaTreino.query.get(id)
    db.session.delete(tabelaTreino)
    db.session.commit()

    logger.info(f"Tabela de treino de id: {id} deletado com sucesso")
    return {}, 200
