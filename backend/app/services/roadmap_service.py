from sqlalchemy.orm import Session, joinedload
from app.models import Roadmap, RoadmapNode, NodeConnection, NodeLevel


class RoadmapService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, creator_id: int | None = None) -> list[Roadmap]:
        query = self.db.query(Roadmap)
        if creator_id:
            query = query.filter(Roadmap.creator_id == creator_id)
        return query.order_by(Roadmap.created_at.desc()).all()

    def get_by_id(self, roadmap_id: int) -> Roadmap | None:
        return (
            self.db.query(Roadmap)
            .options(joinedload(Roadmap.nodes))
            .filter(Roadmap.id == roadmap_id)
            .first()
        )

    def get_with_connections(self, roadmap_id: int) -> Roadmap | None:
        return (
            self.db.query(Roadmap)
            .options(
                joinedload(Roadmap.nodes).joinedload(RoadmapNode.connections_from),
                joinedload(Roadmap.nodes).joinedload(RoadmapNode.connections_to)
            )
            .filter(Roadmap.id == roadmap_id)
            .first()
        )

    def create(
        self,
        title: str,
        creator_id: int,
        description: str | None = None,
        source_content: str | None = None
    ) -> Roadmap:
        roadmap = Roadmap(
            title=title,
            description=description,
            source_content=source_content,
            creator_id=creator_id
        )
        self.db.add(roadmap)
        self.db.commit()
        self.db.refresh(roadmap)
        return roadmap

    def update(self, roadmap_id: int, **kwargs) -> Roadmap | None:
        roadmap = self.get_by_id(roadmap_id)
        if not roadmap:
            return None
        for key, value in kwargs.items():
            if hasattr(roadmap, key):
                setattr(roadmap, key, value)
        self.db.commit()
        self.db.refresh(roadmap)
        return roadmap

    def delete(self, roadmap_id: int) -> bool:
        roadmap = self.get_by_id(roadmap_id)
        if not roadmap:
            return False
        self.db.delete(roadmap)
        self.db.commit()
        return True


class NodeService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_roadmap(self, roadmap_id: int) -> list[RoadmapNode]:
        return (
            self.db.query(RoadmapNode)
            .filter(RoadmapNode.roadmap_id == roadmap_id)
            .order_by(RoadmapNode.order_index)
            .all()
        )

    def get_by_id(self, node_id: int) -> RoadmapNode | None:
        return self.db.query(RoadmapNode).filter(RoadmapNode.id == node_id).first()

    def create(
        self,
        roadmap_id: int,
        title: str,
        level: NodeLevel = NodeLevel.BEGINNER,
        description: str | None = None,
        content: str | None = None,
        position_x: int = 0,
        position_y: int = 0,
        order_index: int = 0
    ) -> RoadmapNode:
        node = RoadmapNode(
            roadmap_id=roadmap_id,
            title=title,
            description=description,
            content=content,
            level=level,
            position_x=position_x,
            position_y=position_y,
            order_index=order_index
        )
        self.db.add(node)
        self.db.commit()
        self.db.refresh(node)
        return node

    def update(self, node_id: int, **kwargs) -> RoadmapNode | None:
        node = self.get_by_id(node_id)
        if not node:
            return None
        for key, value in kwargs.items():
            if hasattr(node, key):
                setattr(node, key, value)
        self.db.commit()
        self.db.refresh(node)
        return node

    def delete(self, node_id: int) -> bool:
        node = self.get_by_id(node_id)
        if not node:
            return False
        self.db.delete(node)
        self.db.commit()
        return True

    def create_connection(self, from_node_id: int, to_node_id: int) -> NodeConnection:
        connection = NodeConnection(from_node_id=from_node_id, to_node_id=to_node_id)
        self.db.add(connection)
        self.db.commit()
        self.db.refresh(connection)
        return connection

    def delete_connection(self, connection_id: int) -> bool:
        connection = self.db.query(NodeConnection).filter(NodeConnection.id == connection_id).first()
        if not connection:
            return False
        self.db.delete(connection)
        self.db.commit()
        return True

    def get_connections(self, roadmap_id: int) -> list[NodeConnection]:
        return (
            self.db.query(NodeConnection)
            .join(RoadmapNode, NodeConnection.from_node_id == RoadmapNode.id)
            .filter(RoadmapNode.roadmap_id == roadmap_id)
            .all()
        )
