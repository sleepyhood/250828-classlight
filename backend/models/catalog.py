# backend/models/catalog.py
from __future__ import annotations
import datetime as dt
from typing import Any, Dict, List, Optional
from sqlalchemy import Integer, String, Text, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin


class Chapter(TimestampMixin, Base):
    __tablename__ = "chapters"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    groups: Mapped[List["Group"]] = relationship(back_populates="chapter")


class Group(TimestampMixin, Base):
    __tablename__ = "groups"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chapter_id: Mapped[int | None] = mapped_column(ForeignKey("chapters.id"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    chapter: Mapped[Chapter | None] = relationship(back_populates="groups")
    problems: Mapped[List["Problem"]] = relationship(back_populates="group")


class Problem(TimestampMixin, Base):
    __tablename__ = "problems"
    __table_args__ = (
        UniqueConstraint("site", "server_problem_id", name="uq_problem_site_server_id"),
        Index("ix_problems_tags", "tags", postgresql_using="gin"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site: Mapped[str] = mapped_column(String(50), default="doingcoding", nullable=False)
    server_problem_id: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    difficulty: Mapped[Optional[str]] = mapped_column(String(32))
    total_score: Mapped[Optional[int]] = mapped_column(Integer)
    tags: Mapped[List[str]] = mapped_column(
        ARRAY(String(50)), default=list, nullable=False
    )
    chapter_id: Mapped[int | None] = mapped_column(ForeignKey("chapters.id"))
    group_id: Mapped[int | None] = mapped_column(ForeignKey("groups.id"))
    meta: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    chapter: Mapped[Chapter | None] = relationship()
    group: Mapped[Group | None] = relationship(back_populates="problems")
    aliases: Mapped[List["ProblemAlias"]] = relationship(
        back_populates="problem", cascade="all, delete-orphan"
    )


class ProblemAlias(TimestampMixin, Base):
    __tablename__ = "problem_aliases"
    __table_args__ = (
        UniqueConstraint("problem_id", "alias", name="uq_problem_alias"),
        Index("ix_problem_alias_alias", "alias"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    problem_id: Mapped[int] = mapped_column(
        ForeignKey("problems.id", ondelete="CASCADE"), nullable=False
    )
    alias: Mapped[str] = mapped_column(String(128), nullable=False)
    alias_type: Mapped[Optional[str]] = mapped_column(String(32))
    problem: Mapped[Problem] = relationship(back_populates="aliases")
