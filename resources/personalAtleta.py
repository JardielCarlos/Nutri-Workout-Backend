from datetime import datetime

from flask_restful import Resource, marshal, reqparse
from sqlalchemy.exc import IntegrityError

from helpers.auth.token_verifier import token_verify
from helpers.database import db
from helpers.logger import logger
from model.atleta import Atleta, atletaAssociatedFields
from model.mensagem import Message, msgFields
from model.notificacaoPersonal import NotificacaoPersonal
from model.personalTrainer import (PersonalTrainer,
                                   personalAtletaPaginationFields)
from model.tabelaTreino import TabelaTreino, tabelaTreinoFields

parser = reqparse.RequestParser()

def parse_date(date_string):
  return datetime.strptime(date_string, '%d/%m/%Y')

parser.add_argument("semanaInicio", type=parse_date, help="semana de inicio não informada", required=True)
parser.add_argument("semanaFim", type=parse_date, help="semana fim não informada", required=True)
parser.add_argument("musculoTrabalhado", type=str, help="musculo trabalhado não informado", required=True)
parser.add_argument("nomeExercicio", type=str, help="Nome do exercicio informado", required=True)
parser.add_argument("series", type=int, help="Séries não informada", required=True)
parser.add_argument("kg", type=int, help="kg não informado", required=True)
parser.add_argument("repeticao", type=int, help="repetições não informada", required=True)
parser.add_argument("descanso", type=int, help="descanso não informado", required=True)
parser.add_argument("unidadeDescanso", type=str, help="unidade do descanso não informado", required=True)
parser.add_argument("observacoes", type=str, help="observações não informadas", required=False)
parser.add_argument("atleta", type=int, help="atleta não informado", required=False)

class PersonalAtleta(Resource):
  @token_verify
  def get(self, tipo, refreshToken, user_id):
    print(tipo)
    if tipo != "Personal":
      logger.error("Usuario sem autorizacao para acessar os atletas associados ao personal trainer")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    personal = PersonalTrainer.query.get(user_id)
    return marshal(personal.atletas, atletaAssociatedFields), 200

class PersonalAtletaPagination(Resource):
  @token_verify
  def get(self, tipo, refreshToken, user_id, id, max_itens):
    if tipo != "Personal":
      logger.error("Usuario sem autorizacao para acessar os atletas associados ao personal trainer")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    personal = PersonalTrainer.query.get(user_id)
    atletasPagination = Atleta.query.filter_by(personal_trainer_id=user_id).paginate(page=id, per_page=max_itens, error_out=False)

    data = {"atletasPersonal": atletasPagination.items, "totalAtletas": len(personal.atletas)}

    return marshal(data, personalAtletaPaginationFields), 200



class PersonalAtletaId(Resource):
  @token_verify
  def get(self, tipo, refreshToken, user_id, id):
    if tipo != "Personal":
      logger.error("Usuario sem autorizacao para acessar os atletas associados ao personal trainer")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    atleta = Atleta.query.get(id)
    if atleta is None:
      logger.error(f"Atleta de id: {id} nao encontrado")

      codigo = Message(1, f"Atleta de id: {id} não encontrado")
      return marshal(codigo, msgFields), 200

    personal = PersonalTrainer.query.get(user_id)

    if atleta not in personal.atletas:
      logger.error(f"Atleta de id:{id} associado a outro personal")

      codigo = Message(1, f"Atleta de id: {id} não associado ao personal")
      return marshal(codigo, msgFields), 400

    return marshal(atleta, atletaAssociatedFields), 200

  @token_verify
  def delete(self, tipo, refreshToken, user_id, id):
    if tipo != "Personal":
      logger.error("Usuario sem autorizacao para acessar os atletas associados ao personal trainer")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    atleta = Atleta.query.get(id)
    if atleta is None:
      logger.error(f"Atleta de id: {id} nao encontrado")

      codigo = Message(1, f"Atleta de id: {id} não encontrado")
      return marshal(codigo, msgFields), 200

    personal = PersonalTrainer.query.get(user_id)

    if atleta not in personal.atletas:
      logger.error(f"Atleta de id:{id} associado a outro personal")

      codigo = Message(1, f"Atleta de id: {id} não associado ao personal")
      return marshal(codigo, msgFields), 400


    atleta.personal_trainer_id = None
    notificacaoAtleta = NotificacaoPersonal.query.filter_by(atleta_id=atleta.usuario_id).first()
    notificacaoAtleta.solicitacao= False

    db.session.add(notificacaoAtleta)
    db.session.add(atleta)
    db.session.commit()

    logger.info(f"Atleta de id: {id} deletado com sucesso")
    return {}, 200

