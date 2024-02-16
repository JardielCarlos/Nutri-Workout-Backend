<h1 align="center" style="font-weight: bold;">Nutri Workout 💻</h1>

<p align="center">
 <a href="#tech">Technologies</a> •
 <a href="#started">Getting Started</a> •
  <a href="#routes">API Endpoints</a> •
 <a href="#colab">Collaborators</a> •
 <a href="#contribute">Contribute</a>
</p>

<p align="center">
    <b>Descrição simples do que o projeto faz e como usá-lo.</b>
</p>

<h2 id="technologies">💻 Technologies</h2>

- lista de todas as tecnologias usada
- Python
- Flask
- SqlAlchemy
- Flask-Migrate
- Flask-Mail
- Stripe
- PyJWT
- PostgreSQL

<h2 id="started">🚀 Getting started</h2>

- ### Como executar o projeto localmente.

<h3>Prerequisites</h3>

lista de todos os pré-requisitos necessários para execução do projeto.

- [Python](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/)

<h3>Cloning</h3>

Como clonar o projeto

```bash
git clone https://github.com/JardielCarlos/Nutri-Workout-Backend.git
```

<h3>Config .env variables</h2>

Use `.env.example` como referência para criar seu arquivo de configuração `.env` com suas credenciais

```yaml
TOKEN_KEY= {SECRET_KEY}
EXP_TIME_HRS= {TEMPO_DURACAO_HORAS}
REFRESH_TIME_HRS= {TEMPO_RENOVACAO_HORAS}
SECRET_STRIPE= {SECRET_KEY_STRIPE}
EMAIL_USER= {EMAIL_USER}
EMAIL_PASS= {SENHA_EMAIL_APP}
```

<h2 id="routes">📍 API Endpoints</h2>

