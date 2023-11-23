from flask import url_for
from flask_restful import Resource, reqparse, marshal
from flask_mail import Message
from helpers.mail import mail
from helpers.logger import logger
from model.mensagem import  Message, msgFields
from model.usuario import Usuario
from jwt import encode
from datetime import datetime, timedelta
parser = reqparse.RequestParser()

parser.add_argument("email", type=str, help="Email não informado", required=False)

class ResetSenha(Resource):
  def post(self):
    args = parser.parse_args()
    try:
      if args["email"] is None:
        logger.error("Email nao informado")
        codigo = Message(1, "Email não informado")
        return marshal(codigo, msgFields), 400

      usuario = Usuario.query.filter_by(email=args["email"]).first()
      msg = Message("Redefinir senha", sender="serviceemail927@gmail.com", recipients=[usuario.email])

      payload = {
        "email": usuario.email,
        "exp": datetime.utcnow() + timedelta(minutes=30)
      }
      token = encode(payload, "1234", algorithm="HS256")

      reset_url = url_for('reset_password', token=token, _external=True)
      msg.body = f'''Para redefinir sua senha, visite o seguinte link:
      {reset_url}
      Se você não fez esta solicitação, simplesmente ignore este e-mail e nenhuma alteração será feita.
      '''
      msg.html = f'''
        <html>
          <body>
              <center>
                  <h1>Redefinir Senha</h1>
                  <p>Para redefinir sua senha, clique no botão abaixo:</p>
                  <a href="{reset_url}" style="display: inline-block; padding: 10px 20px; color: white; background-color: #007BFF; text-decoration: none;">Redefinir Senha</a>
                  <p>Se você não fez esta solicitação, simplesmente ignore este e-mail e nenhuma alteração será feita.</p>
              </center>
          </body>
        </html>
      '''
      mail.send(msg)

    except:
      pass
