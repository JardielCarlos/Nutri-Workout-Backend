from flask import Flask
from flask_restful import Api
from helpers.database import db, migrate
from helpers.configCORS import cors

from resources.atletas import Atletas, AtletaId, AtletaNome
from resources.PersonaisTrainer import PersonaisTrainer, PersonalTrainerId, PersonalTrainerNome
from resources.nutricionistas import Nutricionistas, NutricionistaId, NutricionistaNome
from resources.administradores import Administradores, AdministradorId, AdministradorNome

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://postgres:senhasecreta@localhost:5432/NutriWorkout"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
cors.init_app(app)
migrate.__init__(app, db)
api = Api(app)

api.add_resource(Atletas, '/atletas')
api.add_resource(AtletaId, '/atletas/<int:id>')
api.add_resource(AtletaNome, '/atletas/<string:nome>')

api.add_resource(PersonaisTrainer, '/personalTrainer')
api.add_resource(PersonalTrainerId, '/personalTrainer/<int:id>')
api.add_resource(PersonalTrainerNome, '/personalTrainer/<string:nome>')

api.add_resource(Nutricionistas, '/nutricionista')
api.add_resource(NutricionistaId, '/nutricionista/<int:id>')
api.add_resource(NutricionistaNome, '/nutricionista/<string:nome>')

api.add_resource(Administradores, '/administradores')
api.add_resource(AdministradorId, '/administradores/<int:id>')
api.add_resource(AdministradorNome, '/administradores/<string:nome>')

if __name__ == '__main__':
  app.run(debug=True)
