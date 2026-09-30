"""Add revocable user sessions and single-use password reset tokens.

Revision ID: 0002_auth_sessions
Revises: 0001_initial_schema
Create Date: 2026-09-30
"""

from alembic import op

revision = "0002_auth_sessions"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def _execute_statements(script: str) -> None:
    for statement in script.split(";"):
        if statement.strip():
            op.execute(statement)


def upgrade() -> None:
    _execute_statements("""
    CREATE TABLE user_sessions (
        id UUID PRIMARY KEY,
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
        token_hash VARCHAR(64) NOT NULL UNIQUE,
        csrf_token_hash VARCHAR(64) NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        expires_at TIMESTAMPTZ NOT NULL,
        revoked_at TIMESTAMPTZ,
        last_used_at TIMESTAMPTZ
    );
    CREATE INDEX ix_user_sessions_user_expires ON user_sessions(user_id, expires_at);
    CREATE TABLE password_reset_tokens (
        id UUID PRIMARY KEY,
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
        token_hash VARCHAR(64) NOT NULL UNIQUE,
        purpose VARCHAR(24) NOT NULL DEFAULT 'password_reset',
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        expires_at TIMESTAMPTZ NOT NULL,
        used_at TIMESTAMPTZ
    );
    CREATE INDEX ix_password_reset_tokens_user_expires
        ON password_reset_tokens(user_id, expires_at);
    """)


def downgrade() -> None:
    _execute_statements("""
    DROP TABLE password_reset_tokens;
    DROP TABLE user_sessions;
    """)
