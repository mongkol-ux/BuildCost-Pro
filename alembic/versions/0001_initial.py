from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    user_role = sa.Enum("ADMIN", "MANAGER", "USER", name="userrole")
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        user_role.create(bind, checkfirst=True)
    else:
        user_role = sa.Enum("ADMIN", "MANAGER", "USER", name="userrole", native_enum=False)

    op.create_table("users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_table("projects",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("owner_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_projects_name", "projects", ["name"])
    op.create_index("ix_projects_code", "projects", ["code"])
    op.create_index("ix_projects_owner_id", "projects", ["owner_id"])
    for table, extra in [("costs", [sa.Column("category", sa.String(100), nullable=False)]), ("budgets", []), ("transactions", [sa.Column("reference", sa.String(100), nullable=False)])]:
        columns = [sa.Column("id", sa.String(36), primary_key=True), sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)] + extra + [sa.Column("description", sa.String(500), nullable=False), sa.Column("amount", sa.Numeric(14,2), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False)]
        if table == "budgets":
            columns.insert(2, sa.Column("name", sa.String(200), nullable=False))
        op.create_table(table, *columns)
        op.create_index(f"ix_{table}_project_id", table, ["project_id"])
    op.create_index("ix_transactions_reference", "transactions", ["reference"])


def downgrade():
    op.drop_index("ix_transactions_reference", table_name="transactions")
    for table in ("transactions", "budgets", "costs"):
        op.drop_index(f"ix_{table}_project_id", table_name=table)
        op.drop_table(table)
    for idx in ("ix_projects_owner_id", "ix_projects_code", "ix_projects_name"):
        op.drop_index(idx, table_name="projects")
    op.drop_table("projects")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    if op.get_bind().dialect.name == "postgresql":
        sa.Enum(name="userrole").drop(op.get_bind(), checkfirst=True)
