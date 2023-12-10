"""Added Posts db

Revision ID: 5a1f97365860
Revises: 1b042d8ac453
Create Date: 2023-11-29 09:25:04.841693

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '5a1f97365860'
down_revision = '1b042d8ac453'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.alter_column('content',
               existing_type=mysql.TEXT(),
               type_=sa.String(length=1000),
               existing_nullable=False)

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('color',
               existing_type=mysql.VARCHAR(length=100),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('color',
               existing_type=mysql.VARCHAR(length=100),
               nullable=True)

    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.alter_column('content',
               existing_type=sa.String(length=1000),
               type_=mysql.TEXT(),
               existing_nullable=False)

    # ### end Alembic commands ###
