from flask_restful import Resource, marshal, reqparse

from helpers.auth.token_verifier import token_verify
from helpers.logger import logger
from helpers.stripe_config import stripe
from helpers.database import db

from sqlalchemy.exc import IntegrityError

from model.mensagem import msgFields, Message
from model.atleta import Atleta
from model.planos import Plano
from model.assinatura import Assinatura, assinaturaFields

from datetime import datetime

parser = reqparse.RequestParser()

parser.add_argument("idPlano", type=int, help="id do plano não informado", required=False)


class Assinaturas(Resource):
  @token_verify
  def get(self, tipo, refreshToken, user_id):
    if tipo != 'Atleta':
      logger.error("Usuario sem autorizacao para acessar os atletas")

      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    assinatura = Assinatura.query.filter_by(atleta_id=user_id).first()

    if assinatura is None:
      logger.error(f"Usuario de id: {user_id} nao possui uma assinatura")
      codigo = Message(1, f"Usuario de id: {user_id} nao possui uma assinatura")
      return marshal(codigo, msgFields), 404

    return marshal(assinatura, assinaturaFields), 200

  @token_verify
  def post(self, tipo, refreshToken, user_id):
    if tipo != 'Atleta':
      logger.error("Usuario sem autorizacao para acessar os atletas")

      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    try:
      args= parser.parse_args()
      with db.session.begin_nested():

        atleta = Atleta.query.get(user_id)

        if args["idPlano"] is None:
          logger.error("Id do plano nao informado")
          codigo = Message(1, "Id do plano não informado ")
          return marshal(codigo, msgFields), 400

        plano = Plano.query.get(args["idPlano"])
        if plano is None:
          logger.error(f"Plano de id: {args['idPlano']} nao encontrado")
          codigo = Message(1, f"Plano de id: {args['idPlano']} não encontrado")
          return marshal(codigo, msgFields), 404

        periodoTest = 0
        if plano.intervalo == "week":
          periodoTest = 7
        elif plano.intervalo == "month":
          periodoTest = 30
        elif plano.intervalo == "year":
          periodoTest = 60

        assinaturaStripe = stripe.Subscription.create(
          customer=atleta.stripe_id,
          items=[
            {
              "plan": plano.id_PlanoStripe
            }
          ],
          trial_period_days=periodoTest
        )
        assinatura_dict = assinaturaStripe.to_dict()
        assinatura = Assinatura()

        assinatura.id_AssinaturaStripe = assinaturaStripe.id
        assinatura.nome = assinatura_dict['items'].data[0].plan.nickname
        assinatura.intervalo = assinatura_dict['items'].data[0].plan.interval
        assinatura.valor = (float(assinatura_dict['items'].data[0].plan.amount) /100)
        assinatura.data_inicio = datetime.fromtimestamp(assinaturaStripe.current_period_start)
        assinatura.data_fim = datetime.fromtimestamp(assinaturaStripe.current_period_end)
        assinatura.data_inicio_teste = datetime.fromtimestamp(assinaturaStripe.trial_start)
        assinatura.data_fim_teste = datetime.fromtimestamp(assinaturaStripe.trial_end)
        assinatura.status = assinaturaStripe.status
        assinatura.atleta_id = atleta.usuario_id
        assinatura.plano_id = plano.id

        atleta.statusPagamento = assinaturaStripe.status
        db.session.add(assinatura)
        db.session.add(atleta)

      db.session.commit()
      logger.info("Assinatura criada com sucesso")
      return marshal(assinatura, assinaturaFields), 200

    except IntegrityError:
      logger.error("atleta já possui uma assinatura")
      codigo = Message(1, "Você já possui uma assinatura")
      return marshal(codigo, msgFields), 400

    except:
      logger.error(f"Erro ao fazer a asssinatura do atleta de id:{atleta.id}")
      codigo = Message(2, f"Erro ao fazer a asssinatura do atleta de id:{atleta.id}")
      return marshal(codigo, msgFields), 400

  @token_verify
  def delete(self, tipo, refreshToken, user_id):
    if tipo != 'Atleta':
      logger.error("Usuario sem autorizacao para acessar os atletas")

      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    atleta = Atleta.query.get(user_id)

    if atleta.assinatura is None:
      logger.error(f"Atleta de id: {user_id} nao tem uma assinatura")
      codigo = Message(1, f"Atleta de id: {user_id} não tem uma assinatura")
      return marshal(codigo, msgFields), 400

    stripe.Subscription.delete(
      atleta.assinatura.id_AssinaturaStripe
    )

    db.session.delete(atleta.assinatura)
    db.session.commit()
    logger.info("Assinatura cancelada com sucesso")
    return {}, 200

