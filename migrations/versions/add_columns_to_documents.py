# File: lexforge-backend/migrations/versions/add_columns_to_documents.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY

# revision identifiers, used by Alembic
revision = '6a2e4b7c9f2a'
down_revision = 'f569ee4ffca8'  # Replace with the previous revision ID if known
branch_labels = None
depends_on = None

def upgrade():
    # Adding embedding, citation, and jurisdiction columns to documents table
    op.add_column("documents", sa.Column("embedding", ARRAY(sa.Float), nullable=True))
    op.add_column("documents", sa.Column("citation", sa.String, nullable=True))
    op.add_column("documents", sa.Column("jurisdiction", sa.String, nullable=True))

def downgrade():
    # Removing added columns in case of rollback
    op.drop_column("documents", "embedding")
    op.drop_column("documents", "citation")
    op.drop_column("documents", "jurisdiction")