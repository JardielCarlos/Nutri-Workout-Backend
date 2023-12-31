from flask import Flask
from flask_restful import Api
from helpers.mail import mail
from helpers.configCORS import cors
from helpers.database import db, migrate
from dotenv import load_dotenv
from os import getenv

from resources.administradores import Administradores, AdministradorId, AdministradorImg, AdministradorNome

from resources.atletas import AtletaId, AtletaImg, AtletaNome, AtletaPagination, Atletas, RequestNutricionista, RequestPersonal, TabelaAtleta, CardapioAtleta, AtletaIngredientePagination

from resources.cardapioAtleta import CardapioAtletaNutri, CardapioAtletaNutriId, CardapioId
from resources.refeicaoAtleta import RefeicaoAtleta, RefeicaoAtletaId
from resources.ingredienteAtleta import IngredienteAtleta, IngredienteAtletaId, IngredienteAtletaPagination

from resources.login import Login
from resources.logout import Logout

from resources.nutricionistaAtleta import NutricionistaAtleta, NutricionistaAtletaId, NutricionistaAtletaPagination, NutricionistaAtletaNome
from resources.nutricionistas import NutricionistaId, NutricionistaImg, NutricionistaNome,NutricionistaNotificacaoState, NutricionistaNotificacoes, NutricionistaNotificacoesId,NutricionistaPagination, Nutricionistas

from resources.PersonaisTrainer import PersonaisTrainer, PersonalImg, PersonalNotificacoes, PersonalNotificacoesId, PersonalTrainerId, PersonalTrainerNome,PersonalTrainerNotificacaoState, PersonalTrainerPagination
from resources.personalAtleta import PersonalAtleta, PersonalAtletaId, PersonalAtletaPagination, PersonalAtletaNome
from resources.tabelaTreinoAtleta import TabelaTreinoAtleta, TabelaTreinoAtletaId
from resources.ExercicioAtleta import ExerciciosAtleta, ExercicioAtletaId, ExercicioAtletaTabela, ExercicioAtletaTabelaId
from resources.usuario import UsuarioId, UsuarioNome, Usuarios, UsuarioPagination

from resources.produtosNutriWorkOut import ProdutosNutriWorkOut, ProdutosNutriWorkOutId
from resources.planosNutriWorkOut import PlanosNutriWorkOut, PlanosNutriWorkOutId
from resources.cartaoCredito import CartaoCreditoAtleta, CartaoCreditoAtletaId
from resources.assinaturas import Assinaturas
from resources.stripeWebHook import StripeWeebHook

from resources.resetSenha import ResetSenha
from resources.newSenha import NewSenha
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://postgres:senhasecreta@localhost:5432/NutriWorkout"
app.config['SECRET_KEY'] = 'senhasecreta'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = getenv('EMAIL_USER')
app.config['MAIL_PASSWORD'] = getenv('EMAIL_PASS')

db.init_app(app)
cors.init_app(app)
migrate.__init__(app, db)
api = Api(app)
mail.init_app(app)

api.add_resource(Atletas, '/atletas')
api.add_resource(AtletaId, '/atleta/<int:id>')
api.add_resource(AtletaNome, '/atletas/<string:nome>')
api.add_resource(AtletaPagination, '/atletas/<int:id>/<int:max_itens>')
api.add_resource(AtletaImg, '/atleta/imagem/<int:id>')
api.add_resource(RequestPersonal, '/atleta/solicitar-personal')
api.add_resource(RequestNutricionista, '/atleta/solicitar-nutricionista')
api.add_resource(TabelaAtleta, '/atleta/tabelaTreino')
api.add_resource(CardapioAtleta, '/atleta/cardapio')
api.add_resource(CartaoCreditoAtleta, '/cartaoCredito')
api.add_resource(CartaoCreditoAtletaId, '/cartaoCredito/<int:id>')
api.add_resource(ResetSenha, "/solicitar-recuperacao")
api.add_resource(NewSenha, '/reset_password/<string:token>')

