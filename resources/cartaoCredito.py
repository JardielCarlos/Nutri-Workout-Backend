from flask_restful import Resource, reqparse, marshal

from helpers.database import db
from helpers.stripe_config import stripe
from helpers.auth.token_verifier import token_verify
from helpers.logger import logger

from model.atleta import Atleta
from model.mensagem import Message, msgFields
from model.cartaoCredito import CartaoCredito, cartaoCreditoFields

from stripe.error import InvalidRequestError

parser = reqparse.RequestParser()

parser.add_argument("token", type=str, help="token não informado", required=False)
parser.add_argument("nomeTitular", type=str, help="nome do titular não informado", required=False)
parser.add_argument("mesCartao", type=str, help="mês do cartão não informado", required=False)
parser.add_argument("anoCartao", type=str, help="ano do cartão não informado", required=False)

class CartaoCreditoAtleta(Resource):
  @token_verify
  def get(self, tipo, refreshToken, user_id):
    if tipo != 'Atleta':
      logger.error("Usuario sem autorizacao para acessar os atletas")

      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    atleta = Atleta.query.get(user_id)
    return marshal(atleta.cartoes, cartaoCreditoFields), 200

  @token_verify
  def post(self, tipo, refreshToken, user_id):
    if tipo != 'Atleta':
      logger.error("Usuario sem autorizacao para acessar os atletas")

      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    try:
      with db.session.begin_nested():

        args = parser.parse_args()

        if args["token"] is None:
          logger.error("token nao informado")

          codigo = Message(1, "Token não informado")
          return marshal(codigo, msgFields), 400

        if len(args['token']) == 0:
          logger.error("token nao valido")

          codigo = Message(1, "Token não valido")
          return marshal(codigo, msgFields), 400

        atleta = Atleta.query.get(user_id)
        cartaoCredito = CartaoCredito(atleta.usuario_id)
        cartao = stripe.Customer.create_source(
          atleta.stripe_id,
          source=args["token"]
        )
        print(cartao)
        cartaoCredito.id_cartaoCredito = cartao.id
        cartaoCredito.nomeTitular = cartao.name
        cartaoCredito.bandeira = cartao.brand
        cartaoCredito.mesVencimento = cartao.exp_month
        cartaoCredito.anoVencimento = cartao.exp_year
        cartaoCredito.finalCartao = cartao.last4

        if len(atleta.cartoes) == 0:
          stripe.Customer.modify(
            atleta.stripe_id,
            invoice_settings={
              "default_payment_method": cartaoCredito.id_cartaoCredito
            }
          )
          cliente = stripe.Customer.retrieve(atleta.stripe_id)
          cartaoCredito.pagamentoPadrao = cliente.invoice_settings.default_payment_method
          atleta.cartoes.append(cartaoCredito)

          db.session.add(atleta)
          db.session.add(cartaoCredito)
          db.session.flush()

        atleta.cartoes.append(cartaoCredito)

        db.session.add(atleta)
        db.session.add(cartaoCredito)
        db.session.flush()

      db.session.commit()

      logger.info(f"Cartao de credito do atleta de id: {atleta.id}")
      return marshal(cartaoCredito, cartaoCreditoFields), 201

    except InvalidRequestError as e:
      if "You cannot use a Stripe token more than once" in str(e):
        logger.error("Token de cartao de credito ja utilizado")
        codigo = Message(1, "Token do cartão de credito já utilizado")
        return marshal(codigo, msgFields), 400

    except:
      logger.error(f"Error ao cadastrar o cartao de credito")
      codigo = Message(2, "Error ao cadastrar o cartao de credito")
      return marshal(codigo, msgFields), 400

