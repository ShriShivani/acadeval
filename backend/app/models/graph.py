"""
Module 4 — Relational Graph ORM Models
======================================
Defines `GraphNode` and `GraphEdge` for persistent relational graph storage.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class GraphNode(Base):
    __tablename__ = "graph_nodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_type = Column(String(50), nullable=False, index=True)  # Project | Domain | Algorithm | Technology ...
    name = Column(String(300), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("node_type", "name", name="uq_graph_nodes_type_name"),
    )

    # Relationships
    outgoing_edges = relationship("GraphEdge", foreign_keys="[GraphEdge.from_node]", back_populates="source_node", cascade="all, delete-orphan")
    incoming_edges = relationship("GraphEdge", foreign_keys="[GraphEdge.to_node]", back_populates="target_node", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<GraphNode(id={self.id}, type={self.node_type!r}, name={self.name!r})>"


class GraphEdge(Base):
    __tablename__ = "graph_edges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_node = Column(Integer, ForeignKey("graph_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    to_node = Column(Integer, ForeignKey("graph_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    relationship = Column(String(50), nullable=False, index=True)  # HAS_DOMAIN | USES_ALGORITHM | ...
    confidence = Column(Numeric(5, 4), nullable=False, server_default="1.0000")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    source_node = relationship("GraphNode", foreign_keys=[from_node], back_populates="outgoing_edges")
    target_node = relationship("GraphNode", foreign_keys=[to_node], back_populates="incoming_edges")

    def __repr__(self):
        return f"<GraphEdge(from={self.from_node}, to={self.to_node}, rel={self.relationship!r})>"
