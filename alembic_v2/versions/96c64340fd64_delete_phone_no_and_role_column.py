"""delete phone.no and role column

Revision ID: 96c64340fd64
Revises: 
Create Date: 2024-06-10 14:22:16.615335

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96c64340fd64'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('users', 'phone_number')
    op.drop_column('users', 'role')
    pass


def downgrade() -> None:
    pass
