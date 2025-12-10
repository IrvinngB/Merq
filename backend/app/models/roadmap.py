from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class NodeLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    source_content = Column(Text)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    creator = relationship("User", back_populates="roadmaps")
    nodes = relationship("RoadmapNode", back_populates="roadmap", cascade="all, delete-orphan")


class RoadmapNode(Base):
    __tablename__ = "roadmap_nodes"

    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    content = Column(Text)
    level = Column(SQLEnum(NodeLevel), default=NodeLevel.BEGINNER)
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    order_index = Column(Integer, default=0)

    roadmap = relationship("Roadmap", back_populates="nodes")
    connections_from = relationship(
        "NodeConnection",
        foreign_keys="NodeConnection.from_node_id",
        back_populates="from_node",
        cascade="all, delete-orphan"
    )
    connections_to = relationship(
        "NodeConnection",
        foreign_keys="NodeConnection.to_node_id",
        back_populates="to_node",
        cascade="all, delete-orphan"
    )


class NodeConnection(Base):
    __tablename__ = "node_connections"

    id = Column(Integer, primary_key=True, index=True)
    from_node_id = Column(Integer, ForeignKey("roadmap_nodes.id", ondelete="CASCADE"), nullable=False)
    to_node_id = Column(Integer, ForeignKey("roadmap_nodes.id", ondelete="CASCADE"), nullable=False)

    from_node = relationship("RoadmapNode", foreign_keys=[from_node_id], back_populates="connections_from")
    to_node = relationship("RoadmapNode", foreign_keys=[to_node_id], back_populates="connections_to")
