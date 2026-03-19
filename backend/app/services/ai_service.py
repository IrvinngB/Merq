"""
AI Service - Roadmap Generation
Business Logic Layer
- Uses ai_provider.py for connections
- Handles Prompt Engineering & Parsing
"""

import json
import re
from io import BytesIO
from urllib.parse import quote_plus
import pdfplumber
from .ai_provider import AIGateway

# Initialize Gateway (handles Gemini/Ollama connections)
gateway = AIGateway()

# Content limits
MAX_CONTENT_LENGTH = 25000 
MAX_SUMMARY_LENGTH = 12000
MAX_RETRIES = 3
TARGET_ROADMAP_NODES = 15

def log_ai(msg):
    print(f"[AI SERVICE] {msg}", flush=True)

def call_ai(prompt: str, json_mode: bool = False, provider: str = None, model: str = None) -> str:
    """
    Call AI using the Gateway.

    Args:
        provider: "gemini", "qwen", "ollama", or None (auto-fallback)
        model: Optional model override for selected provider
    """
    try:
        response_text, provider_name = gateway.generate(prompt, json_mode, provider=provider, model=model)

        # LOGGING
        log_ai(f"Used Provider: {provider_name}")
        log_ai(f"--- AI RESPONSE ({provider_name}) ---")
        log_ai(response_text[:500] + "..." if len(response_text) > 500 else response_text)
        log_ai("-------------------------------")

        return response_text
    except Exception as e:
        log_ai(f"CRITICAL AI FAILURE: {e}")
        raise e

def call_ai_text(prompt: str) -> str:
    """Call AI for plain text response (no JSON)."""
    return call_ai(prompt, json_mode=False)


# =============================================================================
# PDF EXTRACTION - Using pdfplumber
# =============================================================================

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF using pdfplumber (more robust than PyPDF2)."""
    text_parts = []
    
    with pdfplumber.open(BytesIO(file_content)) as pdf:
        for page in pdf.pages:
            # Extract text with better handling of layouts
            text = page.extract_text(layout=True)
            if text:
                text_parts.append(text)
    
    text = "\n\n".join(text_parts)
    
    # Clean invalid characters for PostgreSQL
    text = text.replace('\x00', '')
    text = ''.join(char for char in text if char.isprintable() or char in '\n\r\t')
    
    return text.strip()


# =============================================================================
# TEXT PROCESSING
# =============================================================================

def truncate_content(content: str, max_length: int = MAX_CONTENT_LENGTH) -> str:
    """Truncate content intelligently at paragraph or sentence boundaries."""
    if len(content) <= max_length:
        return content
    
    truncated = content[:max_length]
    
    # Try to cut at paragraph
    last_paragraph = truncated.rfind("\n\n")
    if last_paragraph > max_length * 0.7:
        return truncated[:last_paragraph]
    
    # Try to cut at sentence
    last_sentence = truncated.rfind(". ")
    if last_sentence > max_length * 0.7:
        return truncated[:last_sentence + 1]
    
    return truncated


def clean_json_text(text: str) -> str:
    """Clean and repair malformed JSON from AI responses."""
    # Remove markdown code blocks
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        parts = text.split("```")
        if len(parts) >= 2:
            text = parts[1]
    
    text = text.strip()
    
    # Extract JSON object
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        text = text[start:end]
    
    # Fix common issues
    text = re.sub(r',\s*}', '}', text)  # Trailing comma before }
    text = re.sub(r',\s*]', ']', text)  # Trailing comma before ]
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    
    return text


def parse_json_response(response_text: str) -> dict:
    """Parse JSON response with multiple repair strategies."""
    # Direct attempt
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass
    
    # Clean and retry
    try:
        cleaned = clean_json_text(response_text)
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    # Aggressive regex extraction
    try:
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            return json.loads(clean_json_text(match.group()))
    except json.JSONDecodeError:
        pass
    
    raise ValueError(f"Could not parse JSON: {response_text[:200]}...")


def call_ai_with_retry(prompt: str, provider: str = None, model: str = None) -> dict:
    """Call AI with retries for JSON parsing failures."""
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            # Try with JSON mode first (Gemini/Qwen native)
            response_text = call_ai(prompt, json_mode=True, provider=provider, model=model)
            return parse_json_response(response_text)
        except Exception as e:
            last_error = e
            # Retry without JSON mode
            try:
                response_text = call_ai(prompt, json_mode=False, provider=provider, model=model)
                return parse_json_response(response_text)
            except Exception as e2:
                last_error = e2
                continue

    if last_error:
        raise last_error
    raise ValueError("Failed to get valid JSON response")


# =============================================================================
# CONTENT SUMMARY (Optimized for storage)
# =============================================================================

def generate_content_summary(content: str, roadmap_title: str, nodes_info: list[dict], provider: str = None, model: str = None) -> str:
    """
    Generate optimized summary for node content generation.
    Stored in DB instead of full content, but with enough context for rich node generation.
    """
    processed_content = truncate_content(content, max_length=14000)

    # Build topics list compactly
    topics = "\n".join([f"• {n.get('title', '')}" for n in nodes_info[:12]])

    prompt = f"""Genera un RESUMEN ESTRUCTURADO y CONCISO del contenido.

