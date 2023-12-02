from flask_restful import Resource, marshal, reqparse

from helpers.auth.token_verifier import token_verify
from helpers.database import db
from helpers.logger import logger
from model.atleta import Atleta, atletaFields
from model.mensagem import Message, msgFields
from model.notificacaoNutricionista import NotificacaoNutricionista
from model.nutricionista import Nutricionista, nutricionistaAtletasPaginationFields

parser = reqparse.RequestParser()


parser.add_argument("massaMagra", type=str, help="Massa magra não informada", required=False)
parser.add_argument("massaGorda", type=str, help="Massa gorda não informada", required=False)
parser.add_argument("altura", type=str, help="Altura não informada", required=False)
parser.add_argument("peso", type=str, help="peso não informado", required=False)

class NutricionistaAtleta(Resource):
  @token_verify
  def get(self, tipo, refreshToken, user_id):
    if tipo != "Nutricionista":
      logger.error("Usuario sem autorizacao para acessar os atletas associados ao nutricionista")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    nutricionista = Nutricionista.query.get(user_id)
    return marshal(nutricionista.atletas, atletaFields), 200

class NutricionistaAtletaNome(Resource):
  @token_verify
  def get(self, tipo, refreshToken, user_id, nome):
    if tipo != "Nutricionista":
      logger.error("Usuario sem autorizacao para acessar os atletas associados ao nutricionista")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    atletas = Atleta.query.filter(db.and_(Atleta.nome.ilike(f"%{nome}%"), Atleta.nutricionista_id == user_id)).all()
    return marshal(atletas, atletaFields), 200

class NutricionistaAtletaPagination(Resource):
  @token_verify
  def get(self, tipo, refreshToken, user_id, id, max_itens):
    if tipo != "Nutricionista":
      logger.error("Usuario sem autorizacao para acessar os atletas associados ao nutricionista")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    nutricionista = Nutricionista.query.get(user_id)
    atletasPagination = Atleta.query.filter_by(nutricionista_id=user_id).paginate(page=id, per_page=max_itens, error_out=False)

    data = {"atletasNutricionista": atletasPagination.items, "totalAtletas": len(nutricionista.atletas)}

    return marshal(data, nutricionistaAtletasPaginationFields), 200

class NutricionistaAtletaId(Resource):
  @token_verify
  def get(self, tipo, refreshToken, user_id, id):
    if tipo != "Nutricionista":
      logger.error("Usuario sem autorizacao para acessar os atletas associados ao nutricionista")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    atleta = Atleta.query.get(id)
    if atleta is None:
      logger.error(f"Atleta de id: {id} nao encontrado")

      codigo = Message(1, f"Atleta de id: {id} não encontrado")
      return marshal(codigo, msgFields), 200

    nutricionista = Nutricionista.query.get(user_id)

    if atleta not in nutricionista.atletas:
      logger.error(f"Atleta de id:{id} associado a outro nutricionista")

      codigo = Message(1, f"Atleta de id: {id} não associado ao nutricionista")
      return marshal(codigo, msgFields), 400

    return marshal(atleta, atletaFields), 200

  @token_verify
  def put(self, tipo, refreshToken, user_id, id):
    args = parser.parse_args()

    if tipo != "Nutricionista":
      logger.error("Usuario sem autorizacao para acessar os atletas associados ao nutricionista")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    try:
      atleta = Atleta.query.get(id)
      if atleta is None:
        logger.error(f"Atleta de id: {id} nao encontrado")

        codigo = Message(1, f"Atleta de id: {id} não encontrado")
        return marshal(codigo, msgFields), 200

      nutricionista = Nutricionista.query.get(user_id)

      if atleta not in nutricionista.atletas:
        logger.error(f"Atleta de id:{id} associado a outro nutricionista")

        codigo = Message(1, f"Atleta de id: {id} não associado ao nutricionista")
        return marshal(codigo, msgFields), 400

      atleta.massaMagra = args["massaMagra"]
      atleta.massaGorda = args["massaGorda"]
      atleta.altura = args["altura"]
      atleta.peso = args["peso"]
      if args["altura"] is not None and args["peso"] is not None:
        imc = round(float(args["peso"])/float(args["altura"])**2, 2)
        atleta.imc = imc

        if imc <= 18.5:
          atleta.statusImc = "Abaixo do peso"
        elif imc > 18.5 and imc <= 24.9:
          atleta.statusImc = "Peso normal"
        elif imc > 24.9 and imc <= 29.9:
          atleta.statusImc = "Pré-obesidade"
        elif imc > 29.9 and imc <= 34.9:
          atleta.statusImc = "Obesidade Grau 1"
        elif imc > 34.9 and imc <= 39.9:
          atleta.statusImc = "Obesidade Grau 2"
        elif imc >= 40:
          atleta.statusImc = "Obesidade Grau 3"
      else:
        atleta.imc = None
        atleta.statusImc = None

      db.session.add(atleta)
      db.session.commit()
      return marshal(atleta, atletaFields), 200
    except:
      logger.error(f"Nao foi possivel atualizar as informacoes do atleta de id: {id}")

      codigo = Message(2, f"Não foi possível atualizar as informaçõesdo atleta de id: {id}")
      return marshal(codigo, msgFields), 400

  @token_verify
  def delete(self, tipo, refreshToken, user_id, id):
    if tipo != "Nutricionista":
      logger.error("Usuario sem autorizacao para acessar os atletas associados ao nutricionista")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    atleta = Atleta.query.get(id)
    if atleta is None:
      logger.error(f"Atleta de id: {id} nao encontrado")

      codigo = Message(1, f"Atleta de id: {id} não encontrado")
      return marshal(codigo, msgFields), 200

    nutricionista = Nutricionista.query.get(user_id)

    if atleta not in nutricionista.atletas:
      logger.error(f"Atleta de id:{id} associado a outro nutricionista")

      codigo = Message(1, f"Atleta de id: {id} não associado ao nutricionista")
      return marshal(codigo, msgFields), 400

    atleta.nutricionista_id = None
    notificacaoAtleta = NotificacaoNutricionista.query.filter_by(atleta_id=atleta.usuario_id).first()
    notificacaoAtleta.solicitacao= False

    db.session.add(notificacaoAtleta)
    db.session.add(atleta)
    db.session.commit()

    logger.info(f"Atleta de id: {id} deletado com sucesso")
    return {}, 200
