from uuid import UUID, uuid4
from datetime import datetime, UTC

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.domain.expense import model as expense_model
from src.domain.user import model as user_model


class Base(DeclarativeBase):
    pass


class OrganizationORM(Base):
    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255))
    created: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
    last_modified: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )
    expenses: Mapped[list["ExpenseORM"]] = relationship(back_populates="organization")
    users: Mapped[list["UserORM"]] = relationship(back_populates="organization")


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    role: Mapped[user_model.UserRole] = mapped_column(SQLEnum(user_model.UserRole))
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"))
    organization: Mapped[OrganizationORM] = relationship(back_populates="users")
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    last_modified: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


class ExpenseORM(Base):
    __tablename__ = "expenses"
    id: Mapped[UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    submitter_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id")
    )  # Using ID to prevent context leak between domains
    approved_by_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    # Relationships for ORM efficiency
    submitter: Mapped[UserORM] = relationship(foreign_keys=[submitter_id])
    approver: Mapped[UserORM | None] = relationship(foreign_keys=[approved_by_id])

    title: Mapped[str] = mapped_column(String(255))
    amount: Mapped[float] = mapped_column(Float)
    date: Mapped[datetime] = mapped_column(DateTime)
    category: Mapped[expense_model.ExpenseCategory] = mapped_column(
        SQLEnum(expense_model.ExpenseCategory)
    )
    state: Mapped[expense_model.ExpenseState] = mapped_column(
        SQLEnum(expense_model.ExpenseState)
    )
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"))
    organization: Mapped[OrganizationORM] = relationship(back_populates="expenses")
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    last_modified: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    def to_domain(self) -> expense_model.Expense:
        """Convert ORM model to domain model."""
        return expense_model.Expense(
            id=self.id,
            submitter_id=str(self.submitter_id),
            title=self.title,
            amount=self.amount,
            date=self.date,
            category=self.category,
            state=self.state,
            organization=expense_model.Organization(
                id=self.organization_id, name=self.organization.name
            ),
            approved_by_id=str(self.approved_by_id) if self.approved_by_id else None,
        )

    @classmethod
    def from_domain(cls, expense: expense_model.Expense) -> "ExpenseORM":
        return cls(
            id=expense.id,
            submitter_id=UUID(expense.submitter_id),
            title=expense.title,
            amount=expense.amount,
            date=expense.date,
            category=expense.category,
            state=expense.state,
            organization_id=expense.organization.id,
            approved_by_id=UUID(expense.approved_by_id)
            if expense.approved_by_id
            else None,
        )
