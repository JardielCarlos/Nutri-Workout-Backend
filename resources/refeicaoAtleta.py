from flask_restful import Resource, marshal, reqparse

from sqlalchemy.exc import IntegrityError, DataError

from helpers.auth.token_verifier import token_verify
from helpers.logger import logger
from helpers.database import db

from model.mensagem import msgFields, Message
from model.cardapio import Cardapio
from model.refeicao import Refeicao, refeicaoFields
from model.nutricionista import Nutricionista

parser = reqparse.RequestParser()

parser.add_argument("nome", type=str, help="Nome não informado", required=True)
parser.add_argument("diaSemana", type=str, help="dia da semana não informada", required=True)
parser.add_argument("tipoRefeicao", type=str, help="tipo da refeição não informada", required=True)

class RefeicaoAtleta(Resource):
  @token_verify
  def get(self, tipo, refreshToken, user_id, id_cardapio):
    if tipo != "Nutricionista":
      logger.error("Usuario sem autorizacao para acessar o cardapio do atleta")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    cardapio = Cardapio.query.get(id_cardapio)
    if cardapio is None:
      logger.error(f"Cardapio de id: {id_cardapio} nao encontrado")

      codigo = Message(1, f"Cardapio de id: {id_cardapio} não encontrado")
      return marshal(codigo, msgFields), 400
    nutricionista = Nutricionista.query.get(user_id)

    idAtletas = [atleta.usuario_id for atleta in nutricionista.atletas]

    if cardapio.atleta not in idAtletas:
      logger.error(f"Cardapio de id: {id_cardapio} nao associado ao nutricionista de id: {nutricionista.usuario_id}")

      codigo = Message(1, f"Cardapio de id: {id_cardapio} não encontrado")
      return marshal(codigo, msgFields), 404

    refeicao = Refeicao.query.filter_by(cardapio=cardapio.id).all()
    return marshal(refeicao, refeicaoFields), 200

  @token_verify
  def post(self, tipo, refreshToken, user_id, id_cardapio):
    args = parser.parse_args()
    if tipo != "Nutricionista":
      logger.error("Usuario sem autorizacao para acessar o cardapio do atleta")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    try:
      cardapio = Cardapio.query.get(id_cardapio)
      if cardapio is None:
        logger.error(f"Cardapio de id: {id_cardapio} nao encontrado")

        codigo = Message(1, f"Cardapio de id: {id_cardapio} não encontrado")
        return marshal(codigo, msgFields), 400

      if len(args["nome"]) == 0 or len(args["nome"]) < 2:
        logger.info("Nome não informado")

        codigo = Message(1, "Nome não informado")
        return marshal(codigo, msgFields), 400

      refeicao = Refeicao(args["nome"], args["diaSemana"], args["tipoRefeicao"])
      refeicao.cardapio = cardapio.id

      db.session.add(refeicao)
      db.session.commit()

      logger.info(f"Refeicao do cardapio de id: {cardapio.id} criada com sucesso")
      return marshal(refeicao, refeicaoFields), 201

    except DataError:
      db.session.rollback()
      logger.error(f"Erro ao digitar o dia da semana ou o tipo da refeicao do cardapio de od: {cardapio.id}")

      codigo = Message(1, "Você digitou o dia da semana ou o tipo de refeicao inválida")
      return marshal(codigo, msgFields), 400

    except IntegrityError:
      db.session.rollback()
      logger.error(f"Erro ja existe uma refeicao identica no cardapio de id: {cardapio.id}")
      codigo = Message(1, "Você já possui uma refeicao para esse mesmo dia ou já possui para o mesmo horario")
      return marshal(codigo, msgFields), 400

    except:
      db.session.rollback()
      logger.error(f"Erro em criar a refeicao do cardapio de id: {cardapio.id}")

      codigo = Message(2, f"Error em criar a refeicao do cardapio de id: {cardapio.id}")
      return marshal(codigo, msgFields), 400

