"""Small, idempotent tenant-data migration for deployments without Alembic."""

from collections import defaultdict

from sqlalchemy import text, update
from sqlmodel import Session, select

from .models import Form, Organization, User


def normalize_organization_name(name: str) -> str:
    """Return the single canonical representation used as the tenant key."""
    return name.strip().casefold()


def normalize_tenants(session: Session) -> None:
    """Merge legacy duplicate tenants and enforce normalized-name uniqueness.

    Duplicate organizations created by older versions are merged into a stable
    canonical record. Users and forms are reassigned before the duplicate row
    is removed, preserving all tenant-owned data.
    """
    organizations = session.exec(select(Organization)).all()
    groups: dict[str, list[Organization]] = defaultdict(list)

    for organization in organizations:
        normalized_name = normalize_organization_name(organization.name)
        if not normalized_name:
            raise RuntimeError(f"Organization {organization.id} has an empty name")
        groups[normalized_name].append(organization)

    for normalized_name, organizations_with_name in groups.items():
        # UUID ordering is deterministic, so repeated starts select the same
        # canonical tenant until all legacy duplicates are gone.
        canonical = min(organizations_with_name, key=lambda organization: str(organization.id))
        canonical.name = normalized_name

        for duplicate in organizations_with_name:
            if duplicate.id == canonical.id:
                continue

            session.exec(
                update(User)
                .where(User.organization_id == duplicate.id)
                .values(organization_id=canonical.id)
            )
            session.exec(
                update(Form)
                .where(Form.organization_id == duplicate.id)
                .values(organization_id=canonical.id)
            )
            session.delete(duplicate)

    session.commit()

    # SQLModel's create_all does not alter existing tables. These two columns
    # record ownership for forms and per-user response limits.
    session.exec(
        text(
            'ALTER TABLE form ADD COLUMN IF NOT EXISTS created_by_user_id '
            'UUID REFERENCES "user"(id)'
        )
    )
    session.exec(
        text(
            'ALTER TABLE formsubmission ADD COLUMN IF NOT EXISTS submitted_by_user_id '
            'UUID REFERENCES "user"(id)'
        )
    )
    session.exec(
        text(
            'CREATE UNIQUE INDEX IF NOT EXISTS uq_formsubmission_user '
            'ON formsubmission (form_id, submitted_by_user_id) '
            'WHERE submitted_by_user_id IS NOT NULL'
        )
    )

    # Old forms have no creator history. Assign an owner only when the tenant
    # has exactly one user; multi-user legacy forms remain unassigned rather
    # than granting response access to the wrong person.
    session.exec(
        text(
            'UPDATE form AS f SET created_by_user_id = u.id '
            'FROM "user" AS u '
            'WHERE f.created_by_user_id IS NULL '
            'AND u.organization_id = f.organization_id '
            'AND NOT EXISTS ('
            'SELECT 1 FROM "user" AS other '
            'WHERE other.organization_id = f.organization_id AND other.id <> u.id'
            ')'
        )
    )
    session.commit()

    session.exec(text("ALTER TABLE \"user\" ADD COLUMN IF NOT EXISTS role VARCHAR NOT NULL DEFAULT 'member'"))
    session.exec(text("ALTER TABLE fileattachment ADD COLUMN IF NOT EXISTS field_id VARCHAR"))
    # Preserve existing access by selecting one deterministic owner per tenant.
    session.exec(
        text(
            'WITH ranked_users AS ('
            'SELECT id, row_number() OVER (PARTITION BY organization_id ORDER BY id) AS row_number '
            'FROM "user"'
            ') '
            'UPDATE "user" AS u SET role = \'owner\' '
            'FROM ranked_users AS r WHERE u.id = r.id AND r.row_number = 1 '
            'AND NOT EXISTS (SELECT 1 FROM "user" AS owner_user WHERE owner_user.organization_id = u.organization_id AND owner_user.role = \'owner\')'
        )
    )
    session.commit()

    # A functional unique index protects against casing/whitespace variants
    # even if data is written outside the API.
    session.exec(
        text(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_organization_normalized_name "
            "ON organization (lower(btrim(name)))"
        )
    )
    session.commit()
