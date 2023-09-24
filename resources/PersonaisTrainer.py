from flask_restful import marshal, Resource, reqparse
from helpers.logger import logger
from helpers.database import db
from password_strength import PasswordPolicy
from validate_docbr import CPF
from sqlalchemy.exc import IntegrityError
import re

from model.mensagem import Message, msgFields
from model.personalTrainer import PersonalTrainer, personalTrainerFields

parser = reqparse.RequestParser()
parser.add_argument("nome", type=str, help="Nome não informado", required=False)
parser.add_argument("email", type=str, help="email não informado", required=False)
parser.add_argument("senha", type=str, help="senha não informado", required=False)
parser.add_argument("cpf", type=str, help="cpf não informado", required=False)
parser.add_argument("cref", type=str, help="cref não informado", required=False)
parser.add_argument("novaSenha", type=str, help="nova senha não informado", required=False)

padrao_email = r'^[\w\.-]+@[\w\.-]+\.\w+$'
# padraoCref = r'CREF \d{6}-G\/[A-Z]{2}'
policy = PasswordPolicy.from_names(
  length =8,
  uppercase = 1,
  numbers=1,
  special=1
)

cpfValidate = CPF()

"056.998.308-80"
"290.297.910-04"
"607.298.816-44"
"167.167.991-17"
"677.986.197-98"

"CREF 123456-G/SP"
"CREF 654321-G/RJ"
"CREF 789012-G/ES"
"CREF 210987-G/BA"
"CREF 345678-P/RS"
"CREF 876543-P/SC"

class PersonaisTrainer(Resource):
  def get(self):
    return marshal(PersonalTrainer.query.all(), personalTrainerFields), 200
  
  def post(self):
    args = parser.parse_args()

    try:
      if len(args["nome"]) == 0:
        logger.info("Nome não informado")

        codigo = Message(1, "Nome não informado")
        return marshal(codigo, msgFields), 400
      
      if not args['email']:
        codigo = Message(1, "email não informada")
        return marshal(codigo, msgFields), 400
      
      if re.match(padrao_email, args['email']) == None:
        codigo = Message(1, "Email no formato errado")
        return marshal(codigo, msgFields), 400
      
      if not args["cpf"]:
        codigo = Message(1, "cpf não informado")
        return marshal(codigo, msgFields), 400
      
      if not cpfValidate.validate(args["cpf"]):
        logger.error(f"CPF {args['cpf']} não valido")

        codigo = Message(1, f"CPF {args['cpf']} não valido")
        return marshal(codigo, msgFields), 400
      
      if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', args["cpf"]):
        logger.error(f"CPF {args['cpf']} no formato errado")

        codigo = Message(1, "CPF no formato errado")
        return marshal(codigo, msgFields), 400

      if not args['senha']:
        codigo = Message(1, "Senha não informada")
        return marshal(codigo, msgFields), 400
      
      verifySenha = policy.test(args['senha'])
      if len(verifySenha) != 0:
        codigo = Message(1, "Senha no formato errado")
        return marshal(codigo, msgFields), 400
      
      if not args['cref']:
        codigo = Message(1, "CREF não informada")
        return marshal(codigo, msgFields), 400
      
      if not re.match(r'CREF \d{6}-G\/[A-Z]{2}', args['cref']):
        codigo = Message(1, "CREF no formato errado")
        return marshal(codigo, msgFields), 400

      personalTrainer = PersonalTrainer(args["nome"], args["email"], args["senha"], args["cpf"], args["cref"])

      db.session.add(personalTrainer)
      db.session.commit()

      logger.info(f"Personal Trainer de id: {personalTrainer.id} criado com sucesso")
      return marshal(personalTrainer, personalTrainerFields), 201
    except IntegrityError as e:
      if 'cpf' in str(e.orig):
        codigo = Message(1, "CPF já cadastrado no sistema")
        return marshal(codigo, msgFields), 400
      
      elif 'email' in str(e.orig):
        codigo = Message(1, "Email já cadastrado no sistema")
        return marshal(codigo, msgFields), 400
      
    except:
      logger.error("Erro ao cadastrar o Personal Trainer")

      codigo = Message(2, "Erro ao cadastrar o Personal Trainer")
      return marshal(codigo, msgFields), 400
    
class PersonalTrainerId(Resource):
  def get(self, id):
    pass
  def delete(self, id):
    personalTrainer = PersonalTrainer.query.get(id)

    if personalTrainer is None:
      logger.error(f"Personal Trainer de id: {id} nao encotrado")

      codigo = Message(1, f"Personal Trainer de id: {id} não encontrado")
      return marshal(codigo, msgFields), 404
    
    db.session.delete(personalTrainer)
    db.session.commit()

    logger.info(f"Atleta de id: {id} deletado com sucesso")
    return {}, 200