"""empty message

Revision ID: 444a17ed83c4
Revises: a4516a05b670
Create Date: 2025-04-09 22:58:29.483151

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '444a17ed83c4'
down_revision = 'a4516a05b670'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('userupload', schema=None) as batch_op:
        batch_op.drop_index('ix_userupload_upload_amt')
        batch_op.drop_index('ix_userupload_upload_desc')
        batch_op.drop_index('ix_userupload_upload_filename')

    op.drop_table('userupload')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('userupload',
    sa.Column('upload_id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('upload_filename', mysql.VARCHAR(length=200), nullable=False),
    sa.Column('upload_desc', mysql.VARCHAR(length=500), nullable=False),
    sa.Column('upload_amt', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('upload_date', mysql.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('upload_id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    with op.batch_alter_table('userupload', schema=None) as batch_op:
        batch_op.create_index('ix_userupload_upload_filename', ['upload_filename'], unique=False)
        batch_op.create_index('ix_userupload_upload_desc', ['upload_desc'], unique=False)
        batch_op.create_index('ix_userupload_upload_amt', ['upload_amt'], unique=False)

    # ### end Alembic commands ###