class RefeicaoAtletaId(Resource):
  @token_verify
  def get(self, tipo, refreshToken, user_id, id_cardapio, id):
    if tipo != "Nutricionista":
      logger.error("Usuario sem autorizacao para acessar o cardapio do atleta")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    cardapio = Cardapio.query.get(id_cardapio)
    if cardapio is None:
      logger.error(f"Cardapio de id: {id_cardapio} nao encontrado")

      codigo = Message(1, f"Cardapio de id: {id_cardapio} não encontrado")
      return marshal(codigo, msgFields), 400

    refeicao = Refeicao.query.get(id)
    if refeicao is None:
      logger.error(f"Refeicao de id: {id} nao encontrado")
      codigo = Message(1, f"Refeição de id: {id} não encontrado")
      return marshal(codigo, msgFields), 400

    return marshal(refeicao, refeicaoFields), 200

  @token_verify
  def put(self, tipo, refreshToken, user_id, id_cardapio, id):
    args = parser.parse_args()
    if tipo != "Nutricionista":
      logger.error("Usuario sem autorizacao para acessar o cardapio do atleta")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    try:
      cardapio = Cardapio.query.get(id_cardapio)
      if cardapio is None:
        logger.error(f"Cardapio de id: {id_cardapio} nao encontrado")

        codigo = Message(1, f"Cardapio de id: {id_cardapio} não encontrado")
        return marshal(codigo, msgFields), 400

      refeicao = Refeicao.query.get(id)
      if refeicao is None:
        logger.error(f"Refeicao de id: {id} nao encontrado")
        codigo = Message(1, f"Refeição de id: {id} não encontrado")
        return marshal(codigo, msgFields), 400

      if refeicao not in cardapio.refeicoes:
        logger.error(f"Refeicao de id: {id} nao esta asssociado ao cardapio de id: {cardapio.id}")
        codigo = Message(1, f"Refeição não encontrada no cardapio")
        return marshal(codigo, msgFields), 400

      if len(args["nome"]) == 0 or len(args["nome"]) < 2:
        logger.info("Nome não informado")

        codigo = Message(1, "Nome não informado")
        return marshal(codigo, msgFields), 400

      refeicao.nome = args["nome"]
      refeicao.diaSemana = args["diaSemana"]
      refeicao.tipoRefeicao = args["tipoRefeicao"]

      db.session.add(refeicao)
      db.session.commit()

      logger.info(f"Voce atualizou a refeicao de id: {refeicao.id}")
      return marshal(refeicao, refeicaoFields), 200

    except DataError:
      db.session.rollback()
      logger.error(f"Erro ao digitar o dia da semana ou o tipo da refeicao do cardapio de od: {cardapio.id}")

      codigo = Message(1, "Você digitou o dia da semana ou o tipo de refeicao inválida")
      return marshal(codigo, msgFields), 400

    except IntegrityError:
      db.session.rollback()
      logger.error(f"Erro ja existe uma refeicao identica no cardapio de id: {cardapio.id}")
      codigo = Message(1, "Você já possui uma refeicao para esse mesmo dia ou já possui para o mesmo horario")
      return marshal(codigo, msgFields), 400

    except:
      db.session.rollback()
      logger.error(f"Erro em atualizar a refeicao do cardapio de id: {cardapio.id}")

      codigo = Message(2, f"Error em atualizar a refeicao do cardapio de id: {cardapio.id}")
      return marshal(codigo, msgFields), 400
  @token_verify
  def delete(self, tipo, refreshToken, user_id, id_cardapio, id):
    if tipo != "Nutricionista":
      logger.error("Usuario sem autorizacao para acessar o cardapio do atleta")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    cardapio = Cardapio.query.get(id_cardapio)
    if cardapio is None:
      logger.error(f"Cardapio de id: {id_cardapio} nao encontrado")

      codigo = Message(1, f"Cardapio de id: {id_cardapio} não encontrado")
      return marshal(codigo, msgFields), 400

    refeicao = Refeicao.query.get(id)
    if refeicao is None:
      logger.error(f"Refeicao de id: {id} nao encontrado")
      codigo = Message(1, f"Refeição de id: {id} não encontrado")
      return marshal(codigo, msgFields), 400

    if refeicao not in cardapio.refeicoes:
      logger.error(f"Refeicao de id: {id} nao esta asssociado ao cardapio de id: {cardapio.id}")
      codigo = Message(1, f"Refeição não encontrada no cardapio")
      return marshal(codigo, msgFields), 400

    db.session.delete(refeicao)
    db.session.commit()

    logger.info(f"Refeicao de id: {refeicao.id} deletado com sucesso")
    return {}, 200




