from flask_restful import Resource, marshal, reqparse

from helpers.auth.token_verifier import token_verify
from helpers.logger import logger
from helpers.database import db

from model.cardapio import Cardapio
from model.ingrediente import Ingrediente, ingredienteFields, ingredienteFieldsPagination
from model.mensagem import Message, msgFields
from model.nutricionista import Nutricionista
from model.refeicao import Refeicao

parser = reqparse.RequestParser()

parser.add_argument("nome", type=str, help="Nome não informado", required=True)
parser.add_argument("quantidade", type=str, help="quantidade não informada", required=True)


class IngredienteAtleta(Resource):
  @token_verify
  def get(self, tipo, refreshToken, user_id, id_cardapio, id_refeicao):
    if tipo != "Nutricionista":
      logger.error("Usuario sem autorizacao para acessar o cardapio do atleta")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    cardapio = Cardapio.query.get(id_cardapio)
    if cardapio is None:
      logger.error(f"Cardapio de id: {id_cardapio} nao encontrado")

      codigo = Message(1, f"Cardapio de id: {id_cardapio} não encontrado")
      return marshal(codigo, msgFields), 404

    nutricionista = Nutricionista.query.get(user_id)

    idAtletas = [atleta.usuario_id for atleta in nutricionista.atletas]

    if cardapio.atleta not in idAtletas:
      logger.error(f"Cardapio de id: {id_cardapio} nao associado ao nutricionista de id: {nutricionista.usuario_id}")

      codigo = Message(1, f"Cardapio de id: {id_cardapio} não encontrado")
      return marshal(codigo, msgFields), 404

    refeicao = Refeicao.query.get(id_refeicao)

    if refeicao is None:
      logger.error(f"Refeicao de id: {id_refeicao} nao encontrado")

      codigo = Message(1, f"Refeição de id: {id_refeicao} não encontrada")
      return marshal(codigo, msgFields), 404

    if refeicao not in cardapio.refeicoes:
      logger.error(f"Refeicao de id: {id_refeicao} nao associado ao cardapio de id: {cardapio.id}")

      codigo = Message(1, f"Refeição de id: {id_refeicao} não encontrada")
      return marshal(codigo, msgFields), 404

    ingrediente = Ingrediente.query.filter_by(refeicao=refeicao.id).all()
    return marshal(ingrediente, ingredienteFields), 200

  @token_verify
  def post(self, tipo, refreshToken, user_id, id_cardapio, id_refeicao):
    if tipo != "Nutricionista":
      logger.error("Usuario sem autorizacao para acessar o cardapio do atleta")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    try:
      args = parser.parse_args()
      cardapio = Cardapio.query.get(id_cardapio)
      if cardapio is None:
        logger.error(f"Cardapio de id: {id_cardapio} nao encontrado")

        codigo = Message(1, f"Cardapio de id: {id_cardapio} não encontrado")
        return marshal(codigo, msgFields), 404

      nutricionista = Nutricionista.query.get(user_id)

      idAtletas = [atleta.usuario_id for atleta in nutricionista.atletas]

      if cardapio.atleta not in idAtletas:
        logger.error(f"Cardapio de id: {id_cardapio} nao associado ao nutricionista de id: {nutricionista.usuario_id}")

        codigo = Message(1, f"Cardapio de id: {id_cardapio} não encontrado")
        return marshal(codigo, msgFields), 404

      refeicao = Refeicao.query.get(id_refeicao)

      if refeicao is None:
        logger.error(f"Refeicao de id: {id_refeicao} nao encontrado")

        codigo = Message(1, f"Refeição de id: {id_refeicao} não encontrada")
        return marshal(codigo, msgFields), 404

      if refeicao not in cardapio.refeicoes:
        logger.error(f"Refeicao de id: {refeicao.id} nao esta associado ao cardapio de id: {cardapio.id}")

        codigo = Message(1, f"Refeição de id: {refeicao.id} não encontrada")
        return marshal(codigo, msgFields), 404

      if len(args["nome"]) == 0 or len(args["nome"]) < 2:
        logger.info("Nome não informado")

        codigo = Message(1, "Nome não informado")
        return marshal(codigo, msgFields), 400

      if len(args["quantidade"]) == 0:
        logger.info("quantidade não informado")

        codigo = Message(1, "quantidade não informado")
        return marshal(codigo, msgFields), 400

      ingrediente = Ingrediente(args["nome"], args["quantidade"])
      ingrediente.refeicao = refeicao.id

      db.session.add(ingrediente)
      db.session.commit()

      logger.info(f"Ingrediente da refeicao de id: {refeicao.id} criada com sucesso")
      return marshal(ingrediente, ingredienteFields), 200
    except:
      logger.error(f"Erro ao cadastrar o ingrediente na refeicao de id: {refeicao.id}")
      codigo = Message(1, f"Erro ao cadastrar o ingrediente da refeição de id: {refeicao.id}")
      return marshal(codigo, msgFields), 400

