"""empty message

Revision ID: 1e0500509c70
Revises: fbaeab06ab51
Create Date: 2023-10-16 11:43:43.209653

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e0500509c70'
down_revision = 'fbaeab06ab51'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tb_atleta', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nutricionista_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'tb_nutricionista', ['nutricionista_id'], ['usuario_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tb_atleta', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('nutricionista_id')

    # ### end Alembic commands ###
