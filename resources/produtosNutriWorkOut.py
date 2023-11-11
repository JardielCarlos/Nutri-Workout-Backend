from flask_restful import Resource, reqparse, marshal

from helpers.stripe_config import stripe
from helpers.database import db
from helpers.logger import logger

from model.produtos import Produto, produtoFields
from model.mensagem import Message, msgFields

parser = reqparse.RequestParser()

parser.add_argument("nome", type=str, help="nome não informado", required=True)
parser.add_argument("descricao", type=str, help="descrição não informada", required=True)

class ProdutosNutriWorkOut(Resource):
  def get(self):
    produtos = stripe.Product.list()
    if not produtos.data:
      return [], 200

    return marshal(produtos, produtoFields), 200

  def post(self):
    try:
      args = parser.parse_args()

      produtoStripe = stripe.Product.create(
        name=args["nome"],
        description=args["descricao"]
      )

      produto = Produto(produtoStripe.id, produtoStripe.name, produtoStripe.description, produtoStripe.active)

      db.session.add(produto)
      db.session.commit()

      logger.info("Produto criado com sucesso")
      return marshal(produto, produtoFields), 201
    except:
      logger.error("Error ao criar o produto")
      codigo = Message(2, "Error ao criar o produto")
      return marshal(codigo, msgFields)

class ProdutosNutriWorkOutId(Resource):
  def get(self, id):
    produto = Produto.query.get(id)

    if produto is None:
      logger.error(f"Produto de id: {id} nao encontrado")

      codigo = Message(f"Produto de id: {id} não encontrado")
      return marshal(codigo, msgFields), 404

    return marshal(produto, produtoFields), 200

  def put(self, id):
    try:
      args = parser.parse_args()
      produto = Produto.query.get(id)

      if produto is None:
        logger.error(f"Produto de id: {id} nao encontrado")

        codigo = Message(f"Produto de id: {id} não encontrado")
        return marshal(codigo, msgFields), 404

      produto.nome = args["nome"]
      produto.descricao = args["descricao"]

      stripe.Product.modify(
        produto.id_ProductStripe,
        name=args["nome"],
        description= args["descricao"]
      )

      logger.info(f"Produto de id: {produto.id} atualizado com sucesso")
      return marshal(produto, produtoFields), 200
    except:
      logger.error(f"Error ao atualizar o produto de id: {produto.id}")
      codigo = Message(2, f"Error ao atualizar o produto de id: {produto.id}")

  def delete(self, id):
    produto = Produto.query.get(id)

    if produto is None:
      logger.error(f"Produto de id: {id} nao encontrado")

      codigo = Message(f"Produto de id: {id} não encontrado")
      return marshal(codigo, msgFields), 404

    stripe.Product.delete(produto.id_ProductStripe)
    db.session.delete(produto)
    db.session.commit()

    logger.info("Produto deletado com sucesso")
    return {}, 200

