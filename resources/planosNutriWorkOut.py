from flask_restful import Resource, reqparse, marshal

from sqlalchemy.exc import DataError

from helpers.stripe_config import stripe
from helpers.logger import logger
from helpers.database import db

from model.mensagem import Message, msgFields
from model.planos import Plano, planosFields
from model.produtos import Produto
parser = reqparse.RequestParser()

parser.add_argument("id_produto", type=str, help="nome não informado", required=False)
parser.add_argument("nome", type=str, help="nome não informado", required=False)
parser.add_argument("intervalo", type=str, help="nome não informado", required=False)
parser.add_argument("valor", type=float, help="nome não informado", required=False)


class PlanosNutriWorkOut(Resource):
  def get(self):
    planos = Plano.query.all()
    return marshal(planos, planosFields), 200

  def post(self):
    try:
      with db.session.begin_nested():

        args = parser.parse_args()

        if args["id_produto"] is None:
          logger.error(f"id do produto nao informado")

          codigo = Message(1,"id do produto não informado")
          return marshal(codigo, msgFields), 400

        if args["nome"] is None:
          logger.error(f"Nome nao informado")

          codigo = Message(1,"Nome não informado")
          return marshal(codigo, msgFields), 400

        if args["intervalo"] is None:
          logger.error(f"intervalo nao informado")

          codigo = Message(1,"intervalo não informado")
          return marshal(codigo, msgFields), 400

        if args["valor"] is None:
          logger.error(f"valor nao informado")

          codigo = Message(1,"valor não informado")
          return marshal(codigo, msgFields), 400

        if len(args["nome"]) == 0:
          logger.info("Nome não informado")

          codigo = Message(1, "Nome não informado")
          return marshal(codigo, msgFields), 400

        if args["valor"] <= 0:
          logger.info("valor não valido")

          codigo = Message(1, "valor não valido")
          return marshal(codigo, msgFields), 400

        produto = Produto.query.get(args["id_produto"])
        if produto is None:
          logger.error(f"Produto de id: {args['id_produto']} nao encontrado")

          codigo = Message(1, f"produto de id: {args['id_produto']} não encontrado")
          return marshal(codigo, msgFields), 404

        valor = args["valor"] * 100
        
        plano = Plano(args["nome"], args["intervalo"], args["valor"])
        db.session.add(plano)
        db.session.flush()

        planoStripe = stripe.Plan.create(
          product=produto.id_ProductStripe,
          nickname=args["nome"],
          interval=args["intervalo"],
          currency="brl",
          amount=int(valor)
        )

        plano.id_PlanoStripe = planoStripe.id
        plano.ativo = planoStripe.active
        produto.planos.append(plano)

        db.session.add(produto)

      db.session.commit()
      logger.info("Plano criado com sucesso")
      return marshal(plano, planosFields), 201

    except DataError:
      logger.error("Intervalo digitado invalido")

      codigo = Message(1, "Você digitou um intervalo inválido digte: day, week, month ou year")
      return marshal(codigo, msgFields), 400

    except:
      logger.error("Erro ao criar o plano")

      codigo = Message(2, "Erro ao criar o plano")
      return marshal(codigo, msgFields), 400

class PlanosNutriWorkOutId(Resource):
  def get(self, id):
    plano = Plano.query.get(id)

    if plano is None:
      logger.error(f"Plano de id: {id} nao encontrado")

      codigo = Message(1, f"Plano de id: {id} não encontrado")
      return marshal(codigo, msgFields), 400

    logger.info(f"Plano de id: {id} listado com sucesso")
    return marshal(plano, planosFields), 200

  def put(self, id):
    try:
      args = parser.parse_args()

      plano = Plano.query.get(id)

      if plano is None:
        logger.error(f"Plano de id: {id} nao encontrado")

        codigo = Message(1, f"Plano de id: {id} não encontrado")
        return marshal(codigo, msgFields), 400

      if args["nome"] is None:
          logger.error(f"Nome nao informado")

          codigo = Message(1,"Nome não informado")
          return marshal(codigo, msgFields), 400

      if len(args["nome"]) == 0:
        logger.info("Nome não informado")

        codigo = Message(1, "Nome não informado")
        return marshal(codigo, msgFields), 400

      plano.nome = args["nome"]

      stripe.Plan.modify(
        plano.id_PlanoStripe,
        nickname=args["nome"],
      )

      db.session.add(plano)
      db.session.commit()

      logger.info(f"Plano de id: {plano.id} atualizado com sucesso")
      return marshal(plano, planosFields), 200
    except:
      logger.error(f"Error ao atualizar o plano de id: {id}")

      codigo = Message(1, f"Error ao atualizar o plano de id: {id}")
      return marshal(codigo, msgFields), 400

  def delete(self, id):
    plano = Plano.query.get(id)

    if plano is None:
      logger.error(f"Plano de id: {id} nao encontrado")

      codigo = Message(1, f"Plano de id: {id} não encontrado")
      return marshal(codigo, msgFields), 400

    stripe.Plan.delete(
      plano.id_PlanoStripe
    )

    db.session.delete(plano)
    db.session.commit()

    return {}, 200
