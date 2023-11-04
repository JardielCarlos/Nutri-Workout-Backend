from flask import Flask
from flask_restful import Api
from helpers.configCORS import cors
from helpers.database import db, migrate

from resources.administradores import Administradores, AdministradorId, AdministradorImg, AdministradorNome

from resources.atletas import AtletaId, AtletaImg, AtletaNome, AtletaPagination, Atletas, RequestNutricionista, RequestPersonal, TabelaAtleta

from resources.login import Login
from resources.logout import Logout

from resources.nutricionistaAtleta import NutricionistaAtleta
from resources.nutricionistas import NutricionistaId, NutricionistaImg, NutricionistaNome,NutricionistaNotificacaoState, NutricionistaNotificacoes, NutricionistaNotificacoesId,NutricionistaPagination, Nutricionistas

from resources.PersonaisTrainer import PersonaisTrainer, PersonalImg, PersonalNotificacoes, PersonalNotificacoesId, PersonalTrainerId, PersonalTrainerNome,PersonalTrainerNotificacaoState, PersonalTrainerPagination
from resources.personalAtleta import PersonalAtleta
from resources.tabelaTreinoAtleta import TabelaTreinoAtleta, TabelaTreinoAtletaId
from resources.ExercicioAtleta import ExerciciosAtleta, ExercicioAtletaId, ExercicioAtletaTabela, ExercicioAtletaTabelaId
from resources.usuario import UsuarioId, UsuarioNome, Usuarios

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://postgres:senhasecreta@localhost:5432/NutriWorkout"
app.config['SECRET_KEY'] = 'senhasecreta'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
cors.init_app(app)
migrate.__init__(app, db)
api = Api(app)

api.add_resource(Atletas, '/atletas')
api.add_resource(AtletaId, '/atleta/<int:id>')
api.add_resource(AtletaNome, '/atletas/<string:nome>')
api.add_resource(AtletaPagination, '/atletas/<int:id>')
api.add_resource(AtletaImg, '/atleta/imagem/<int:id>')
api.add_resource(RequestPersonal, '/atleta/solicitar-personal')
api.add_resource(RequestNutricionista, '/atleta/solicitar-nutricionista')
api.add_resource(TabelaAtleta, '/atleta/tabelaTreino/<int:id>')

api.add_resource(PersonaisTrainer, '/personalTrainer')
api.add_resource(PersonalTrainerId, '/personalTrainer/<int:id>')
api.add_resource(PersonalTrainerNome, '/personalTrainer/<string:nome>')
api.add_resource(PersonalNotificacoes, '/personalTrainer/notificacoes')
api.add_resource(PersonalNotificacoesId, '/personalTrainer/notificacoes/<int:id>')
api.add_resource(PersonalTrainerNotificacaoState, '/personalTrainer/notificacao')
api.add_resource(PersonalTrainerPagination, '/personalTraineres/<int:id>')
api.add_resource(PersonalImg, '/personal/imagem/<int:id>')
api.add_resource(PersonalAtleta, '/personal/atleta')
api.add_resource(TabelaTreinoAtleta, '/personal/atleta/tabelaTreino')
api.add_resource(TabelaTreinoAtletaId, '/personal/atleta/tabelaTreino/<int:id>')
api.add_resource(ExerciciosAtleta, '/personal/atleta/tabelaTreino/exercicio')
api.add_resource(ExercicioAtletaId, '/personal/atleta/tabelaTreino/exercicio/<int:id>')
api.add_resource(ExercicioAtletaTabela, '/personal/atleta/tabelaTreino/exercicios/<int:id_tabela>')
api.add_resource(ExercicioAtletaTabelaId, '/personal/atleta/tabelaTreino/exercicios/<int:id_tabela>/<int:id_exercicio>')


api.add_resource(Nutricionistas, '/nutricionista')
api.add_resource(NutricionistaId, '/nutricionista/<int:id>')
api.add_resource(NutricionistaNome, '/nutricionista/<string:nome>')
api.add_resource(NutricionistaNotificacoes, '/nutricionista/notificacoes')
api.add_resource(NutricionistaNotificacoesId, '/nutricionista/notificacoes/<int:id>')
api.add_resource(NutricionistaNotificacaoState, '/nutricionista/notificacao')
api.add_resource(NutricionistaPagination, "/nutricionistas/<int:id>")
api.add_resource(NutricionistaImg, '/nutricionista/imagem/<int:id>')
api.add_resource(NutricionistaAtleta, '/nutricionista/atleta')

api.add_resource(Administradores, '/administradores')
api.add_resource(AdministradorId, '/administradores/<int:id>')
api.add_resource(AdministradorNome, '/administradores/<string:nome>')
api.add_resource(AdministradorImg, '/administrador/imagem/<int:id>')

api.add_resource(Usuarios, '/usuarios')
api.add_resource(UsuarioId, '/usuarios/<int:id>')
api.add_resource(UsuarioNome, '/usuarios/<string:nome>')

api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')

if __name__ == '__main__':
  app.run(debug=True)