REGLAS:
- Máximo 11000 caracteres
- Usa secciones y bullet points claros
- Incluye conceptos clave, ejemplos, casos de uso y errores frecuentes
- Conserva terminología técnica importante del material
- NO incluyas opiniones

Temas del roadmap "{roadmap_title}":
{topics}

Contenido:
{processed_content}

RESUMEN:"""

    summary = call_ai(prompt, json_mode=False, provider=provider, model=model)

    # Enforce max length
    if len(summary) > MAX_SUMMARY_LENGTH:
        summary = summary[:MAX_SUMMARY_LENGTH - 3] + "..."

    return summary


# =============================================================================
# ROADMAP VALIDATION
# =============================================================================

def validate_roadmap_structure(roadmap_data: dict, strict: bool = True) -> tuple[bool, dict]:
    """
    Validate roadmap structure.
    
    Args:
        roadmap_data: Roadmap data to validate
        strict: If True, requires 3+ nodes per level. If False, accepts 1+ nodes.
    
    Returns:
        Tuple (is_valid, level_counts)
    """
    nodes = roadmap_data.get("nodes", [])
    
    level_counts = {"beginner": 0, "intermediate": 0, "advanced": 0}
    
    for node in nodes:
        level = node.get("level", "beginner")
        if level in level_counts:
            level_counts[level] += 1
    
    min_nodes = 4 if strict else 1
    max_nodes = 10
    
    valid = all(min_nodes <= count <= max_nodes for count in level_counts.values())
    
    return valid, level_counts


def _sanitize_node_title(title: str, fallback_index: int) -> str:
    clean = re.sub(r'\s+', ' ', (title or '').strip())
    if not clean:
        return f"Tema {fallback_index + 1}"
    words = clean.split(' ')
    if len(words) > 7:
        clean = ' '.join(words[:7])
    return clean


def _sanitize_node_description(description: str) -> str:
    clean = re.sub(r'\s+', ' ', (description or '').strip())
    if not clean:
        return "Aprenderás los fundamentos, práctica guiada y criterios para aplicar este tema."
    if len(clean) < 40:
        return f"{clean}. Incluye conceptos clave, pasos prácticos y errores comunes a evitar."
    return clean


def _sanitize_track(track: str | None, level: str) -> str:
    clean = re.sub(r'\s+', '-', (track or '').strip().lower())
    clean = re.sub(r'[^a-z0-9\-_]', '', clean)
    if clean:
        return clean[:60]
    if level == "beginner":
        return "fundamentals"
    if level == "intermediate":
        return "implementation"
    return "specialization"


def normalize_roadmap_data(roadmap_data: dict) -> dict:
    """
    Normalize roadmap content to keep quality and consistency even when the AI response is imperfect.
    """
    raw_nodes = roadmap_data.get("nodes", [])
    if not isinstance(raw_nodes, list):
        raw_nodes = []

    if not raw_nodes:
        raise ValueError("La IA no devolvió nodos para construir el roadmap")

    # Keep target node count for a deeper roadmap.
    raw_nodes = raw_nodes[:TARGET_ROADMAP_NODES]
    seen_titles = set()
    normalized = []

    for i, node in enumerate(raw_nodes):
        title = _sanitize_node_title(node.get("title", ""), i)
        base_title = title
        suffix = 2
        while title.lower() in seen_titles:
            title = f"{base_title} ({suffix})"
            suffix += 1
        seen_titles.add(title.lower())

        level = node.get("level", "beginner")
        if level not in ("beginner", "intermediate", "advanced"):
            level = "beginner"

        prerequisites = node.get("prerequisites", [])
        if not isinstance(prerequisites, list):
            prerequisites = []
        valid_prereq = sorted({p for p in prerequisites if isinstance(p, int) and 0 <= p < i})

        normalized.append({
            "title": title,
            "description": _sanitize_node_description(node.get("description", "")),
            "track": _sanitize_track(node.get("track"), level),
            "level": level,
            "order": i,
            "prerequisites": valid_prereq,
        })

    # Re-balance levels if the model failed to distribute content correctly.
    balanced = redistribute_nodes_levels(normalized)
    return {
        "description": re.sub(r'\s+', ' ', (roadmap_data.get("description") or "").strip()) or "Ruta de aprendizaje generada con IA",
        "nodes": balanced,
    }


# =============================================================================
# ROADMAP GENERATION - TOON-inspired compact prompts
# =============================================================================

def generate_roadmap(content: str, title: str, provider: str = None, model: str = None) -> dict:
    """
    Generate learning roadmap structured by levels.
    Uses compact prompts for token efficiency.

    Args:
        provider: "gemini", "qwen", "ollama", or None (auto-fallback)
        model: Optional model override for selected provider
    """
    # Use larger context window
    processed_content = truncate_content(content)

    # Compact prompt design (TOON-inspired: less syntax, more data)
    base_prompt = f"""Analiza el contenido y genera un roadmap de aprendizaje accionable.

