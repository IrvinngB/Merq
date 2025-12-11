import os
import json
import re
from io import BytesIO
from PyPDF2 import PdfReader
from ollama import Client

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma2")

MAX_CONTENT_LENGTH = 6000
MAX_RETRIES = 3


def get_ollama_client() -> Client:
    """Obtiene el cliente de Ollama."""
    return Client(host=OLLAMA_HOST)


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extrae texto de un archivo PDF."""
    reader = PdfReader(BytesIO(file_content))
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    text = "\n\n".join(text_parts)
    # Limpiar caracteres NUL y otros caracteres no válidos para PostgreSQL
    text = text.replace('\x00', '')
    text = ''.join(char for char in text if char.isprintable() or char in '\n\r\t')
    return text


def truncate_content(content: str, max_length: int = MAX_CONTENT_LENGTH) -> str:
    """Trunca el contenido de forma inteligente, intentando cortar en párrafos."""
    if len(content) <= max_length:
        return content
    
    truncated = content[:max_length]
    last_paragraph = truncated.rfind("\n\n")
    if last_paragraph > max_length * 0.7:
        return truncated[:last_paragraph]
    
    last_sentence = truncated.rfind(". ")
    if last_sentence > max_length * 0.7:
        return truncated[:last_sentence + 1]
    
    return truncated


def clean_json_text(text: str) -> str:
    """Limpia y repara JSON malformado."""
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    
    text = text.strip()
    
    # Buscar el JSON entre llaves
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        text = text[start:end]
    
    # Reparar problemas comunes
    text = re.sub(r',\s*}', '}', text)  # Coma antes de }
    text = re.sub(r',\s*]', ']', text)  # Coma antes de ]
    text = text.replace('\n', ' ')       # Saltos de línea
    text = re.sub(r'\s+', ' ', text)     # Espacios múltiples
    
    return text


def parse_json_response(response_text: str) -> dict:
    """Parsea la respuesta JSON con múltiples estrategias de reparación."""
    # Intento 1: Directo
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass
    
    # Intento 2: Limpiar y reparar
    try:
        cleaned = clean_json_text(response_text)
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    # Intento 3: Extraer con regex más agresivo
    try:
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            return json.loads(clean_json_text(match.group()))
    except json.JSONDecodeError:
        pass
    
    raise ValueError(f"No se pudo parsear JSON: {response_text[:200]}...")


def call_ollama(prompt: str) -> str:
    """Llama a Ollama y retorna la respuesta."""
    client = get_ollama_client()
    response = client.generate(
        model=OLLAMA_MODEL,
        prompt=prompt,
        options={
            "temperature": 0.7,
            "num_predict": 4096,
        }
    )
    return response["response"]


def call_ollama_text(prompt: str) -> str:
    """Llama a Ollama y retorna texto plano (sin JSON)."""
    client = get_ollama_client()
    response = client.generate(
        model=OLLAMA_MODEL,
        prompt=prompt,
        options={
            "temperature": 0.5,
            "num_predict": 2048,
        }
    )
    return response["response"].strip()


def call_ollama_with_retry(prompt: str) -> dict:
    """Llama a Ollama con reintentos si falla el parsing JSON."""
    last_error = None
    
    for attempt in range(MAX_RETRIES):
        response_text = call_ollama(prompt)
        try:
            return parse_json_response(response_text)
        except (json.JSONDecodeError, ValueError) as e:
            last_error = e
            continue
    
    raise last_error


def generate_content_summary(content: str, roadmap_title: str, nodes_info: list[dict]) -> str:
    """
    Genera un resumen optimizado del contenido para usar en generación de nodos.
    Este resumen reemplaza guardar todo el texto del PDF/TXT.
    Máximo ~3000 caracteres para mantener la BD ligera.
    """
    processed_content = truncate_content(content, max_length=4000)
    
    # Crear lista de temas de los nodos
    topics_list = "\n".join([f"- {n.get('title', '')}: {n.get('description', '')}" for n in nodes_info])
    
    prompt = f"""Eres un experto en síntesis de contenido educativo. 
    
Analiza el siguiente contenido y genera un RESUMEN ESTRUCTURADO que capture:
1. Los conceptos principales y definiciones clave
2. Información relevante para cada tema del roadmap
3. Datos, ejemplos o casos importantes mencionados