class IngredienteAtletaId(Resource):

  @token_verify
  def get(self, tipo, refreshToken, user_id, id_cardapio, id_refeicao, id):
    if tipo != "Nutricionista":
      logger.error("Usuario sem autorizacao para acessar o cardapio do atleta")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    cardapio = Cardapio.query.get(id_cardapio)
    if cardapio is None:
      logger.error(f"Cardapio de id: {id_cardapio} nao encontrado")

      codigo = Message(1, f"Cardapio de id: {id_cardapio} não encontrado")
      return marshal(codigo, msgFields), 404

    nutricionista = Nutricionista.query.get(user_id)

    idAtletas = [atleta.usuario_id for atleta in nutricionista.atletas]

    if cardapio.atleta not in idAtletas:
      logger.error(f"Cardapio de id: {id_cardapio} nao associado ao nutricionista de id: {nutricionista.usuario_id}")

      codigo = Message(1, f"Cardapio de id: {id_cardapio} não encontrado")
      return marshal(codigo, msgFields), 404

    refeicao = Refeicao.query.get(id_refeicao)

    if refeicao is None:
      logger.error(f"Refeicao de id: {id_refeicao} nao encontrado")

      codigo = Message(1, f"Refeição de id: {id_refeicao} não encontrada")
      return marshal(codigo, msgFields), 404

    if refeicao not in cardapio.refeicoes:
      logger.error(f"Refeicao de id: {id_refeicao} nao associado ao cardapio de id: {cardapio.id}")

      codigo = Message(1, f"Refeição de id: {id_refeicao} não encontrada")
      return marshal(codigo, msgFields), 404

    ingrediente = Ingrediente.query.get(id)

    if ingrediente is None:
      logger.error(f"Ingrediente de id: {id} nao encontrado")

      codigo = Message(1, f"Ingrediente de id: {id} não encontrado")
      return marshal(codigo, msgFields), 404

    if ingrediente not in refeicao.ingredientes:
      logger.error(f"Ingrediente de id: {ingrediente.id} nao esta associado as refeicao de id: {refeicao.id}")

      codigo = Message(1, f"Ingrediente de id: {ingrediente.id} não encontrado")
      return marshal(codigo, msgFields), 404

    logger.info(f"Ingrediente de id: {ingrediente.id} listado com sucesso")
    return marshal(ingrediente, ingredienteFields), 200

  @token_verify
  def put(self, tipo, refreshToken, user_id, id_cardapio, id_refeicao, id):
    if tipo != "Nutricionista":
      logger.error("Usuario sem autorizacao para acessar o cardapio do atleta")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    try:
      args = parser.parse_args()
      cardapio = Cardapio.query.get(id_cardapio)
      if cardapio is None:
        logger.error(f"Cardapio de id: {id_cardapio} nao encontrado")

        codigo = Message(1, f"Cardapio de id: {id_cardapio} não encontrado")
        return marshal(codigo, msgFields), 404

      nutricionista = Nutricionista.query.get(user_id)

      idAtletas = [atleta.usuario_id for atleta in nutricionista.atletas]

      if cardapio.atleta not in idAtletas:
        logger.error(f"Cardapio de id: {id_cardapio} nao associado ao nutricionista de id: {nutricionista.usuario_id}")

        codigo = Message(1, f"Cardapio de id: {id_cardapio} não encontrado")
        return marshal(codigo, msgFields), 404

      refeicao = Refeicao.query.get(id_refeicao)

      if refeicao is None:
        logger.error(f"Refeicao de id: {id_refeicao} nao encontrado")

        codigo = Message(1, f"Refeição de id: {id_refeicao} não encontrada")
        return marshal(codigo, msgFields), 404

      if refeicao not in cardapio.refeicoes:
        logger.error(f"Refeicao de id: {id_refeicao} nao associado ao cardapio de id: {cardapio.id}")

        codigo = Message(1, f"Refeição de id: {id_refeicao} não encontrada")
        return marshal(codigo, msgFields), 404

      ingrediente = Ingrediente.query.get(id)

      if ingrediente is None:
        logger.error(f"Ingrediente de id: {id} nao encontrado")

        codigo = Message(1, f"Ingrediente de id: {id} não encontrado")
        return marshal(codigo, msgFields), 404

      if ingrediente not in refeicao.ingredientes:
        logger.error(f"Ingrediente de id: {ingrediente.id} nao esta associado as refeicao de id: {refeicao.id}")

        codigo = Message(1, f"Ingrediente de id: {ingrediente.id} não encontrado")
        return marshal(codigo, msgFields), 404

      if len(args["nome"]) == 0 or len(args["nome"]) < 2:
        logger.info("Nome não informado")

        codigo = Message(1, "Nome não informado")
        return marshal(codigo, msgFields), 400

      if len(args["quantidade"]) == 0:
        logger.info("quantidade não informado")

        codigo = Message(1, "quantidade não informado")
        return marshal(codigo, msgFields), 400

      ingrediente.nome = args["nome"]
      ingrediente.quantidade = args["quantidade"]

      db.session.add(ingrediente)
      db.session.commit()

      logger.info(f"Ingrediente atualizado com sucesso")
      return marshal(ingrediente, ingredienteFields), 200
    except:
      logger.error(f"Erro em atualizar o ingrediente de id: {ingrediente.id}")

      codigo = Message(2, f"Erro em atualizar o ingrediente de id: {ingrediente.id}")
      return marshal(codigo, msgFields), 400


  @token_verify
  def delete(self, tipo, refreshToken, user_id, id_cardapio, id_refeicao, id):
    if tipo != "Nutricionista":
      logger.error("Usuario sem autorizacao para acessar o cardapio do atleta")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    cardapio = Cardapio.query.get(id_cardapio)

    if cardapio is None:
      logger.error(f"Cardapio de id: {id_cardapio} nao encontrado")

      codigo = Message(1, f"Cardapio de id: {id_cardapio} não encontrado")
      return marshal(codigo, msgFields), 404

    nutricionista = Nutricionista.query.get(user_id)

    idAtletas = [atleta.usuario_id for atleta in nutricionista.atletas]

    if cardapio.atleta not in idAtletas:
      logger.error(f"Cardapio de id: {id_cardapio} nao associado ao nutricionista de id: {nutricionista.usuario_id}")

      codigo = Message(1, f"Cardapio de id: {id_cardapio} não encontrado")
      return marshal(codigo, msgFields), 404

    refeicao = Refeicao.query.get(id_refeicao)

    if refeicao is None:
      logger.error(f"Refeicao de id: {id_refeicao} nao encontrado")

      codigo = Message(1, f"Refeição de id: {id_refeicao} não encontrada")
      return marshal(codigo, msgFields), 404

    if refeicao not in cardapio.refeicoes:
      logger.error(f"Refeicao de id: {id_refeicao} nao associado ao cardapio de id: {cardapio.id}")

      codigo = Message(1, f"Refeição de id: {id_refeicao} não encontrada")
      return marshal(codigo, msgFields), 404

    ingrediente = Ingrediente.query.get(id)

    if ingrediente is None:
      logger.error(f"Ingrediente de id: {id} nao encontrado")

      codigo = Message(1, f"Ingrediente de id: {id} não encontrado")
      return marshal(codigo, msgFields), 404

    if ingrediente not in refeicao.ingredientes:
      logger.error(f"Ingrediente de id: {ingrediente.id} nao esta associado as refeicao de id: {refeicao.id}")

      codigo = Message(1, f"Ingrediente de id: {ingrediente.id} não encontrado")
      return marshal(codigo, msgFields), 404

    logger.info(f"Ingrediente deletado com sucesso")
    db.session.delete(ingrediente)
    db.session.commit()

    return {}, 200

