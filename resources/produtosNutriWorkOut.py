from flask_restful import Resource, reqparse, marshal

from helpers.stripe_config import stripe
from helpers.database import db
from helpers.logger import logger

from model.produtos import Produto, produtoFields, produtoPlanosFields
from model.mensagem import Message, msgFields

parser = reqparse.RequestParser()

parser.add_argument("nome", type=str, help="nome não informado", required=False)
parser.add_argument("descricao", type=str, help="descrição não informada", required=False)

class ProdutosNutriWorkOut(Resource):
  def get(self):
    produtos = Produto.query.all()
    return marshal(produtos, produtoFields), 200

  def post(self):
    try:
      with db.session.begin_nested():
        args = parser.parse_args()

        if args["nome"] is None:
          logger.info("Nome não informado")

          codigo = Message(1, "Nome não informado")
          return marshal(codigo, msgFields), 400

        if args["descricao"] is None:
          logger.info("descricao não informado")

          codigo = Message(1, "Descrição não informado")
          return marshal(codigo, msgFields), 400

        if len(args["nome"]) == 0:
          logger.info("Nome não informado")

          codigo = Message(1, "Nome não informado")
          return marshal(codigo, msgFields), 400
        if len(args["descricao"]) == 0:
          logger.info("descricao não informada")

          codigo = Message(1, "descrição não informada")
          return marshal(codigo, msgFields), 400

        produto = Produto(args["nome"], args["descricao"])

        db.session.add(produto)
        db.session.flush()

        produtoStripe = stripe.Product.create(
          name=args["nome"],
          description=args["descricao"]
        )

        produto.id_ProductStripe = produtoStripe.id
        produto.ativo = produtoStripe.active

      db.session.commit()

      logger.info("Produto criado com sucesso")
      return marshal(produto, produtoFields), 201
    except:
      db.session.rollback()
      logger.error("Error ao criar o produto")
      codigo = Message(2, "Error ao criar o produto")
      return marshal(codigo, msgFields), 400

class ProdutosNutriWorkOutId(Resource):
  def get(self, id):
    produto = Produto.query.get(id)

    if produto is None:
      logger.error(f"Produto de id: {id} nao encontrado")

      codigo = Message(1, f"Produto de id: {id} não encontrado")
      return marshal(codigo, msgFields), 404

    return marshal(produto, produtoPlanosFields), 200

  def put(self, id):
    try:
      args = parser.parse_args()
      produto = Produto.query.get(id)
      print(produto)
      if produto is None:
        logger.error(f"Produto de id: {id} nao encontrado")

        codigo = Message(1, f"Produto de id: {id} não encontrado")
        return marshal(codigo, msgFields), 404
      if args["nome"] is None:
        logger.info("Nome não informado")

        codigo = Message(1, "Nome não informado")
        return marshal(codigo, msgFields), 400

      if args["descricao"] is None:
        logger.info("descricao não informado")

        codigo = Message(1, "Descrição não informado")
        return marshal(codigo, msgFields), 400
      if len(args["nome"]) == 0:
        logger.info("Nome não informado")

        codigo = Message(1, "Nome não informado")
        return marshal(codigo, msgFields), 400
      if len(args["descricao"]) == 0:
        logger.info("descricao não informada")

        codigo = Message(1, "descrição não informada")
        return marshal(codigo, msgFields), 400


      produto.nome = args["nome"]
      produto.descricao = args["descricao"]

      stripe.Product.modify(
        produto.id_ProductStripe,
        name=args["nome"],
        description= args["descricao"]
      )

      db.session.add(produto)
      db.session.commit()

      logger.info(f"Produto de id: {produto.id} atualizado com sucesso")
      return marshal(produto, produtoFields), 200
    except:
      logger.error(f"Error ao atualizar o produto de id: {id}")
      codigo = Message(2, f"Error ao atualizar o produto de id: {id}")
      return marshal(codigo, msgFields), 400

  def delete(self, id):
    produto = Produto.query.get(id)

    if produto is None:
      logger.error(f"Produto de id: {id} nao encontrado")

      codigo = Message(1, f"Produto de id: {id} não encontrado")
      return marshal(codigo, msgFields), 404

    stripe.Product.delete(produto.id_ProductStripe)
    db.session.delete(produto)
    db.session.commit()

    logger.info("Produto deletado com sucesso")
    return {}, 200

