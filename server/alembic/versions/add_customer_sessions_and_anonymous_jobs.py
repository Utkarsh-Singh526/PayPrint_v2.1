
"""Add customer sessions and anonymous print job support."""

from alembic import op
import sqlalchemy as sa


revision = "a21c0001cust"
down_revision = "6969223db037"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customer_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("kiosk_id", sa.Integer(), nullable=False),
        sa.Column("customer_name", sa.String(100), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            server_default="ACTIVE",
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["kiosk_id"], ["kiosks.id"]),
        sa.UniqueConstraint("token_hash"),
    )

    op.create_index(
        "ix_customer_sessions_id",
        "customer_sessions",
        ["id"],
    )
    op.create_index(
        "ix_customer_sessions_kiosk_id",
        "customer_sessions",
        ["kiosk_id"],
    )
    op.create_index(
        "ix_customer_sessions_token_hash",
        "customer_sessions",
        ["token_hash"],
    )

    # Keep existing users/jobs intact; allow new anonymous records.
    op.alter_column(
        "documents",
        "user_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.alter_column(
        "print_jobs",
        "user_id",
        existing_type=sa.Integer(),
        nullable=True,
    )

    op.add_column(
        "documents",
        sa.Column(
            "customer_session_id",
            sa.Integer(),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_documents_customer_session",
        "documents",
        "customer_sessions",
        ["customer_session_id"],
        ["id"],
    )

    op.add_column(
        "print_jobs",
        sa.Column(
            "customer_session_id",
            sa.Integer(),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_print_jobs_customer_session",
        "print_jobs",
        "customer_sessions",
        ["customer_session_id"],
        ["id"],
    )

    op.add_column(
        "print_jobs",
        sa.Column(
            "tracking_code",
            sa.String(20),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_print_jobs_tracking_code",
        "print_jobs",
        ["tracking_code"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_print_jobs_tracking_code",
        table_name="print_jobs",
    )
    op.drop_column("print_jobs", "tracking_code")

    op.drop_constraint(
        "fk_print_jobs_customer_session",
        "print_jobs",
        type_="foreignkey",
    )
    op.drop_column("print_jobs", "customer_session_id")

    op.drop_constraint(
        "fk_documents_customer_session",
        "documents",
        type_="foreignkey",
    )
    op.drop_column("documents", "customer_session_id")

    op.alter_column(
        "print_jobs",
        "user_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.alter_column(
        "documents",
        "user_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.drop_index(
        "ix_customer_sessions_token_hash",
        table_name="customer_sessions",
    )
    op.drop_index(
        "ix_customer_sessions_kiosk_id",
        table_name="customer_sessions",
    )
    op.drop_index(
        "ix_customer_sessions_id",
        table_name="customer_sessions",
    )
    op.drop_table("customer_sessions")