RESPONDE SOLO JSON:
{{
    "description": "Descripción breve (1-2 líneas, enfocada en resultados)",
  "nodes": [
      {{"title": "Tema", "description": "Qué aprenderás y para qué sirve", "track": "fundamentals|implementation|specialization|...", "level": "beginner|intermediate|advanced", "order": 0, "prerequisites": []}}
  ]
}}

ESTRUCTURA (15 nodos total):
• beginner: 5 nodos - fundamentos
• intermediate: 5 nodos - aplicación práctica
• advanced: 5 nodos - especialización

SUBNIVELES (dentro de cada nivel):
• beginner: B1, B2
• intermediate: I1, I2
• advanced: A1, A2

REGLAS:
• titles: 2-5 palabras
• order: 0-14 secuencial
• prerequisites: Cada nodo intermediate/advanced debe tener 1-2 prerequisitos válidos de nodos anteriores
• track: cada nodo debe incluir un track textual corto (ej: fundamentals, backend, data, devops, project, architecture)
• Evita títulos genéricos como "Introducción" repetida o "Tema avanzado" sin contexto
• Incluye progresión real: fundamentos -> práctica -> integración/proyecto
• En description, empieza con etiqueta de subnivel, por ejemplo: "[B1] ...", "[I2] ...", "[A1] ..."

Título: {title}

Contenido:
{processed_content}

JSON:"""

    # Attempt 1
    roadmap_data = call_ai_with_retry(base_prompt, provider=provider, model=model)
    roadmap_data = normalize_roadmap_data(roadmap_data)
    is_valid, counts = validate_roadmap_structure(roadmap_data, strict=True)

    if is_valid:
        return roadmap_data

    # Attempt 2: More specific
    retry_prompt = f"""Tu tarea es GENERAR EL JSON COMPLETO del roadmap.