El resumen debe ser útil para generar contenido educativo detallado sobre estos temas:
{topics_list}

REGLAS:
- Máximo 2500 caracteres
- Usa bullet points y secciones claras
- Incluye términos técnicos y definiciones exactas del documento
- NO incluyas opiniones, solo hechos del documento

Título del roadmap: {roadmap_title}

Contenido a resumir:
{processed_content}

RESUMEN ESTRUCTURADO:"""

    summary = call_ollama_text(prompt)
    
    # Limitar a 3000 caracteres máximo
    if len(summary) > 3000:
        summary = summary[:2997] + "..."
    
    return summary


def validate_roadmap_structure(roadmap_data: dict, strict: bool = True) -> tuple[bool, dict]:
    """
    Valida la estructura del roadmap.
    
    Args:
        roadmap_data: Datos del roadmap a validar
        strict: Si True, requiere 3+ nodos por nivel. Si False, acepta 2+ nodos.
    
    Returns:
        Tuple (is_valid, level_counts)
    """
    nodes = roadmap_data.get("nodes", [])
    
    # Contar nodos por nivel
    level_counts = {"beginner": 0, "intermediate": 0, "advanced": 0}
    
    for node in nodes:
        level = node.get("level", "beginner")
        if level in level_counts:
            level_counts[level] += 1
    
    min_nodes = 3 if strict else 2
    max_nodes = 8
    
    valid = True
    for level, count in level_counts.items():
        if count < min_nodes or count > max_nodes:
            valid = False
            break
    
    return valid, level_counts


def generate_roadmap(content: str, title: str) -> dict:
    """
    Genera un roadmap de aprendizaje estructurado por niveles.
    Incluye múltiples reintentos con prompts cada vez más específicos.
    """
    processed_content = truncate_content(content)

    base_prompt = f"""Eres un experto en diseño de rutas de aprendizaje. Analiza el contenido y crea un roadmap educativo completo.

RESPONDE ÚNICAMENTE CON JSON VÁLIDO. Sin texto adicional.

Formato JSON requerido:
{{
  "description": "Descripción breve del roadmap",
  "nodes": [
    {{"title": "Tema", "description": "Qué aprenderás", "level": "beginner", "order": 0, "prerequisites": []}}
  ]
}}

ESTRUCTURA OBLIGATORIA - CADA NIVEL DEBE TENER ENTRE 3 Y 6 NODOS:
- beginner (3-6 nodos): Fundamentos y conceptos básicos
- intermediate (3-6 nodos): Aplicación práctica y técnicas  
- advanced (3-6 nodos): Temas avanzados y especialización

REGLAS:
1. MÍNIMO 3 nodos por nivel, MÁXIMO 6 nodos por nivel
2. Total: 9-18 nodos
3. Títulos: 2-5 palabras
4. order: secuencial desde 0
5. prerequisites: [] para beginner, [1-2 índices previos] para intermediate/advanced

Título: {title}

Contenido:
{processed_content}

JSON:"""

    # Intento 1: Prompt base
    roadmap_data = call_ollama_with_retry(base_prompt)
    is_valid, counts = validate_roadmap_structure(roadmap_data, strict=True)
    
    if is_valid:
        return roadmap_data
    
    # Intento 2: Prompt con énfasis en los niveles que faltan
    missing_levels = [level for level, count in counts.items() if count < 3]
    
    retry_prompt = f"""CORRIGE EL ROADMAP. Faltan nodos en: {', '.join(missing_levels)}.

Nodos actuales: beginner={counts['beginner']}, intermediate={counts['intermediate']}, advanced={counts['advanced']}

GENERA UN NUEVO ROADMAP CON EXACTAMENTE:
- 4 nodos beginner (fundamentos básicos)
- 4 nodos intermediate (aplicación práctica)
- 4 nodos advanced (especialización y casos avanzados)

Total: 12 nodos exactos.

RESPONDE SOLO CON JSON:
{{
  "description": "Descripción",
  "nodes": [
    {{"title": "Tema", "description": "Descripción", "level": "beginner|intermediate|advanced", "order": 0, "prerequisites": []}}
  ]
}}

Título: {title}

Contenido:
{processed_content}

JSON:"""

    roadmap_data = call_ollama_with_retry(retry_prompt)
    is_valid, counts = validate_roadmap_structure(roadmap_data, strict=True)
    
    if is_valid:
        return roadmap_data
    
    # Intento 3: Prompt ultra específico con ejemplos
    specific_prompt = f"""GENERA EXACTAMENTE 12 NODOS para el roadmap "{title}".