class IngredienteAtletaPagination(Resource):
  @token_verify
  def get(self, tipo, refreshToken, user_id, id_cardapio, id_refeicao, id_page, max_itens):
    if tipo != "Nutricionista":
      logger.error("Usuario sem autorizacao para acessar os atletas associados ao nutricionista")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    cardapio = Cardapio.query.get(id_cardapio)
    if cardapio is None:
      logger.error(f"Cardapio de id: {id_cardapio} nao encontrado")

      codigo = Message(1, f"Cardapio de id: {id_cardapio} não encontrado")
      return marshal(codigo, msgFields), 404

    nutricionista = Nutricionista.query.get(user_id)

    idAtletas = [atleta.usuario_id for atleta in nutricionista.atletas]

    if cardapio.atleta not in idAtletas:
      logger.error(f"Cardapio de id: {id_cardapio} nao associado ao nutricionista de id: {nutricionista.usuario_id}")

      codigo = Message(1, f"Cardapio de id: {id_cardapio} não encontrado")
      return marshal(codigo, msgFields), 404

    refeicao = Refeicao.query.get(id_refeicao)

    if refeicao is None:
      logger.error(f"Refeicao de id: {id_refeicao} nao encontrado")

      codigo = Message(1, f"Refeição de id: {id_refeicao} não encontrada")
      return marshal(codigo, msgFields), 404

    if refeicao not in cardapio.refeicoes:
      logger.error(f"Refeicao de id: {id_refeicao} nao associado ao cardapio de id: {cardapio.id}")

      codigo = Message(1, f"Refeição de id: {id_refeicao} não encontrada")
      return marshal(codigo, msgFields), 404

    ingrediente = Ingrediente.query.filter_by(refeicao=refeicao.id).count()
    ingredientePagination = Ingrediente.query.filter_by(refeicao=refeicao.id).paginate(page=id_page, per_page=max_itens, error_out=False)

    data = {"ingredientes": ingredientePagination.items, "total": ingrediente}

    logger.info("Ingredientes listado com sucesso")
    return marshal(data, ingredienteFieldsPagination), 200

class test(Resource):
  def get(self):
    pass
