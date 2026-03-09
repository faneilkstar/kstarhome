"""Ajout classes assemblees et extension LF LP
Revision ID: f7f39b3674b8
Revises: 
Create Date: 2026-03-03 21:30:38.616391
"""
from alembic import op
import sqlalchemy as sa
revision = 'f7f39b3674b8'
down_revision = None
branch_labels = None
depends_on = None
def upgrade():
    with op.batch_alter_table('classes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('est_assemblee', sa.Boolean(), nullable=True, server_default='false'))
        batch_op.add_column(sa.Column('departement_source_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('type_diplome_assemblee', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('semestres_assemblee', sa.String(length=20), nullable=True))
        batch_op.create_foreign_key('fk_classes_dept_source', 'departements', ['departement_source_id'], ['id'])
def downgrade():
    with op.batch_alter_table('classes', schema=None) as batch_op:
        batch_op.drop_constraint('fk_classes_dept_source', type_='foreignkey')
        batch_op.drop_column('semestres_assemblee')
        batch_op.drop_column('type_diplome_assemblee')
        batch_op.drop_column('departement_source_id')
        batch_op.drop_column('est_assemblee')