api.add_resource(AtletaIngredientePagination, '/atleta/ingrediente/<int:id_cardapio>/<int:id_refeicao>/<int:id_page>/<int:max_itens>/<int:id_nutri>')

api.add_resource(PersonaisTrainer, '/personalTrainer')
api.add_resource(PersonalTrainerId, '/personalTrainer/<int:id>')
api.add_resource(PersonalTrainerNome, '/personalTrainer/<string:nome>')
api.add_resource(PersonalNotificacoes, '/personalTrainer/notificacoes')
api.add_resource(PersonalNotificacoesId, '/personalTrainer/notificacoes/<int:id>')
api.add_resource(PersonalTrainerNotificacaoState, '/personalTrainer/notificacao')
api.add_resource(PersonalTrainerPagination, '/personalTraineres/<int:id>/<int:max_itens>')
api.add_resource(PersonalImg, '/personal/imagem/<int:id>')
api.add_resource(PersonalAtleta, '/personal/atleta')
api.add_resource(PersonalAtletaNome, '/personal/atleta/<string:nome>')
api.add_resource(PersonalAtletaId, '/personal/atleta/<int:id>')
api.add_resource(PersonalAtletaPagination, '/personal/atleta/<int:id>/<int:max_itens>')
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
api.add_resource(NutricionistaPagination, "/nutricionistas/<int:id>/<int:max_itens>")
api.add_resource(NutricionistaImg, '/nutricionista/imagem/<int:id>')
api.add_resource(NutricionistaAtleta, '/nutricionista/atleta')
api.add_resource(NutricionistaAtletaId, '/nutricionista/atleta/<int:id>')
api.add_resource(NutricionistaAtletaNome, '/nutricionista/atleta/<string:nome>')
api.add_resource(NutricionistaAtletaPagination, '/nutricionista/atleta/<int:id>/<int:max_itens>')
api.add_resource(CardapioAtletaNutri, '/nutricionista/atleta/cardapio')
api.add_resource(CardapioAtletaNutriId, '/nutricionista/atleta/cardapio/<int:id>')
api.add_resource(CardapioId, '/nutricionista/atleta/cardapioId/<int:id>')
api.add_resource(RefeicaoAtleta, '/nutricionista/atleta/refeicao/<int:id_cardapio>')
api.add_resource(RefeicaoAtletaId, '/nutricionista/atleta/refeicao/<int:id_cardapio>/<int:id>')
api.add_resource(IngredienteAtleta, '/nutricionista/atleta/ingrediente/<int:id_cardapio>/<int:id_refeicao>')
api.add_resource(IngredienteAtletaPagination, '/nutricionista/atleta/ingrediente/<int:id_cardapio>/<int:id_refeicao>/<int:id_page>/<int:max_itens>')
api.add_resource(IngredienteAtletaId, '/nutricionista/atleta/ingrediente/<int:id_cardapio>/<int:id_refeicao>/<int:id>')

api.add_resource(Administradores, '/administradores')
api.add_resource(AdministradorId, '/administradores/<int:id>')
api.add_resource(AdministradorNome, '/administradores/<string:nome>')
api.add_resource(AdministradorImg, '/administrador/imagem/<int:id>')

api.add_resource(Usuarios, '/usuarios')
api.add_resource(UsuarioId, '/usuario/<int:id>')
api.add_resource(UsuarioNome, '/usuarios/<string:nome>')
api.add_resource(UsuarioPagination, '/usuarios/<int:id>/<int:max_itens>')

api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')

api.add_resource(ProdutosNutriWorkOut, '/produtos')
api.add_resource(ProdutosNutriWorkOutId, '/produtos/<int:id>')

api.add_resource(PlanosNutriWorkOut, '/planos')
api.add_resource(PlanosNutriWorkOutId, '/planos/<int:id>')

api.add_resource(Assinaturas, '/assinaturas')
api.add_resource(StripeWeebHook, '/webhook')

if __name__ == '__main__':
  app.run(debug=True)
