from flask_restful import Resource, marshal, reqparse

from helpers.auth.token_verifier import token_verify
from helpers.database import db
from helpers.logger import logger
from model.exercicioAtleta import ExercicioAtleta, exercicioFields
from model.mensagem import Message, msgFields
from model.tabelaTreino import TabelaTreino

parser = reqparse.RequestParser()

parser.add_argument("idTabela", type=int, help="id da tabela não informada", required=False)
parser.add_argument("musculoTrabalhado", type=str, help="musculo trabalhado não informado", required=True)
parser.add_argument("nomeExercicio", type=str, help="Nome do exercicio informado", required=True)
parser.add_argument("series", type=int, help="Séries não informada", required=True)
parser.add_argument("kg", type=int, help="kg não informado", required=True)
parser.add_argument("repeticao", type=int, help="repetições não informada", required=True)
parser.add_argument("descanso", type=int, help="descanso não informado", required=True)
parser.add_argument("unidadeDescanso", type=str, help="unidade do descanso não informado", required=True)
parser.add_argument("observacoes", type=str, help="observações não informadas", required=False)

class ExerciciosAtleta(Resource):
  @token_verify
  def post(self, tipo, refreshToken, user_id):
    if tipo != "Personal":
      logger.error("Usuario sem autorizacao para acessar os exercicios do atleta")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403
    try:
      args = parser.parse_args()
      if args["idTabela"] is None:
        logger.error("id da tabela nao informado")

        codigo = Message(1, "id da tabela não informada")
        return marshal(codigo, msgFields), 200
      if len(args["musculoTrabalhado"]) <= 2:
          logger.error(f"Escreva o nome de um musculo valido")

          codigo = Message(1, f"Escreva o nome de um musculo válido")
          return marshal(codigo, msgFields), 400

      if len(args['nomeExercicio']) <= 2:
        logger.error(f"Escreva o nome de um exercicio valido")

        codigo = Message(1, f"Escreva o nome de um exercicio válido")
        return marshal(codigo, msgFields), 400

      tabelaTreino = TabelaTreino.query.get(args["idTabela"])

      if tabelaTreino is None:
        logger.error(f"Tabela de id: {args['idTabela']} nao encontrado")

        codigo = Message(1, f"Tabela de id: {args['idTabela']} não encontrado")
        return marshal(codigo, msgFields), 400

      exercicio = ExercicioAtleta(tabelaTreino, args["musculoTrabalhado"], args["nomeExercicio"], args["series"], args["repeticao"], args["kg"], args["descanso"], args["unidadeDescanso"], args["observacoes"])

      tabelaTreino.exercicios.append(exercicio)

      db.session.add(tabelaTreino)
      db.session.add(exercicio)
      db.session.commit()

      logger.info(f"Exercicio adicionado a tabela de treino")
      return marshal(exercicio, exercicioFields), 201
    except:
      logger.error("Erro ao cadastrar o exercicio")

      codigo = Message(2, "Erro ao cadastrar o exercicio")
      return marshal(codigo, msgFields), 400

class ExercicioAtletaId(Resource):
  @token_verify
  def put(self, tipo, refreshToken, user_id, id):
    args = parser.parse_args()
    if tipo != "Personal":
      logger.error("Usuario sem autorizacao para acessar os exercicios do atleta")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    exercicio = ExercicioAtleta.query.get(id)
    if exercicio is None:
      logger.error(f"Exercicio de id: {id} nao encontrado")

      codigo = Message(1, f"Exercicio de id: {id} não encontrado")
      return marshal(codigo, msgFields), 200

    if len(args["musculoTrabalhado"]) <= 2:
        logger.error(f"Escreva o nome de um musculo valido")

        codigo = Message(1, f"Escreva o nome de um musculo válido")
        return marshal(codigo, msgFields), 400

    if len(args['nomeExercicio']) <= 2:
      logger.error(f"Escreva o nome de um exercicio valido")

      codigo = Message(1, f"Escreva o nome de um exercicio válido")
      return marshal(codigo, msgFields), 400

    exercicio.musculoTrabalhado = args["musculoTrabalhado"]
    exercicio.nomeExercicio = args["nomeExercicio"]
    exercicio.series = args["series"]
    exercicio.kg = args["kg"]
    exercicio.repeticao = args["repeticao"]
    exercicio.descanso = args["descanso"]
    exercicio.unidadeDescanso = args["unidadeDescanso"]
    exercicio.observacoes = args["observacoes"]

    db.session.add(exercicio)
    db.session.commit()
    logger.info(f"Exercicio de id: {id} atualizado com sucesso")
    return marshal(exercicio, exercicioFields)

  @token_verify
  def delete(self, tipo, refreshToken, user_id, id):
    if tipo != "Personal":
      logger.error("Usuario sem autorizacao para acessar os exercicios do atleta")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    exercicio = ExercicioAtleta.query.get(id)
    if exercicio is None:
      logger.error(f"Exercicio de id: {id} nao encontrado")

      codigo = Message(1, f"Exercicio de id: {id} não encontrado")
      return marshal(codigo, msgFields), 200

    db.session.delete(exercicio)
    db.session.commit()

    logger.info(f"Exercicio de id: {id} nao encontrado")
    return {}, 200

class ExercicioAtletaTabela(Resource):
  @token_verify
  def get(self, tipo, refreshToken, user_id, id_tabela):
    if tipo != "Personal":
      logger.error("Usuario sem autorizacao para acessar os exercicios do atleta")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    tabelaTreino = TabelaTreino.query.get(id_tabela)

    if tabelaTreino is None:
      logger.error(f"Tabela de treino de id: {id_tabela} nao encontrada")

      codigo = Message(1, f"Tabela de treino de id: {id_tabela} não encontrada")
      return marshal(codigo, msgFields), 200

    return marshal(tabelaTreino.exercicios, exercicioFields), 200

class ExercicioAtletaTabelaId(Resource):
  @token_verify
  def get(self, tipo, refreshToken, user_id, id_tabela, id_exercicio):
    if tipo != "Personal":
      logger.error("Usuario sem autorizacao para acessar os exercicios do atleta")
      codigo = Message(1, "Usuario sem autorização suficiente!")
      return marshal(codigo, msgFields), 403

    tabelaTreino = TabelaTreino.query.get(id_tabela)

    if tabelaTreino is None:
      logger.error(f"Tabela de treino de id: {id_tabela} nao encontrada")

      codigo = Message(1, f"Tabela de treino de id: {id_tabela} não encontrada")
      return marshal(codigo, msgFields), 200

    exercicio = ExercicioAtleta.query.get(id_exercicio)

    if exercicio is None:
      logger.error(f"Exercicio de id: {id_exercicio} nao encontrada")

      codigo = Message(1, f"Exercicio de id: {id_exercicio} não encontrada")
      return marshal(codigo, msgFields), 200

    if exercicio not in tabelaTreino.exercicios:
      logger.error(f"Exercicio nao encontrado na tabela de treino")

      codigo = Message(1, f"Exercicio não encontrado na tabela de treino")
      return marshal(codigo, msgFields), 200

    return marshal(exercicio, exercicioFields), 200