ERROR PREVIO: Faltan nodos. Se requieren estos conteos exactos:
- beginner: 5 nodos
- intermediate: 5 nodos
- advanced: 5 nodos

GENERA EL JSON SIGUIENDO ESTA ESTRUCTURA EXACTA:
{{
  "description": "Descripción...",
  "nodes": [
        {{"title": "T1", "description": "[B1] ...", "track": "fundamentals", "level": "beginner", "order": 0, "prerequisites": []}},
        {{"title": "T2", "description": "[B1] ...", "track": "fundamentals", "level": "beginner", "order": 1, "prerequisites": []}},
        {{"title": "T3", "description": "[B2] ...", "track": "practice", "level": "beginner", "order": 2, "prerequisites": []}},
        {{"title": "T4", "description": "[B2] ...", "track": "practice", "level": "beginner", "order": 3, "prerequisites": []}},
        {{"title": "T5", "description": "[B2] ...", "track": "practice", "level": "beginner", "order": 4, "prerequisites": []}},
        {{"title": "T6", "description": "[I1] ...", "track": "implementation", "level": "intermediate", "order": 5, "prerequisites": [3,4]}},
        ... (hasta completar los 15 nodos)
  ]
}}

NO expliques nada. SOLO JSON.

Título: {title}
Contenido:
{processed_content[:3000]}

JSON:"""

    roadmap_data = call_ai_with_retry(retry_prompt, provider=provider, model=model)
    roadmap_data = normalize_roadmap_data(roadmap_data)
    is_valid, counts = validate_roadmap_structure(roadmap_data, strict=True)
    
    if is_valid:
        return roadmap_data
    
    # Attempt 3: Flexible validation
    is_valid_flex, _ = validate_roadmap_structure(roadmap_data, strict=False)
    
    if is_valid_flex:
        return roadmap_data

    # Attempt 4: Auto-Balancing (Safety Net)
    # If we have enough total nodes but distribution is wrong (e.g. 0 advanced),
    # we algorithmically reassign levels based on order.
    nodes = roadmap_data.get("nodes", [])
    if len(nodes) >= 8:
        log_ai("Validation failed but enough nodes present. Auto-balancing levels.")
        roadmap_data["nodes"] = redistribute_nodes_levels(nodes)
        return roadmap_data
    
    raise ValueError(
        f"No se pudo generar roadmap válido. "
        f"Nodos: beginner={counts['beginner']}, intermediate={counts['intermediate']}, advanced={counts['advanced']}. "
        f"Contenido insuficiente para distribuir en 3 niveles."
    )


# =============================================================================
# AUTO-BALANCING UTILS
# =============================================================================

def redistribute_nodes_levels(nodes: list[dict]) -> list[dict]:
    """
    Force balanced distribution of levels based on node order.
    Used when AI generates enough nodes but fails strict level counts.
    """
    # Sort by existing order or list index
    nodes_sorted = sorted(nodes, key=lambda x: x.get('order', 0))
    total = len(nodes_sorted)
    
    # Calculate partition sizes (approx 33% each)
    # Prioritize base levels being larger if uneven
    n_beginner = total // 3 + (1 if total % 3 > 0 else 0)
    n_intermediate = total // 3 + (1 if total % 3 > 1 else 0)
    # Rest is advanced
    
    for i, node in enumerate(nodes_sorted):
        # Assign Level
        if i < n_beginner:
            new_level = "beginner"
        elif i < n_beginner + n_intermediate:
            new_level = "intermediate"
        else:
            new_level = "advanced"
            
        node['level'] = new_level
        node['order'] = i  # Ensure strictly sequential order

        # Sublevel tags inspired by roadmap progression depth.
        if new_level == "beginner":
            phase = i / max(n_beginner, 1)
            sublevel = "B1" if phase < 0.5 else "B2"
        elif new_level == "intermediate":
            idx = i - n_beginner
            phase = idx / max(n_intermediate, 1)
            sublevel = "I1" if phase < 0.5 else "I2"
        else:
            idx = i - n_beginner - n_intermediate
            n_advanced = max(total - n_beginner - n_intermediate, 1)
            phase = idx / n_advanced
            sublevel = "A1" if phase < 0.5 else "A2"

        description = str(node.get('description', '')).strip()
        if description and not description.startswith('['):
            node['description'] = f"[{sublevel}] {description}"
        elif not description:
            node['description'] = f"[{sublevel}] Objetivos y práctica recomendada para este tema."

        if not node.get('track'):
            node['track'] = _sanitize_track(None, new_level)
        
        # Repair prerequisites:
        # Beginner: No prerequisites
        # Others: Depend on the immediate previous node (Chain structure)
        # This is a safe default for a linear roadmap
        if new_level == "beginner":
            node['prerequisites'] = []
        else:
            # Keep existing valid previous prerequisites. If absent, use chain fallback.
            existing = node.get('prerequisites', [])
            existing_valid = sorted({p for p in existing if isinstance(p, int) and 0 <= p < i})
            node['prerequisites'] = existing_valid[:2] if existing_valid else [i - 1]
            
    return nodes_sorted


# =============================================================================
# NODE CONTENT GENERATION
# =============================================================================

def generate_node_content(
    source_content: str,
    node_title: str,
    node_description: str,
    provider: str = None,
    model: str = None
) -> dict:
    """Generate detailed educational content for a specific node."""
    processed_content = truncate_content(source_content)
    search_q = quote_plus(node_title)

    prompt = f"""Genera una guía educativa accionable para "{node_title}".

