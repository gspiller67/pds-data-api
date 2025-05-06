"""Add page_size column to pds_tables

Revision ID: fix_page_size_column
Revises: 930e876c9a5f
Create Date: 2024-03-19
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fix_page_size_column'
down_revision = '930e876c9a5f'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('pds_tables', sa.Column('page_size', sa.Integer(), nullable=True, server_default='1000'))

def downgrade():
    op.drop_column('pds_tables', 'page_size') 