"""empty message

Revision ID: 292e2af96407
Revises: e9984505b6f2
Create Date: 2023-11-10 17:01:20.368689

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '292e2af96407'
down_revision = 'e9984505b6f2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tb_tabelaTreino', schema=None) as batch_op:
        batch_op.drop_constraint('tb_tabelaTreino_atleta_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'tb_atleta', ['atleta'], ['usuario_id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tb_tabelaTreino', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('tb_tabelaTreino_atleta_fkey', 'tb_atleta', ['atleta'], ['usuario_id'])

    # ### end Alembic commands ###