RESPONDE JSON:
{{"content": "## Objetivo del nodo\\n\\n...\\n\\n## Conceptos clave\\n\\n- **Concepto**: ...\\n\\n## Plan de práctica (30-60 min)\\n\\n1. ...\\n\\n## Ejemplo aplicado\\n\\n...\\n\\n## Errores comunes\\n\\n- ...\\n\\n## Checklist de dominio\\n\\n- [ ] ...\\n\\n## Recursos recomendados (web)\\n\\n- [Recurso 1](https://...)"}}

Estructura Markdown:
- ## Headers
- **Negritas** para conceptos
- Listas con - y numeradas cuando aplique
- `código` si aplica
- Explicaciones concretas, no relleno
- Incluye SIEMPRE la sección: "## Recursos recomendados (web)"
- Incluye 3-5 enlaces reales en markdown: [texto](https://...)
- Prioriza documentación oficial y tutoriales de alta calidad
- Incluye checklist con formato markdown interactivo: - [ ] tarea

Tema: {node_title}
Contexto: {node_description}

Material:
{processed_content}

JSON:"""

    content_data = call_ai_with_retry(prompt, provider=provider, model=model)

    raw_content = str(content_data.get("content", "")).strip()
    if not raw_content:
        raw_content = "## Objetivo del nodo\n\nNo se pudo generar contenido detallado para este nodo."

    # Ensure checklist section exists with valid markdown tasks.
    if "## Checklist de dominio" not in raw_content:
        raw_content += "\n\n## Checklist de dominio\n\n- [ ] Comprendo los conceptos clave\n- [ ] Puedo aplicarlo en un ejercicio\n- [ ] Puedo explicarlo con mis palabras"

    if "- [ ]" not in raw_content and "- [x]" not in raw_content:
        raw_content += "\n\n## Checklist de dominio\n\n- [ ] Repasar teoría\n- [ ] Practicar con un ejemplo\n- [ ] Verificar resultados"

    # Ensure resources section exists with useful web links.
    if "## Recursos recomendados (web)" not in raw_content:
        raw_content += (
            "\n\n## Recursos recomendados (web)\n\n"
            f"- [Búsqueda guiada en Google: {node_title}](https://www.google.com/search?q={search_q})\n"
            f"- [Documentación en MDN relacionada](https://developer.mozilla.org/en-US/search?q={search_q})\n"
            f"- [Tutoriales en freeCodeCamp relacionados](https://www.freecodecamp.org/news/search/?query={search_q})"
        )

    content_data["content"] = raw_content
    return content_data
