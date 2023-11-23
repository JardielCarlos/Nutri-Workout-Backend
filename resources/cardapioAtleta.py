from flask_restful import Resource, marshal, reqparse

from helpers.auth.token_verifier import token_verify
from helpers.database import db
from helpers.logger import logger

from sqlalchemy.exc import IntegrityError

from model.atleta import Atleta
from model.cardapio import Cardapio, cardapioFields
from model.mensagem import Message, msgFields
from model.nutricionista import Nutricionista


parser = reqparse.RequestParser()

parser.add_argument("nome", type=str, help="nome não informado", required=True)
parser.add_argument("idAtleta", type=int, help="id do atleta não informado", required=False)



class CardapioAtletaNutri(Resource):
  @token_verify
  def get(self, tipo, refreshToken, user_id):
    if tipo != "Nutricionista":
      logger.error("Usuario sem autorizacao para acessar o cardapio do atleta")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    cardapio = Cardapio.query.filter_by(nutricionista=user_id).first()
    return marshal(cardapio, cardapioFields), 200


  @token_verify
  def post(self, tipo, refreshToken, user_id):
    if tipo != "Nutricionista":
      logger.error("Usuario sem autorizacao para acessar o cardapio do atleta")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    try:
      args = parser.parse_args()

      if len(args['nome']) == 0 or len(args['nome']) < 2:
        logger.info("Nome nao informado")

        codigo = Message(1, "Nome nao informado")
        return marshal(codigo, msgFields), 400

      nutricionista = Nutricionista.query.get(user_id)

      if args["idAtleta"] is None:
        logger.error("id do atleta nao informado")

        codigo = Message(1, "id do atleta não informado")
        return marshal(codigo, msgFields), 400

      atleta = Atleta.query.get(args["idAtleta"])

      if atleta is None:
        logger.error(f"Atleta de id: {args['idAtleta']} nao encontrado")

        codigo = Message(1, f"Atleta de id: {args['idAtleta']} não encontrado")
        return marshal(codigo, msgFields), 404

      if atleta not in nutricionista.atletas:
        logger.error(f"Atleta nao asssociado ao nutricionista")

        codigo = Message(1, f"Atleta não associado ao nutricionista")
        return marshal(codigo, msgFields), 200

      cardapio = Cardapio(args['nome'], atleta.usuario_id)
      cardapio.nutricionista = nutricionista.usuario_id

      db.session.add(cardapio)
      db.session.commit()

      logger.info(f"Cardapio do atleta de id: {atleta.usuario_id} criado com sucesso")
      return marshal(cardapio, cardapioFields), 201
    except IntegrityError:
      logger.error(f"Atleta ja tem um cardapio")

      codigo = Message(1, "Atleta já tem um cardapio")
      return marshal(codigo, msgFields), 400

    except:
      logger.error("Erro ao cadastrar o cardapio")

      codigo = Message(2, "Erro ao cadastrar o cardapio")
      return marshal(codigo, msgFields), 400

class CardapioAtletaNutriId(Resource):
  @token_verify
  def get(self, tipo, refreshToken, user_id, id):
    if tipo != "Nutricionista":
      logger.error("Usuario sem autorizacao para acessar o cardapio do atleta")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    atleta = Atleta.query.get(id)
    if atleta is None:
      logger.error(f"Atleta de id: {id} nao encontrado")

      codigo = Message(1, f"Atleta de id: {id} não encontrado")
      return marshal(codigo, msgFields), 404

    nutricionista = Nutricionista.query.get(user_id)

    if atleta not in nutricionista.atletas:
      logger.error(f"Atleta nao associado ao nutricionista")

      codigo = Message(1, f"Atleta não associado ao nutricionista")
      return marshal(codigo, msgFields), 404

    cardapio = Cardapio.query.filter_by(atleta=atleta.usuario_id).first()
    if cardapio is None:
      logger.error(f"Atleta de id: {id} nao possui um cardapio")

      codigo = Message(1, f"Atleta de id: {id} não possui um cardapio")
      return marshal(codigo, msgFields), 404

    return marshal(cardapio, cardapioFields), 200

  @token_verify
  def put(self, tipo, refreshToken, user_id, id):
    args = parser.parse_args()
    if tipo != "Nutricionista":
      logger.error("Usuario sem autorizacao para acessar o cardapio do atleta")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    try:

      atleta = Atleta.query.get(id)
      if atleta is None:
        logger.error(f"Atleta de id: {id} nao encontrado")

        codigo = Message(1, f"Atleta de id: {id} não encontrado")
        return marshal(codigo, msgFields), 404

      nutricionista = Nutricionista.query.get(user_id)

      if atleta not in nutricionista.atletas:
        logger.error(f"Atleta nao associado ao nutricionista")

        codigo = Message(1, f"Atleta não associado ao nutricionista")
        return marshal(codigo, msgFields), 404

      if len(args['nome']) == 0 or len(args['nome']) < 2:
        logger.info("Nome nao informado")

        codigo = Message(1, "Nome nao informado")
        return marshal(codigo, msgFields), 400

      cardapio = Cardapio.query.filter_by(atleta=atleta.usuario_id).first()

      if cardapio is None:
        logger.error(f"Atleta de id: {id} nao possui um cardapio")

        codigo = Message(1, f"Atleta de id: {id} não possui um cardapio")
        return marshal(codigo, msgFields), 404

      cardapio.nome = args["nome"]

      db.session.add(cardapio)
      db.session.commit()

      logger.info(f"Cardapio do atleta de id: {id} atualizado com sucesso")
      return marshal(cardapio, cardapioFields), 200
    except:
      logger.error(f"Erro ao atualizar o cardapio do atleta")

      codigo = Message(2, "Erro ao atualizar o cardapio do atleta")
      return marshal(codigo, msgFields), 400

  @token_verify
  def delete(self, tipo, refreshToken, user_id, id):
    if tipo != "Nutricionista":
      logger.error("Usuario sem autorizacao para acessar o cardapio do atleta")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    atleta = Atleta.query.get(id)
    if atleta is None:
      logger.error(f"Atleta de id: {id} nao encontrado")

      codigo = Message(1, f"Atleta de id: {id} não encontrado")
      return marshal(codigo, msgFields), 404

    nutricionista = Nutricionista.query.get(user_id)

    if atleta not in nutricionista.atletas:
      logger.error(f"Atleta nao associado ao nutricionista")

      codigo = Message(1, f"Atleta não associado ao nutricionista")
      return marshal(codigo, msgFields), 404

    cardapio = Cardapio.query.filter_by(atleta=atleta.usuario_id).first()
    if cardapio is None:
      logger.error(f"Atleta de id: {id} nao possui um cardapio")

      codigo = Message(1, f"Atleta de id: {id} não possui um cardapio")
      return marshal(codigo, msgFields), 404

    logger.info(f"O cardapio de id: {id} deletado com sucesso")
    db.session.delete(cardapio)
    db.session.commit()
    return {}, 200

