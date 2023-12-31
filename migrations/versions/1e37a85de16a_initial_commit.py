"""Initial Commit

Revision ID: 1e37a85de16a
Revises: 
Create Date: 2023-12-05 12:11:40.347521

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e37a85de16a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tb_blacklist',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(), nullable=False),
    sa.Column('exp', sa.TIMESTAMP(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tb_produtos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_ProductStripe', sa.String(), nullable=True),
    sa.Column('nome', sa.String(), nullable=False),
    sa.Column('descricao', sa.String(), nullable=False),
    sa.Column('ativo', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tb_usuario',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nome', sa.String(), nullable=False),
    sa.Column('sobrenome', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('senha', sa.String(), nullable=False),
    sa.Column('cpf', sa.String(), nullable=False),
    sa.Column('tipo', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('cpf'),
    sa.UniqueConstraint('email')
    )
    op.create_table('tb_administrador',
    sa.Column('usuario_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['usuario_id'], ['tb_usuario.id'], ),
    sa.PrimaryKeyConstraint('usuario_id')
    )
    op.create_table('tb_imgUsuarios',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fotoPerfil', sa.LargeBinary(), nullable=True),
    sa.Column('usuario_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['usuario_id'], ['tb_usuario.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tb_nutricionista',
    sa.Column('usuario_id', sa.Integer(), nullable=False),
    sa.Column('crn', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['usuario_id'], ['tb_usuario.id'], ),
    sa.PrimaryKeyConstraint('usuario_id'),
    sa.UniqueConstraint('crn')
    )
    op.create_table('tb_personalTrainer',
    sa.Column('usuario_id', sa.Integer(), nullable=False),
    sa.Column('cref', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['usuario_id'], ['tb_usuario.id'], ),
    sa.PrimaryKeyConstraint('usuario_id'),
    sa.UniqueConstraint('cref')
    )
    op.create_table('tb_planos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_PlanoStripe', sa.String(), nullable=True),
    sa.Column('nome', sa.String(), nullable=False),
    sa.Column('valor', sa.Float(), nullable=False),
    sa.Column('intervalo', sa.Enum('day', 'week', 'month', 'year', name='intervalo_plano'), nullable=False),
    sa.Column('ativo', sa.Boolean(), nullable=False),
    sa.Column('produto_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['produto_id'], ['tb_produtos.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tb_atleta',
    sa.Column('usuario_id', sa.Integer(), nullable=False),
    sa.Column('stripe_id', sa.String(), nullable=True),
    sa.Column('massaMagra', sa.Float(), nullable=True),
    sa.Column('massaGorda', sa.Float(), nullable=True),
    sa.Column('altura', sa.Float(), nullable=True),
    sa.Column('peso', sa.Float(), nullable=True),
    sa.Column('imc', sa.Float(), nullable=True),
    sa.Column('statusImc', sa.String(), nullable=True),
    sa.Column('statusPagamento', sa.String(), nullable=False),
    sa.Column('personal_trainer_id', sa.Integer(), nullable=True),
    sa.Column('nutricionista_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['nutricionista_id'], ['tb_nutricionista.usuario_id'], ),
    sa.ForeignKeyConstraint(['personal_trainer_id'], ['tb_personalTrainer.usuario_id'], ),
    sa.ForeignKeyConstraint(['usuario_id'], ['tb_usuario.id'], ),
    sa.PrimaryKeyConstraint('usuario_id')
    )
    op.create_table('tb_assinaturas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_AssinaturaStripe', sa.String(), nullable=True),
    sa.Column('nome', sa.String(), nullable=False),
    sa.Column('intervalo', sa.Enum('day', 'week', 'month', 'year', name='intervalo_planoAssinatura'), nullable=False),
    sa.Column('valor', sa.Float(), nullable=False),
    sa.Column('data_inicio', sa.DateTime(), nullable=True),
    sa.Column('data_fim', sa.DateTime(), nullable=True),
    sa.Column('data_inicio_teste', sa.DateTime(), nullable=True),
    sa.Column('data_fim_teste', sa.DateTime(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('atleta_id', sa.Integer(), nullable=False),
    sa.Column('plano_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['atleta_id'], ['tb_atleta.usuario_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['plano_id'], ['tb_planos.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('atleta_id')
    )
    op.create_table('tb_cardapio',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nome', sa.String(), nullable=False),
    sa.Column('atleta', sa.Integer(), nullable=True),
    sa.Column('nutricionista', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['atleta'], ['tb_atleta.usuario_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['nutricionista'], ['tb_nutricionista.usuario_id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('atleta')
    )
    op.create_table('tb_cartaoCredito',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_cartaoCredito', sa.String(), nullable=False),
    sa.Column('nomeTitular', sa.String(), nullable=False),
    sa.Column('bandeira', sa.String(), nullable=False),
    sa.Column('mesVencimento', sa.String(), nullable=False),
    sa.Column('anoVencimento', sa.String(), nullable=False),
    sa.Column('finalCartao', sa.String(), nullable=False),
    sa.Column('pagamentoPadrao', sa.String(), nullable=True),
    sa.Column('atleta_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['atleta_id'], ['tb_atleta.usuario_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tb_notificacaoNutricionista',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nome', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('mensagem', sa.String(), nullable=False),
    sa.Column('solicitacao', sa.Boolean(), nullable=False),
    sa.Column('atleta_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['atleta_id'], ['tb_atleta.usuario_id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('atleta_id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('tb_notificacaoPersonal',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nome', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('mensagem', sa.String(), nullable=False),
    sa.Column('solicitacao', sa.Boolean(), nullable=False),
    sa.Column('atleta_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['atleta_id'], ['tb_atleta.usuario_id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('atleta_id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('tb_tabelaTreino',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('semanaInicio', sa.Date(), nullable=False),
    sa.Column('semanaFim', sa.Date(), nullable=False),
    sa.Column('atleta', sa.Integer(), nullable=True),
    sa.Column('personal', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['atleta'], ['tb_atleta.usuario_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['personal'], ['tb_personalTrainer.usuario_id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('atleta')
    )
    op.create_table('nutricionista_rejeitado',
    sa.Column('notificacao_id', sa.Integer(), nullable=True),
    sa.Column('nutricionista_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['notificacao_id'], ['tb_notificacaoNutricionista.id'], ),
    sa.ForeignKeyConstraint(['nutricionista_id'], ['tb_nutricionista.usuario_id'], )
    )
    op.create_table('personal_rejeitado',
    sa.Column('notificacao_id', sa.Integer(), nullable=True),
    sa.Column('personal_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['notificacao_id'], ['tb_notificacaoPersonal.id'], ),
    sa.ForeignKeyConstraint(['personal_id'], ['tb_personalTrainer.usuario_id'], )
    )
    op.create_table('tb_exercicioAtleta',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('diaSemana', sa.Enum('segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sabado', name='dia_da_semana_exercicio'), nullable=False),
    sa.Column('musculoTrabalhado', sa.String(), nullable=False),
    sa.Column('nomeExercicio', sa.String(), nullable=False),
    sa.Column('series', sa.Integer(), nullable=False),
    sa.Column('kg', sa.Integer(), nullable=False),
    sa.Column('repeticao', sa.Integer(), nullable=False),
    sa.Column('descanso', sa.Integer(), nullable=False),
    sa.Column('unidadeDescanso', sa.String(), nullable=False),
    sa.Column('observacoes', sa.String(), nullable=True),
    sa.Column('tabelaTreino', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['tabelaTreino'], ['tb_tabelaTreino.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tb_refeicao',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nome', sa.String(), nullable=False),
    sa.Column('diaSemana', sa.Enum('segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo', name='dia_da_semana'), nullable=False),
    sa.Column('tipoRefeicao', sa.Enum('cafeManha', 'lancheManha', 'almoco', 'lancheTarde', 'janta', 'lancheNoite', name='tipo_refeicao'), nullable=False),
    sa.Column('cardapio', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['cardapio'], ['tb_cardapio.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('diaSemana', 'tipoRefeicao', 'cardapio', name='unique_refeicao_por_dia')
    )
    op.create_table('tb_ingrediente',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nome', sa.String(), nullable=False),
    sa.Column('quantidade', sa.String(), nullable=False),
    sa.Column('refeicao', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['refeicao'], ['tb_refeicao.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tb_ingrediente')
    op.drop_table('tb_refeicao')
    op.drop_table('tb_exercicioAtleta')
    op.drop_table('personal_rejeitado')
    op.drop_table('nutricionista_rejeitado')
    op.drop_table('tb_tabelaTreino')
    op.drop_table('tb_notificacaoPersonal')
    op.drop_table('tb_notificacaoNutricionista')
    op.drop_table('tb_cartaoCredito')
    op.drop_table('tb_cardapio')
    op.drop_table('tb_assinaturas')
    op.drop_table('tb_atleta')
    op.drop_table('tb_planos')
    op.drop_table('tb_personalTrainer')
    op.drop_table('tb_nutricionista')
    op.drop_table('tb_imgUsuarios')
    op.drop_table('tb_administrador')
    op.drop_table('tb_usuario')
    op.drop_table('tb_produtos')
    op.drop_table('tb_blacklist')
    # ### end Alembic commands ###
