"""add usuario

Revision ID: 9fd7c43ff846
Revises: 
Create Date: 2023-09-19 08:28:22.320956

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9fd7c43ff846'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tb_usuario',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nome', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('senha', sa.String(), nullable=False),
    sa.Column('tipo', sa.String(), nullable=False),
    sa.Column('massaMagra', sa.Float(), nullable=True),
    sa.Column('massaGorda', sa.Float(), nullable=True),
    sa.Column('altura', sa.Float(), nullable=True),
    sa.Column('peso', sa.Float(), nullable=True),
    sa.Column('imc', sa.Float(), nullable=True),
    sa.Column('statusPagamento', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tb_usuario')
    # ### end Alembic commands ###
