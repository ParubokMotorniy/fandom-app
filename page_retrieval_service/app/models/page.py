"""SQLAlchemy models"""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    """Base class for SQLAlchemy models"""
    pass

class Page(Base):
    """Page model"""
    __tablename__ = "pages"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    # author_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    # image_url: Mapped[str] = mapped_column(String, nullable=True)

    def __repr__(self):
        return f"<Page(id={self.id}, title={self.title})>"