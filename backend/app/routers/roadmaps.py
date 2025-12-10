from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.services.roadmap_service import RoadmapService, NodeService
from app.models import NodeLevel

router = APIRouter(prefix="/roadmaps", tags=["roadmaps"])


class RoadmapCreate(BaseModel):
    title: str
    description: str | None = None


class RoadmapUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class NodeCreate(BaseModel):
    title: str
    description: str | None = None
    content: str | None = None
    level: NodeLevel = NodeLevel.BEGINNER
    position_x: int = 0
    position_y: int = 0
    order_index: int = 0
    is_completed: bool = False


class NodeUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    content: str | None = None
    level: NodeLevel | None = None
    position_x: int | None = None
    position_y: int | None = None
    order_index: int | None = None
    is_completed: bool | None = None


class ConnectionCreate(BaseModel):
    from_node_id: int
    to_node_id: int


class ConnectionResponse(BaseModel):
    id: int
    from_node_id: int
    to_node_id: int

    class Config:
        from_attributes = True


class NodeResponse(BaseModel):
    id: int
    roadmap_id: int
    title: str
    description: str | None
    content: str | None
    level: NodeLevel
    position_x: int
    position_y: int
    order_index: int
    is_completed: bool

    class Config:
        from_attributes = True


class RoadmapResponse(BaseModel):
    id: int
    title: str
    description: str | None
    creator_id: int

    class Config:
        from_attributes = True


class RoadmapDetailResponse(RoadmapResponse):
    nodes: list[NodeResponse] = []


@router.get("/", response_model=list[RoadmapResponse])
def get_roadmaps(creator_id: int | None = None, db: Session = Depends(get_db)):
    service = RoadmapService(db)
    return service.get_all(creator_id)


@router.get("/{roadmap_id}", response_model=RoadmapDetailResponse)
def get_roadmap(roadmap_id: int, db: Session = Depends(get_db)):
    service = RoadmapService(db)
    roadmap = service.get_with_connections(roadmap_id)
    if not roadmap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")
    return roadmap


@router.post("/", response_model=RoadmapResponse, status_code=status.HTTP_201_CREATED)
def create_roadmap(data: RoadmapCreate, creator_id: int, db: Session = Depends(get_db)):
    service = RoadmapService(db)
    return service.create(
        title=data.title,
        description=data.description,
        creator_id=creator_id
    )


@router.patch("/{roadmap_id}", response_model=RoadmapResponse)
def update_roadmap(roadmap_id: int, data: RoadmapUpdate, db: Session = Depends(get_db)):
    service = RoadmapService(db)
    update_data = data.model_dump(exclude_unset=True)
    roadmap = service.update(roadmap_id, **update_data)
    if not roadmap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")
    return roadmap


@router.delete("/{roadmap_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_roadmap(roadmap_id: int, db: Session = Depends(get_db)):
    service = RoadmapService(db)
    if not service.delete(roadmap_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")


# Node endpoints
node_router = APIRouter(prefix="/roadmaps/{roadmap_id}/nodes", tags=["nodes"])


@node_router.get("/", response_model=list[NodeResponse])
def get_nodes(roadmap_id: int, db: Session = Depends(get_db)):
    service = NodeService(db)
    return service.get_by_roadmap(roadmap_id)


@node_router.get("/{node_id}", response_model=NodeResponse)
def get_node(roadmap_id: int, node_id: int, db: Session = Depends(get_db)):
    service = NodeService(db)
    node = service.get_by_id(node_id)
    if not node or node.roadmap_id != roadmap_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")
    return node


@node_router.post("/", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
def create_node(roadmap_id: int, data: NodeCreate, db: Session = Depends(get_db)):
    roadmap_service = RoadmapService(db)
    if not roadmap_service.get_by_id(roadmap_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")
    
    service = NodeService(db)
    return service.create(
        roadmap_id=roadmap_id,
        title=data.title,
        description=data.description,
        content=data.content,
        level=data.level,
        position_x=data.position_x,
        position_y=data.position_y,
        order_index=data.order_index
    )


@node_router.patch("/{node_id}", response_model=NodeResponse)
def update_node(roadmap_id: int, node_id: int, data: NodeUpdate, db: Session = Depends(get_db)):
    service = NodeService(db)
    node = service.get_by_id(node_id)
    if not node or node.roadmap_id != roadmap_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")
    
    update_data = data.model_dump(exclude_unset=True)
    return service.update(node_id, **update_data)


@node_router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_node(roadmap_id: int, node_id: int, db: Session = Depends(get_db)):
    service = NodeService(db)
    node = service.get_by_id(node_id)
    if not node or node.roadmap_id != roadmap_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")
    service.delete(node_id)


# Connection endpoints
@router.get("/{roadmap_id}/connections", response_model=list[ConnectionResponse])
def get_connections(roadmap_id: int, db: Session = Depends(get_db)):
    service = NodeService(db)
    return service.get_connections(roadmap_id)


@router.post("/{roadmap_id}/connections", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
def create_connection(roadmap_id: int, data: ConnectionCreate, db: Session = Depends(get_db)):
    service = NodeService(db)
    from_node = service.get_by_id(data.from_node_id)
    to_node = service.get_by_id(data.to_node_id)
    
    if not from_node or from_node.roadmap_id != roadmap_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="From node not found")
    if not to_node or to_node.roadmap_id != roadmap_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="To node not found")
    
    return service.create_connection(data.from_node_id, data.to_node_id)


@router.delete("/{roadmap_id}/connections/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_connection(roadmap_id: int, connection_id: int, db: Session = Depends(get_db)):
    service = NodeService(db)
    if not service.delete_connection(connection_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")