ESTRUCTURA EXACTA REQUERIDA (copia este formato):
{{
  "description": "Roadmap de aprendizaje sobre {title}",
  "nodes": [
    {{"title": "Concepto Básico 1", "description": "Fundamento esencial", "level": "beginner", "order": 0, "prerequisites": []}},
    {{"title": "Concepto Básico 2", "description": "Fundamento esencial", "level": "beginner", "order": 1, "prerequisites": []}},
    {{"title": "Concepto Básico 3", "description": "Fundamento esencial", "level": "beginner", "order": 2, "prerequisites": []}},
    {{"title": "Concepto Básico 4", "description": "Fundamento esencial", "level": "beginner", "order": 3, "prerequisites": []}},
    {{"title": "Aplicación 1", "description": "Técnica práctica", "level": "intermediate", "order": 4, "prerequisites": [0, 1]}},
    {{"title": "Aplicación 2", "description": "Técnica práctica", "level": "intermediate", "order": 5, "prerequisites": [1, 2]}},
    {{"title": "Aplicación 3", "description": "Técnica práctica", "level": "intermediate", "order": 6, "prerequisites": [2, 3]}},
    {{"title": "Aplicación 4", "description": "Técnica práctica", "level": "intermediate", "order": 7, "prerequisites": [0, 3]}},
    {{"title": "Avanzado 1", "description": "Especialización", "level": "advanced", "order": 8, "prerequisites": [4, 5]}},
    {{"title": "Avanzado 2", "description": "Especialización", "level": "advanced", "order": 9, "prerequisites": [5, 6]}},
    {{"title": "Avanzado 3", "description": "Especialización", "level": "advanced", "order": 10, "prerequisites": [6, 7]}},
    {{"title": "Avanzado 4", "description": "Especialización", "level": "advanced", "order": 11, "prerequisites": [4, 7]}}
  ]
}}

Reemplaza los títulos y descripciones con temas REALES del contenido.
Mantén EXACTAMENTE 4 nodos por nivel.

Contenido a analizar:
{processed_content}

JSON:"""

    roadmap_data = call_ollama_with_retry(specific_prompt)
    is_valid, counts = validate_roadmap_structure(roadmap_data, strict=True)
    
    if is_valid:
        return roadmap_data
    
    # Último recurso: Validación flexible (mínimo 2 por nivel)
    is_valid_flexible, _ = validate_roadmap_structure(roadmap_data, strict=False)
    
    if is_valid_flexible:
        return roadmap_data
    
    # Si todo falla, lanzar error con información útil
    raise ValueError(
        f"No se pudo generar un roadmap válido después de múltiples intentos. "
        f"Nodos generados - beginner: {counts['beginner']}, "
        f"intermediate: {counts['intermediate']}, advanced: {counts['advanced']}. "
        f"Intente con un contenido más extenso o específico."
    )


def generate_node_content(source_content: str, node_title: str, node_description: str) -> dict:
    """
    Genera el contenido detallado de un nodo específico.
    Incluye qué investigar, recursos sugeridos y puntos clave.
    """
    processed_content = truncate_content(source_content)

    prompt = f"""Genera contenido educativo detallado para el tema "{node_title}".

RESPONDE ÚNICAMENTE CON JSON VÁLIDO.

El campo "content" debe ser Markdown bien estructurado con:
- ## Headers para secciones
- **Negritas** para conceptos importantes
- Listas con viñetas (-)
- `código` para términos técnicos si aplica

Estructura del contenido:
1. Breve introducción al tema
2. Conceptos clave a dominar
3. Pasos o puntos importantes
4. Tips prácticos

Formato JSON:
{{"content": "## Introducción\\n\\nExplicación clara del tema...\\n\\n## Conceptos Clave\\n\\n- **Concepto 1**: explicación\\n- **Concepto 2**: explicación\\n\\n## Puntos Importantes\\n\\n1. Primer punto\\n2. Segundo punto\\n\\n## Tips\\n\\n- Tip práctico 1\\n- Tip práctico 2"}}

Tema: {node_title}
Contexto: {node_description}

Material de referencia:
{processed_content}

JSON:"""

    return call_ollama_with_retry(prompt)