lista de algumas rotas da API e quais são os corpos de solicitação esperados.
​
| route | description
|----------------------|-----------------------------------------------------
| <kbd>POST /login</kbd> | Autenticar usuário na API [detalhes da requisição](#post-login)
| <kbd>POST /atletas</kbd> | Criar um atleta [detalhes da requisição](#post-atleta)
| <kbd>GET /usuarios</kbd> | usuários do sistema [detalhes da resposta](#get-usuarios)
| <kbd>GET /atleta/tabelaTreino</kbd> | Tabela de treino do atleta [detalhes da requisição](#get-tabelaTreino-atleta)
| <kbd>GET /atleta/cardapio</kbd> | Cardápio do atleta [detalhes da requisição](#get-cardapio-atleta)

<h3 id="post-login">POST /login</h3>

**REQUEST**

```json
{
  "email": "personal@gmail.com",
  "senha": "123456Ab%"
}
```

**RESPONSE**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aXBvIjoiUGVyc29uYWwiLCJpZCI6MywiZXhwIjoxNzAyMzUyMDUxfQ.Uwah41srBUH-zqK5JRjnDyBGXBvEKadFWbS0cWWTTMM",
  "tipo": "Personal",
  "user_id": 3,
  "sigla": "pt"
}
```

<h3 id="post-atleta">POST /atletas</h3>

**REQUEST**

```json
{
  "nome": "Marcus",
  "sobrenome": "matheus",
  "email": "marcos@gmail.com",
  "senha": "123456Ab%",
  "cpf": "289.242.590-59"
}
```

**RESPONSE**

```json
{
  "atleta": {
    "id": 7,
    "nome": "Marcus",
    "sobrenome": "matheus",
    "email": "marcos@gmail.com",
    "cpf": "289.242.590-59",
    "tipo": "Atleta",
    "massaMagra": null,
    "massaGorda": null,
    "altura": null,
    "peso": null,
    "imc": null,
    "statusImc": null,
    "statusPagamento": "Inativo",
    "atletaImg": "http://localhost:5000/atleta/imagem/7"
  },
  "token": "yJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aXBvIjoiUGVyc29uYWwiLCJpZCI6MywiZXhwIjoxNzAyMzUyMDUxfQ.JpZCI6MywsrBUH-zqK5JR"
}
```

<h3 id="get-usuarios">GET /usuarios</h3>

**RESPONSE**

```json
[
  {
    "id": 1,
    "nome": "Jardiel",
    "sobrenome": "Carlos",
    "email": "jardiel@gmail.com",
    "cpf": "705.004.404-09",
    "tipo": "Atleta",
    "sigla": "JC",
    "urlImg": "http://localhost:5000/atleta/imagem/1"
  },
  {
    "id": 3,
    "nome": "personalTest",
    "sobrenome": "test",
    "email": "personal@gmail.com",
    "cpf": "402.387.270-92",
    "tipo": "Personal",
    "sigla": "pt",
    "urlImg": "http://localhost:5000/personal/imagem/3"
  },
  {
    "id": 5,
    "nome": "adminsitradorTest ",
    "sobrenome": "test",
    "email": "administrador@gmail.com",
    "cpf": "401.828.470-55",
    "tipo": "Administrador",
    "sigla": "at",
    "urlImg": "http://localhost:5000/administrador/imagem/5"
  }
]
```

<h3 id="get-tabelaTreino-atleta">GET /atleta/tabelaTreino</h3>

**RESPONSE**

```json
{
	"id": 4,
	"semanaInicio": "2023-05-10",
	"semanaFim": "2023-05-21",
	"exercicios": [
		{
			"id": 2,
			"diaSemana": "segunda",
			"musculoTrabalhado": "Tríceps",
			"nomeExercicio": "Tríceps na polia",
			"series": 4,
			"kg": 8,
			"repeticao": 12,
			"descanso": 45,
			"unidadeDescanso": "segundos",
			"observacoes": "Manter os cotovelos próximos ao corpo"
		},
                {
                        "id": 4,
                        "diaSemana": "terça",
                        "musculoTrabalhado": "Peito",
                        "nomeExercicio": "Supino Reto",
                        "series": 3,
                        "kg": 50,
                        "repeticao": 10,
                        "descanso": 60,
                        "unidadeDescanso": "",
                        "observacoes": "Mantenha a postura correta para evitar lesões."
                },
	],
	"atleta": 1,
	"personal": 3
}
```

<h3 id="get-cardapio-atleta">GET /atleta/cardapio</h3>

**RESPONSE**

```json
{
	"id": 2,
	"nome": "Cardápio",
	"refeicoes": [
		{
			"id": 3,
			"nome": "Pão com ovo",
			"diaSemana": "segunda",
			"tipoRefeicao": "lancheManha",
			"ingredientes": [
                                {
					"id": 3,
					"nome": "ovo",
					"quantidade": "1 unidade"
				},
				{
					"id": 4,
					"nome": "pão brioche",
					"quantidade": "1 unidade"
				},
                        ]
		}
	],
	"atleta": 1,
	"nutricionista": 8
}
```

<h2 id="colab">🤝 Collaborators</h2>

Participantes do Projeto

<table>
  <tr>
    <td align="center">
      <a href="#">
        <img src="https://avatars.githubusercontent.com/u/88459973?v=4" width="100px;" alt="Jardiel Carlos Profile Picture"/><br>
        <sub>
          <b>Jardiel Carlos</b>
        </sub>
      </a>
    </td>
  </tr>
</table>

<h2 id="contribute">📫 Contribute</h2>

Para contribuir para este projeto, siga os passos abaixo:

1. `git clone https://github.com/JardielCarlos/API-Spring-Boot-JPA.git`
2. `git checkout -b feature/NAME`
3. Abra um Pull Request explicando o problema resolvido ou recurso realizado, se existir, anexe screenshot das modificações visuais e aguarde a revisão!

<h3>Documentações que podem ajudar</h3>

[📝 Como criar uma solicitação pull request](https://www.atlassian.com/br/git/tutorials/making-a-pull-request)
