"""allow role and page delete cascade

Revision ID: d66bbab4e88d
Revises: af8b14d3014d
Create Date: 2025-04-15 20:29:00.163536
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd66bbab4e88d'
down_revision = 'af8b14d3014d'
branch_labels = None
depends_on = None


def upgrade():
    # Drop and recreate association table with named constraints
    op.drop_table("application_role_application_rule")

    op.create_table(
        "application_role_application_rule",
        sa.Column("application_role_id", sa.Integer(), sa.ForeignKey("application_role.id", ondelete="CASCADE", name="fk_role_rule")),
        sa.Column("application_rule_id", sa.Integer(), sa.ForeignKey("application_rule.id", ondelete="CASCADE", name="fk_rule_role"))
    )

    # Modify page_id column in application_rule table
    with op.batch_alter_table('application_rule', schema=None) as batch_op:
        batch_op.alter_column('page_id',
            existing_type=sa.INTEGER(),
            nullable=True)
        batch_op.create_foreign_key("fk_rule_page", 'application_page', ['page_id'], ['id'], ondelete='SET NULL')



def downgrade():
    # Revert changes to application_rule table
    with op.batch_alter_table('application_rule', schema=None) as batch_op:
        batch_op.drop_constraint("fk_rule_page", type_='foreignkey')
        batch_op.create_foreign_key(None, 'application_page', ['page_id'], ['id'])
        batch_op.alter_column('page_id',
            existing_type=sa.INTEGER(),
            nullable=False)

    op.drop_table("application_role_application_rule")

    op.create_table(
        "application_role_application_rule",
        sa.Column("application_role_id", sa.Integer(), sa.ForeignKey("application_role.id")),
        sa.Column("application_rule_id", sa.Integer(), sa.ForeignKey("application_rule.id"))
    )
