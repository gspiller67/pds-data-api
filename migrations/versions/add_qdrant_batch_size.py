"""add qdrant_batch_size

Revision ID: add_qdrant_batch_size
Revises: add_title_to_pdstables
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_qdrant_batch_size'
down_revision = 'add_title_to_pdstables'
branch_labels = None
depends_on = None

def upgrade():
    # Add qdrant_batch_size column to PDSTABLES table
    op.add_column('PDSTABLES', sa.Column('qdrant_batch_size', sa.Integer(), nullable=True, server_default='100'))

def downgrade():
    # Remove qdrant_batch_size column from PDSTABLES table
    op.drop_column('PDSTABLES', 'qdrant_batch_size') 