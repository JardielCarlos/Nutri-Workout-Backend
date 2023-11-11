from flask_restful import Resource
from helpers.stripe_config import stripe

class PlanosNutriWorkOut(Resource):
  def get(self):
    pass

  def post(self):
    try:
      stripe.Plan.create()
    except:
      pass

