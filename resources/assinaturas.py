# from flask_restful import Resource, marshal

# from helpers.auth.token_verifier import token_verify
# from helpers.logger import logger
# from helpers.stripe_config import stripe

# from model.mensagem import msgFields, Message
# from model.atleta import Atleta
# from model.planos import Plano

# class Assinaturas(Resource):
#   @token_verify
#   def get(self, tipo, refreshToken, user_id, id):
#     pass

#   @token_verify
#   def post(self, tipo, refreshToken, user_id, id):
#     if tipo != 'Atleta':
#       logger.error("Usuario sem autorizacao para acessar os atletas")

#       codigo = Message(1, "Usuario sem autorização suficiente!")
#       return marshal(codigo, msgFields), 403
#     try:
#       atleta = Atleta.query.get(user_id)

#       plano = Plano.query.get(id)
#       if plano is None:
#         logger.error(f"Plano de id: {id} nao encontrado")
#         codigo = Message(1, f"Plano de id: {id} não encontrado")
#         return marshal(codigo, msgFields), 404

#       periodoTest = 0
#       if plano.intervalo == "week":
#         periodoTest = 7
#       elif plano.intervalo == "month":
#         periodoTest = 30
#       elif plano.intervalo == "year":
#         periodoTest = 60

#       assinatura = stripe.Subscription.create(
#         customer=atleta.stripe_id,
#         items=[
#           {
#             "plan": plano.id_PlanoStripe
#           }
#         ],
#         trial_period_days=periodoTest
#       )
#     except:
#       pass
