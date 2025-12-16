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

# Configuración de layout - sincronizado con frontend RoadmapGraph.vue
MAX_NODES_PER_ROW = 6
NODE_WIDTH = 160
NODE_HEIGHT = 56
NODE_GAP_X = 50
NODE_GAP_Y = 100
PADDING = 80
LEVEL_GAP = 160  # Espacio vertical entre niveles


def calculate_node_positions(nodes_data: list[dict]) -> dict[int, tuple[int, int]]:
    """
    Calcula posiciones óptimas para nodos considerando:
    - Distribución por niveles (beginner arriba, advanced abajo)
    - Centrado horizontal de cada fila
    - Orden de prerrequisitos para minimizar cruces
    
    Returns: dict mapping node order -> (x, y)
    """
    level_order = {"beginner": 0, "intermediate": 1, "advanced": 2}
    nodes_by_level: dict[str, list[dict]] = {"beginner": [], "intermediate": [], "advanced": []}
    
    for node in nodes_data:
        level = node.get("level", "beginner")
        if level in nodes_by_level:
            nodes_by_level[level].append(node)
    
    # Ordenar cada nivel por order
    for level in nodes_by_level:
        nodes_by_level[level].sort(key=lambda n: n.get("order", 0))
    
    positions: dict[int, tuple[int, int]] = {}
    
    # Calcular ancho del canvas basado en el nivel más ancho
    max_nodes_in_any_row = 1
    for lvl in nodes_by_level:
        count = len(nodes_by_level[lvl])
        if count > max_nodes_in_any_row:
            max_nodes_in_any_row = min(count, MAX_NODES_PER_ROW)
    
    canvas_width = max_nodes_in_any_row * (NODE_WIDTH + NODE_GAP_X) + PADDING * 2
    
    for level, level_idx in level_order.items():
        nodes_in_level = nodes_by_level.get(level, [])
        if not nodes_in_level:
            continue
        
        # Base Y para este nivel
        base_y = PADDING + 50 + level_idx * LEVEL_GAP
        
        for idx, node in enumerate(nodes_in_level):
            row = idx // MAX_NODES_PER_ROW
            col = idx % MAX_NODES_PER_ROW
            nodes_in_this_row = min(MAX_NODES_PER_ROW, len(nodes_in_level) - row * MAX_NODES_PER_ROW)
            
            # Centrar la fila
            row_width = nodes_in_this_row * (NODE_WIDTH + NODE_GAP_X) - NODE_GAP_X
            start_x = (canvas_width - row_width) / 2
            
            x = int(start_x + col * (NODE_WIDTH + NODE_GAP_X))
            y = int(base_y + row * (NODE_GAP_Y + NODE_HEIGHT))
            
            positions[node.get("order", idx)] = (x, y)
    
    return positions


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
    
    # Generar resumen del contenido
    try:
        content_summary = generate_content_summary(
            content=text_content,
            roadmap_title=title,
            nodes_info=nodes_data
        )
    except Exception:
        content_summary = text_content[:2500] + "..." if len(text_content) > 2500 else text_content

    roadmap = roadmap_service.create(
        title=title,
        description=roadmap_data.get("description", f"Roadmap generado a partir de {file.filename}"),
        source_content=content_summary,
        creator_id=creator_id
    )

    # Calcular posiciones con el nuevo algoritmo
    node_positions = calculate_node_positions(nodes_data)
    
    created_nodes = {}
    for node_data in nodes_data:
        level_str = node_data.get("level", "beginner")
        level = NodeLevel(level_str) if level_str in [l.value for l in NodeLevel] else NodeLevel.BEGINNER
        
        order = node_data.get("order", 0)
        position_x, position_y = node_positions.get(order, (0, 0))

        node = node_service.create(
            roadmap_id=roadmap.id,
            title=node_data["title"],
            description=node_data.get("description"),
            level=level,
            position_x=position_x,
            position_y=position_y,
            order_index=order
        )
        created_nodes[order] = node

    # Crear conexiones
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


@router.post("/{roadmap_id}/auto-layout")
async def auto_layout_roadmap(
    roadmap_id: int,
    db: Session = Depends(get_db)
):
    """
    Recalcula las posiciones óptimas de todos los nodos de un roadmap.
    Útil para roadmaps existentes o después de añadir/eliminar nodos.
    """
    roadmap_service = RoadmapService(db)
    node_service = NodeService(db)
    
    roadmap = roadmap_service.get_by_id(roadmap_id)
    if not roadmap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap no encontrado")
    
    nodes = node_service.get_by_roadmap(roadmap_id)
    if not nodes:
        return {"message": "No hay nodos para reorganizar", "roadmap_id": roadmap_id}
    
    # Convertir nodos a formato dict para calculate_node_positions
    nodes_data = [
        {
            "id": node.id,
            "order": node.order_index,
            "level": node.level.value if hasattr(node.level, 'value') else node.level,
            "title": node.title
        }
        for node in nodes
    ]
    
    # Calcular nuevas posiciones
    new_positions = calculate_node_positions(nodes_data)
    
    # Actualizar posiciones en la BD
    updated_count = 0
    for node in nodes:
        pos = new_positions.get(node.order_index)
        if pos:
            node_service.update(node.id, position_x=pos[0], position_y=pos[1])
            updated_count += 1
    
    return {
        "message": f"Posiciones recalculadas para {updated_count} nodos",
        "roadmap_id": roadmap_id,
        "nodes_updated": updated_count
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
    - Cada nivel (beginner, intermediate, advanced) debe tener entre 2 y 8 nodos
    """
    roadmap_service = RoadmapService(db)
    node_service = NodeService(db)

    if not request.data.nodes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El roadmap debe tener al menos un nodo"
        )

    valid_levels = {"beginner", "intermediate", "advanced"}
    level_counts = {"beginner": 0, "intermediate": 0, "advanced": 0}
    
    for node_data in request.data.nodes:
        if node_data.level not in valid_levels:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Nivel inválido '{node_data.level}' en nodo '{node_data.title}'. Use: {', '.join(valid_levels)}"
            )
        level_counts[node_data.level] += 1
    
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

    roadmap = roadmap_service.create(
        title=request.title,
        description=request.data.description or f"Roadmap importado: {request.title}",
        source_content=None,
        creator_id=request.creator_id
    )

    # Preparar datos para calcular posiciones
    nodes_dict_list = [
        {"order": n.order, "level": n.level, "title": n.title}
        for n in request.data.nodes
    ]
    node_positions = calculate_node_positions(nodes_dict_list)

    created_nodes = {}
    for node_data in request.data.nodes:
        level = NodeLevel(node_data.level)
        position_x, position_y = node_positions.get(node_data.order, (0, 0))

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
