"""Add title column to PDSTABLES

Revision ID: add_title_to_pdstables
Revises: a2a1ae1a3ac1
Create Date: 2025-04-25
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_title_to_pdstables'
down_revision = 'a2a1ae1a3ac1'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('PDSTABLES', sa.Column('title', sa.String(length=256), nullable=True))

def downgrade():
    op.drop_column('PDSTABLES', 'title') 