class TabelaTreinoAtleta(Resource):
  @token_verify
  def post(self, tipo, refreshToken, user_id):
    args = parser.parse_args()
    if tipo != "Personal":
      logger.error("Usuario sem autorizacao para acessar os atletas associados ao nutricionista")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    try:
      personal = PersonalTrainer.query.get(user_id)

      if args["atleta"] is None:
        logger.error("atleta nao informado")

        codigo = Message(1, "Atleta nao informado")
        return marshal(codigo, msgFields), 400

      atleta = Atleta.query.get(args["atleta"])

      if len(args["musculoTrabalhado"]) <= 2:
        logger.error(f"Escreva o nome de um musculo valido")

        codigo = Message(1, f"Escreva o nome de um musculo válido")
        return marshal(codigo, msgFields), 400

      if len(args['nomeExercicio']) <= 2:
        logger.error(f"Escreva o nome de um exercicio valido")

        codigo = Message(1, f"Escreva o nome de um exercicio válido")
        return marshal(codigo, msgFields), 400

      if atleta is None:
        logger.error(f"Atleta de id: {args['atleta']} nao encotrado")

        codigo = Message(1, f"Atleta de id: {args['atleta']} não encontrado")
        return marshal(codigo, msgFields), 404

      if atleta not in personal.atletas:
        logger.error(f"Atleta de id: {atleta.usuario_id} nao esta associado ao personal trainer de id: {user_id}")

        codigo = Message(1, f"Atleta de id: {atleta.usuario_id} não está associado ao personal trainer de id: {user_id}")
        return marshal(codigo, msgFields), 403

      tabelaTreino = TabelaTreino(args["semanaInicio"], args["semanaFim"], args["musculoTrabalhado"], args["nomeExercicio"], args["series"], args["repeticao"], args["kg"], args["descanso"], args["unidadeDescanso"], args["observacoes"], atleta.usuario_id, personal.usuario_id)

      db.session.add(tabelaTreino)
      db.session.commit()

      logger.info(f"tabela de treino do atleta de id: {atleta.usuario_id} criado com sucesso")
      return marshal(tabelaTreino, tabelaTreinoFields), 201
    except IntegrityError:
      logger.error(f"O atleta ja tem uma tabela de treino associada")
      codigo = Message(1, "O atleta já tem uma tabela de treino associada")
      return marshal(codigo, msgFields), 400
    except:
      logger.error(f"Erro ao cadastra a tabela de treino do atleta: {atleta.usuario_id}")
      codigo = Message(2, f"Erro ao cadastra a tabela de treino do atleta: {atleta.usuario_id}")
      return marshal(codigo, msgFields), 400

class TabelaTreinoAtletaId(Resource):
  @token_verify
  def get(self, tipo, refreshToken, user_id, id):
    if tipo != "Personal":
      logger.error("Usuario sem autorizacao para acessar os atletas associados ao nutricionista")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    tabelaTreino = TabelaTreino.query.filter_by(atleta=id, personal=user_id).first()
    if tabelaTreino is None:
      return [], 200
    return marshal(tabelaTreino, tabelaTreinoFields), 200
  @token_verify
  def put(self,tipo, refreshToken, user_id, id):
    args = parser.parse_args()
    if tipo != "Personal":
      logger.error("Usuario sem autorizacao para acessar os atletas associados ao nutricionista")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    try:
      if len(args["musculoTrabalhado"]) <= 2:
        logger.error(f"Escreva o nome de um musculo valido")

        codigo = Message(1, f"Escreva o nome de um musculo válido")
        return marshal(codigo, msgFields), 400

      if len(args['nomeExercicio']) <= 2:
        logger.error(f"Escreva o nome de um exercicio valido")

        codigo = Message(1, f"Escreva o nome de um exercicio válido")
        return marshal(codigo, msgFields), 400

      atleta = Atleta.query.get(id)

      if atleta is None:
        logger.error(f"Atleta de id: {id} nao encontrado")

        codigo = Message(1, f"Atleta de id: {id} nao encontrado")
        return marshal(codigo, msgFields), 400

      tabelaTreino = TabelaTreino.query.filter_by(atleta=atleta.usuario_id).first()
      personal = PersonalTrainer.query.get(user_id)

      if atleta not in personal.atletas:
        logger.error(f"Atleta de id: {atleta.usuario_id} nao esta associado ao personal trainer de id: {user_id}")

        codigo = Message(1, f"Atleta de id: {atleta.usuario_id} não está associado ao personal trainer de id: {user_id}")
        return marshal(codigo, msgFields), 403

      tabelaTreino.semanaInicio = args["semanaInicio"]
      tabelaTreino.semanaFim = args["semanaFim"]
      tabelaTreino.musculoTrabalhado = args["musculoTrabalhado"],
      tabelaTreino.nomeExercicio = args["nomeExercicio"]
      tabelaTreino.series = args["series"]
      tabelaTreino.repeticao = args["repeticao"]
      tabelaTreino.kg = args["kg"]
      tabelaTreino.descanso = args["descanso"]
      tabelaTreino.unidadeDescanso = args["unidadeDescanso"]
      tabelaTreino.observacoes = args ["observacoes"]

      db.session.add(tabelaTreino)
      db.session.commit()

      logger.info(f"Tabela de treino do atleta de id: {atleta.usuario_id} atualizado com sucesso")
      return marshal(tabelaTreino, tabelaTreinoFields), 200
    except:
      logger.error("Erro ao atualizar a tabela de treino")

      codigo = Message(2, "Erro ao atualizar a tabela de treino")
      return marshal(codigo, msgFields), 400
