from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.services.ai_service import extract_text_from_pdf, generate_roadmap, generate_node_content, generate_content_summary
from app.services.roadmap_service import RoadmapService, NodeService
from app.models import NodeLevel

router = APIRouter(prefix="/ai", tags=["ai"])

ALLOWED_EXTENSIONS = {"pdf", "txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Configuración de layout - máximo 8 nodos por fila
MAX_NODES_PER_ROW = 8
NODE_WIDTH = 170
NODE_GAP_X = 16
NODE_GAP_Y = 70


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

    nodes_data = roadmap_data.get("nodes", [])
    
    # Generar resumen del contenido en lugar de guardar todo el texto
    try:
        content_summary = generate_content_summary(
            content=text_content,
            roadmap_title=title,
            nodes_info=nodes_data
        )
    except Exception as e:
        # Si falla el resumen, usar una versión truncada simple
        content_summary = text_content[:2500] + "..." if len(text_content) > 2500 else text_content

    roadmap = roadmap_service.create(
        title=title,
        description=roadmap_data.get("description", f"Roadmap generado a partir de {file.filename}"),
        source_content=content_summary,  # Guardar resumen, no todo el contenido
        creator_id=creator_id
    )

    created_nodes = {}
    level_counters = {"beginner": 0, "intermediate": 0, "advanced": 0}
    
    # Calcular posiciones basadas en el nuevo layout
    def calculate_position(level: str, index_in_level: int) -> tuple[int, int]:
        """Calcula x, y para un nodo basado en su nivel e índice."""
        level_order = {"beginner": 0, "intermediate": 1, "advanced": 2}
        
        row = index_in_level // MAX_NODES_PER_ROW
        col = index_in_level % MAX_NODES_PER_ROW
        
        # Y basado en el nivel y la fila dentro del nivel
        base_y = level_order.get(level, 0) * 150
        y = base_y + row * (50 + 12)
        
        # X centrado
        x = col * (NODE_WIDTH + NODE_GAP_X)
        
        return x, y

    for node_data in nodes_data:
        level_str = node_data.get("level", "beginner")
        level = NodeLevel(level_str) if level_str in [l.value for l in NodeLevel] else NodeLevel.BEGINNER
        
        index_in_level = level_counters.get(level.value, 0)
        position_x, position_y = calculate_position(level.value, index_in_level)
        level_counters[level.value] = index_in_level + 1

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


# === IMPORT JSON ENDPOINT ===

class ImportNodeData(BaseModel):
    title: str
    description: Optional[str] = None
    level: str = "beginner"
    order: int = 0
    prerequisites: list[int] = []


class ImportRoadmapData(BaseModel):
    description: Optional[str] = None
    nodes: list[ImportNodeData]


class ImportRoadmapRequest(BaseModel):
    title: str
    creator_id: int
    data: ImportRoadmapData


@router.post("/import-roadmap")
async def import_roadmap_from_json(
    request: ImportRoadmapRequest,
    db: Session = Depends(get_db)
):
    """
    Importa un roadmap desde un JSON generado externamente (Claude, GPT, Gemini, etc).
    
    El JSON debe tener la estructura:
    {
        "title": "Título del roadmap",
        "creator_id": 1,
        "data": {
            "description": "Descripción del roadmap",
            "nodes": [
                {"title": "Tema", "description": "...", "level": "beginner", "order": 0, "prerequisites": []}
            ]
        }
    }
    
    Requisitos:
    - Cada nivel (beginner, intermediate, advanced) debe tener entre 3 y 8 nodos
    """
    roadmap_service = RoadmapService(db)
    node_service = NodeService(db)

    # Validar que hay nodos
    if not request.data.nodes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El roadmap debe tener al menos un nodo"
        )

    # Validar niveles y contar nodos por nivel
    valid_levels = {"beginner", "intermediate", "advanced"}
    level_counts = {"beginner": 0, "intermediate": 0, "advanced": 0}
    
    for node_data in request.data.nodes:
        if node_data.level not in valid_levels:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Nivel inválido '{node_data.level}' en nodo '{node_data.title}'. Use: {', '.join(valid_levels)}"
            )
        level_counts[node_data.level] += 1
    
    # Validar cantidad de nodos por nivel (mínimo 2, máximo 8) - más flexible para importación
    MIN_NODES_PER_LEVEL = 2
    MAX_NODES_PER_LEVEL = 8
    
    for level, count in level_counts.items():
        if count < MIN_NODES_PER_LEVEL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El nivel '{level}' tiene {count} nodo(s). Se requieren mínimo {MIN_NODES_PER_LEVEL} nodos por nivel."
            )
        if count > MAX_NODES_PER_LEVEL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El nivel '{level}' tiene {count} nodos. Se permiten máximo {MAX_NODES_PER_LEVEL} nodos por nivel."
            )

    # Crear roadmap
    roadmap = roadmap_service.create(
        title=request.title,
        description=request.data.description or f"Roadmap importado: {request.title}",
        source_content=None,  # No hay contenido fuente al importar
        creator_id=request.creator_id
    )

    # Calcular posiciones
    level_counters = {"beginner": 0, "intermediate": 0, "advanced": 0}
    
    def calculate_position(level: str, index_in_level: int) -> tuple[int, int]:
        level_order = {"beginner": 0, "intermediate": 1, "advanced": 2}
        row = index_in_level // MAX_NODES_PER_ROW
        col = index_in_level % MAX_NODES_PER_ROW
        base_y = level_order.get(level, 0) * 150
        y = base_y + row * (50 + 12)
        x = col * (NODE_WIDTH + NODE_GAP_X)
        return x, y

    # Crear nodos
    created_nodes = {}
    for node_data in request.data.nodes:
        level = NodeLevel(node_data.level)
        index_in_level = level_counters.get(node_data.level, 0)
        position_x, position_y = calculate_position(node_data.level, index_in_level)
        level_counters[node_data.level] = index_in_level + 1

        node = node_service.create(
            roadmap_id=roadmap.id,
            title=node_data.title,
            description=node_data.description,
            level=level,
            position_x=position_x,
            position_y=position_y,
            order_index=node_data.order
        )
        created_nodes[node_data.order] = node

    # Crear conexiones basadas en prerequisites
    for node_data in request.data.nodes:
        if node_data.order in created_nodes:
            for prereq_order in node_data.prerequisites:
                if prereq_order in created_nodes:
                    node_service.create_connection(
                        from_node_id=created_nodes[prereq_order].id,
                        to_node_id=created_nodes[node_data.order].id
                    )

    return {
        "roadmap_id": roadmap.id,
        "title": roadmap.title,
        "nodes_count": len(request.data.nodes),
        "message": "Roadmap importado exitosamente"
    }

