from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.ai_service import extract_text_from_pdf, generate_roadmap, generate_node_content
from app.services.roadmap_service import RoadmapService, NodeService
from app.models import NodeLevel

router = APIRouter(prefix="/ai", tags=["ai"])

ALLOWED_EXTENSIONS = {"pdf", "txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

LEVEL_POSITIONS = {
    "beginner": {"y": 0},
    "intermediate": {"y": 200},
    "advanced": {"y": 400}
}


@router.post("/generate-roadmap")
async def generate_roadmap_from_file(
    file: UploadFile = File(...),
    title: str = Form(...),
    creator_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """
    Recibe un PDF o TXT, extrae el contenido y genera un roadmap de aprendizaje
    con nodos organizados por niveles y conexiones entre ellos.
    """
    extension = file.filename.split(".")[-1].lower() if file.filename else ""
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido. Use: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo excede el tamaño máximo de 10MB"
        )

    if extension == "pdf":
        try:
            text_content = extract_text_from_pdf(file_content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al procesar el PDF: {str(e)}"
            )
    else:
        text_content = file_content.decode("utf-8", errors="ignore")

    if len(text_content.strip()) < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El contenido extraído es muy corto. Asegúrate de que el archivo tenga texto legible."
        )

    try:
        roadmap_data = generate_roadmap(text_content, title)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar el roadmap con IA: {str(e)}"
        )

    roadmap_service = RoadmapService(db)
    node_service = NodeService(db)

    roadmap = roadmap_service.create(
        title=title,
        description=roadmap_data.get("description", f"Roadmap generado a partir de {file.filename}"),
        source_content=text_content,
        creator_id=creator_id
    )

    nodes_data = roadmap_data.get("nodes", [])
    created_nodes = {}
    level_counters = {"beginner": 0, "intermediate": 0, "advanced": 0}

    for node_data in nodes_data:
        level_str = node_data.get("level", "beginner")
        level = NodeLevel(level_str) if level_str in [l.value for l in NodeLevel] else NodeLevel.BEGINNER
        
        position_x = level_counters.get(level.value, 0) * 250
        position_y = LEVEL_POSITIONS.get(level.value, {"y": 0})["y"]
        level_counters[level.value] = level_counters.get(level.value, 0) + 1

        node = node_service.create(
            roadmap_id=roadmap.id,
            title=node_data["title"],
            description=node_data.get("description"),
            level=level,
            position_x=position_x,
            position_y=position_y,
            order_index=node_data.get("order", 0)
        )
        created_nodes[node_data.get("order", 0)] = node

    for node_data in nodes_data:
        node_order = node_data.get("order", 0)
        prerequisites = node_data.get("prerequisites", [])
        
        if node_order in created_nodes:
            for prereq_order in prerequisites:
                if prereq_order in created_nodes:
                    node_service.create_connection(
                        from_node_id=created_nodes[prereq_order].id,
                        to_node_id=created_nodes[node_order].id
                    )

    return {
        "roadmap_id": roadmap.id,
        "title": roadmap.title,
        "nodes_count": len(nodes_data),
        "message": "Roadmap creado exitosamente"
    }


@router.post("/nodes/{node_id}/generate-content")
async def generate_node_content_endpoint(
    node_id: int,
    db: Session = Depends(get_db)
):
    """
    Genera el contenido detallado de un nodo específico bajo demanda.
    """
    node_service = NodeService(db)
    roadmap_service = RoadmapService(db)

    node = node_service.get_by_id(node_id)
    if not node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nodo no encontrado")

    if node.content:
        return {"message": "El nodo ya tiene contenido generado", "node_id": node_id}

    roadmap = roadmap_service.get_by_id(node.roadmap_id)
    if not roadmap or not roadmap.source_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El roadmap no tiene contenido fuente para generar"
        )

    try:
        content_data = generate_node_content(
            source_content=roadmap.source_content,
            node_title=node.title,
            node_description=node.description or ""
        )
        
        node_service.update(node_id, content=content_data.get("content", ""))
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar contenido: {str(e)}"
        )

    return {
        "message": "Contenido del nodo generado exitosamente",
        "node_id": node_id
    }
