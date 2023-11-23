from flask_restful import Resource, reqparse, marshal

from helpers.stripe_config import stripe
from helpers.database import db
from helpers.logger import logger

from model.mensagem import Message, msgFields
from model.assinatura import Assinatura
from model.atleta import Atleta

parser = reqparse.RequestParser()

parser.add_argument("type", type=str, help="tipo não informado", required=True)
parser.add_argument("data", type=dict, help="tipo não informado", required=True)

class StripeWeebHook(Resource):
  def post(self):
    # try:
      args = parser.parse_args()
      tipoEvento = args['type']
      data = args['data']

      if tipoEvento == 'customer.subscription.updated' or tipoEvento == 'customer.subscription.trial_will_end':
          assinaturaHook = data['object']
          statusHook = assinaturaHook['status']
          customer_id = assinaturaHook['customer']


          if statusHook == 'canceled': #Cancela a assinatura do atleta
            atleta = Atleta.query.filter_by(stripe_id=customer_id).first()
            assinatura = Assinatura.query.filter_by(atleta_id=atleta.usuario_id).first()

            stripe.Subscription.delete(
              assinatura.id_AssinaturaStripe
            )

            atleta.statusPagamento = statusHook

            db.session.add(atleta)
            db.session.delete(assinatura)

            db.session.commit()
          elif statusHook == 'active' or statusHook == 'trialing':#Ativa a assinatura do atleta
            atleta = Atleta.query.filter_by(stripe_id=customer_id).first()
            assinatura = Assinatura.query.filter_by(atleta_id=atleta.usuario_id).first()

            assinatura.status = statusHook
            atleta.statusPagamento = statusHook

            db.session.add(assinatura)
            db.session.add(atleta)

            db.session.commit()

          elif statusHook == 'past_due':# O pagamento falhou e ele não tem acesso ao sistema
            atleta = Atleta.query.filter_by(stripe_id=customer_id).first()
            assinaturaBD = Assinatura.query.filter_by(atleta_id=atleta.usuario_id).first()

            assinaturaBD.status = statusHook
            atleta.statusPagamento = statusHook

            db.session.add(assinaturaBD)
            db.session.add(atleta)

            db.session.commit()

          # Adicione mais condições conforme necessário
      logger.info("requisicao realizado com sucesso")
      codigo = Message(1, "requisição realizada com sucesso")
      return marshal(codigo, msgFields), 200
    # except:
    #   logger.error("Erro ao fazer a requisicao")
    #   codigo = Message(2, "Erro ao fazer a requisição")
    #   return marshal(codigo, msgFields), 400
