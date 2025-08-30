# backend/models/catalog.py
from __future__ import annotations
from typing import List, Optional
from sqlalchemy import Integer, String, Text, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

class Chapter(TimestampMixin, Base):
    __tablename__ = "chapters"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    groups: Mapped[List["Group"]] = relationship(
        back_populates="chapter",
        cascade="all, delete-orphan",
        order_by="Group.order_index",
    )

class Group(TimestampMixin, Base):
    __tablename__ = "groups"
    __table_args__ = (
        UniqueConstraint("chapter_id", "title", name="uq_group_chapter_title"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chapter_id: Mapped[int] = mapped_column(
        ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    chapter: Mapped["Chapter"] = relationship(back_populates="groups")
    problems: Mapped[List["Problem"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
        order_by="Problem.order_index",
    )

class Problem(TimestampMixin, Base):
    __tablename__ = "problems"
    __table_args__ = (
        Index("ix_problem_external", "source", "external_id"),
        UniqueConstraint("source", "external_id", name="uq_problem_source_external"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(32))          # ex) 'boj','programmers'
    external_id: Mapped[Optional[str]] = mapped_column(String(64))     # 사이트별 문제 id
    url: Mapped[Optional[str]] = mapped_column(Text)
    level: Mapped[Optional[int]] = mapped_column(Integer)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tags: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), default=list)

    group: Mapped["Group"] = relationship(back_populates="problems")
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
    alias_type: Mapped[Optional[str]] = mapped_column(String(32))  # ex) 'boj_id','short'
    problem: Mapped["Problem"] = relationship(back_populates="aliases")
