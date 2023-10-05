from flask import Flask
from flask_restful import Api
from helpers.database import db, migrate
from helpers.configCORS import cors
from model.consumerRabbitmq import RabbitmqConsumer
from json import loads
from flask_socketio import SocketIO, emit

from model.notificacaoPersonal import NotificacaoPersonal
from model.atleta import Atleta

from resources.atletas import Atletas, AtletaId, AtletaNome, RequestPersonal, AtletaPagination
from resources.PersonaisTrainer import PersonaisTrainer, PersonalTrainerId, PersonalTrainerNome, PersonalNotificacoes, PersonalNotificacoesId, PersonalTrainerPagination
from resources.nutricionistas import Nutricionistas, NutricionistaId, NutricionistaNome, NutricionistaPagination
from resources.administradores import Administradores, AdministradorId, AdministradorNome
from resources.login import Login
from resources.logout import Logout

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://postgres:senhasecreta@localhost:5432/NutriWorkout"
app.config['SECRET_KEY'] = 'senhasecreta'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
# socketio = SocketIO(app, cors_allowed_origins="*")
cors.init_app(app)
migrate.__init__(app, db)
api = Api(app)

# @socketio.on('connect')
# def test_connect():
#   emit('after connect',  {'data':'Lets dance'})

# def minha_callback(ch, method, properties, body):
#   with app.app_context():
#     msg = loads(body.decode('utf-8'))
#     atleta = Atleta.query.get(msg["id"])
#     notificacao = NotificacaoPersonal(msg["nome"], msg["email"], msg["mensagem"], atleta)
    
#     db.session.add(notificacao)
#     db.session.commit()
#   # socketio.emit('notification', {'data': loads(body.decode('utf-8'))})

# rabbitmqConsumer = RabbitmqConsumer("solicitacao_personal", minha_callback)
# rabbitmqConsumer.start()

api.add_resource(Atletas, '/atletas')
api.add_resource(AtletaId, '/atletas/<int:id>')
api.add_resource(AtletaNome, '/atletas/<string:nome>')
api.add_resource(RequestPersonal, '/atleta/solicitar-personal/<int:id>')
api.add_resource(AtletaPagination, '/atletasp/<int:id>')

api.add_resource(PersonaisTrainer, '/personalTrainer')
api.add_resource(PersonalTrainerId, '/personalTrainer/<int:id>')
api.add_resource(PersonalTrainerNome, '/personalTrainer/<string:nome>')
api.add_resource(PersonalNotificacoes, '/personalTrainer/notificacoes')
api.add_resource(PersonalNotificacoesId, '/personalTrainer/notificacoes/<int:id>')
api.add_resource(PersonalTrainerPagination, '/personalTraineres/<int:id>')


api.add_resource(Nutricionistas, '/nutricionista')
api.add_resource(NutricionistaId, '/nutricionista/<int:id>')
api.add_resource(NutricionistaNome, '/nutricionista/<string:nome>')
api.add_resource(NutricionistaPagination, "/nutricionistas/<int:id>")

api.add_resource(Administradores, '/administradores')
api.add_resource(AdministradorId, '/administradores/<int:id>')
api.add_resource(AdministradorNome, '/administradores/<string:nome>')

api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')

if __name__ == '__main__':
  app.run(debug=True)
  # socketio.run(app, debug=True)
