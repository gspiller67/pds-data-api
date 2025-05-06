"""add_is_primary_key_to_table_columns

Revision ID: a983b14b9f72
Revises: 
Create Date: 2024-03-19 12:34:56.789012

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a983b14b9f72'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add is_primary_key column with default value False
    op.add_column('table_columns', sa.Column('is_primary_key', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    # Remove is_primary_key column
    op.drop_column('table_columns', 'is_primary_key')