class CartaoCreditoAtletaId(Resource):

  @token_verify
  def get(self, tipo, refreshToken, user_id, id):
    if tipo != 'Atleta':
      logger.error("Usuario sem autorizacao para acessar os atletas")

      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    atleta = Atleta.query.get(user_id)

    cartao = CartaoCredito.query.get(id)

    if cartao is None:
      logger.error(f"Cartao de credito de id: {id} nao encontrado")

      codigo = Message(1,f"Cartão de credito de id: {id} não encontrado")
      return marshal(codigo, msgFields), 404

    if cartao not in atleta.cartoes:
      logger.error(f"Cartao nao associado ao atleta de id: {atleta.usuario_id}")

      codigo = Message(f"Cartao de id: {cartao.id} não encontrado")
      return marshal(codigo, msgFields), 404

    return marshal(cartao, cartaoCreditoFields), 200

  @token_verify
  def put(self, tipo, refreshToken, user_id, id):
    if tipo != 'Atleta':
      logger.error("Usuario sem autorizacao para acessar os atletas")

      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    try:
      args = parser.parse_args()
      atleta = Atleta.query.get(user_id)

      cartao = CartaoCredito.query.get(id)

      if cartao is None:
        logger.error(f"Cartao de credito de id: {id} nao encontrado")

        codigo = Message(1,f"Cartão de credito de id: {id} não encontrado")
        return marshal(codigo, msgFields), 404

      if cartao not in atleta.cartoes:
        logger.error(f"Cartao nao associado ao atleta de id: {atleta.usuario_id}")

        codigo = Message(f"Cartao de id: {cartao.id} não encontrado")
        return marshal(codigo, msgFields), 404

      if args["nomeTitular"] is None:
        logger.error("Nome do titular nao informado")
        codigo = Message(1, "Nome do titular não informado")
        return marshal(codigo, msgFields), 400

      if len(args["nomeTitular"]) < 5:
        logger.error("Nome nao valido")
        codigo = Message(1, "Nome não válido")
        return marshal(codigo, msgFields), 400

      if args["mesCartao"] is None:
        logger.error("mes do cartão nao informado")
        codigo = Message(1, "mês do cartão não informado")
        return marshal(codigo, msgFields), 400

      if len(args["mesCartao"]) < 2:
        logger.error("mes do cartao nao valido")
        codigo = Message(1, "mês do cartão não válido")
        return marshal(codigo, msgFields), 400

      if args["anoCartao"] is None:
        logger.error("ano do cartão nao informado")
        codigo = Message(1, "ano do cartão não informado")
        return marshal(codigo, msgFields), 400

      if len(args["anoCartao"]) < 2:
        logger.error("ano do cartao nao valido")
        codigo = Message(1, "ano do cartão não válido")
        return marshal(codigo, msgFields), 400

      cartao.nomeTitular = args["nomeTitular"]
      cartao.mesVencimento = args["mesCartao"]
      cartao.anoVencimento = args["anoCartao"]

      stripe.Customer.modify_source(
        atleta.stripe_id,
        cartao.id_cartaoCredito,
        name=args["nomeTitular"],
        exp_month=args["mesCartao"],
        exp_year=args["anoCartao"]
      )

      db.session.add(cartao)
      db.session.commit()

      logger.info("Cartao atualizado com sucesso")
      return marshal(cartao, cartaoCreditoFields), 200
    except:
      logger.error("Error ao atualizar cartao de credito")
      codigo = Message(1, "Error ao atualizar cartao de credito")
      return marshal(codigo, msgFields), 400

  @token_verify
  def delete(self, tipo, refreshToken, user_id, id):
    if tipo != 'Atleta':
      logger.error("Usuario sem autorizacao para acessar os atletas")

      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    atleta = Atleta.query.get(user_id)
    cartaoCredito = CartaoCredito.query.get(id)
    if cartaoCredito is None:
      logger.error(f"Cartao de credito de id: {id} nao encontrado")

      codigo = Message(1,f"Cartão de credito de id: {id} não encontrado")
      return marshal(codigo, msgFields), 404

    stripe.Customer.delete_source(
      atleta.stripe_id,
      cartaoCredito.id_cartaoCredito
    )
    db.session.delete(cartaoCredito)
    db.session.commit()

    logger.info("Cartao de credito deletado com sucesso")
    return {}, 200
