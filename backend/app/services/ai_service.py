"""
AI Service - Roadmap Generation
Business Logic Layer
- Uses ai_provider.py for connections
- Handles Prompt Engineering & Parsing
"""

import json
import re
from io import BytesIO
import pdfplumber
from .ai_provider import AIGateway

# Initialize Gateway (handles Gemini/Ollama connections)
gateway = AIGateway()

# Content limits
MAX_CONTENT_LENGTH = 25000 
MAX_SUMMARY_LENGTH = 2000
MAX_RETRIES = 3

def log_ai(msg):
    print(f"[AI SERVICE] {msg}", flush=True)

def call_ai(prompt: str, json_mode: bool = False) -> str:
    """
    Call AI using the Gateway.
    Strategies: Gemini -> Ollama (handled by Gateway)
    """
    try:
        response_text, provider_name = gateway.generate(prompt, json_mode)
        
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


def call_ai_with_retry(prompt: str) -> dict:
    """Call AI with retries for JSON parsing failures."""
    last_error = None
    
    for attempt in range(MAX_RETRIES):
        try:
            # Try with JSON mode first (Gemini native)
            response_text = call_ai(prompt, json_mode=True)
            return parse_json_response(response_text)
        except Exception as e:
            last_error = e
            # Retry without JSON mode
            try:
                response_text = call_ai(prompt, json_mode=False)
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

def generate_content_summary(content: str, roadmap_title: str, nodes_info: list[dict]) -> str:
    """
    Generate optimized summary for node content generation.
    Stored in DB instead of full content - max 2000 chars.
    """
    processed_content = truncate_content(content, max_length=5000)
    
    # Build topics list compactly
    topics = "\n".join([f"• {n.get('title', '')}" for n in nodes_info[:12]])
    
    prompt = f"""Genera un RESUMEN ESTRUCTURADO y CONCISO del contenido.

REGLAS:
- Máximo 1800 caracteres
- Usa bullet points cortos
- Incluye definiciones y conceptos clave
- NO incluyas opiniones

Temas del roadmap "{roadmap_title}":
{topics}

Contenido:
{processed_content}

RESUMEN:"""

    summary = call_ai_text(prompt)
    
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
    
    min_nodes = 3 if strict else 1
    max_nodes = 8
    
    valid = all(min_nodes <= count <= max_nodes for count in level_counts.values())
    
    return valid, level_counts


# =============================================================================
# ROADMAP GENERATION - TOON-inspired compact prompts
# =============================================================================

def generate_roadmap(content: str, title: str) -> dict:
    """
    Generate learning roadmap structured by levels.
    Uses compact prompts for token efficiency.
    """
    # Use larger context window
    processed_content = truncate_content(content)

    # Compact prompt design (TOON-inspired: less syntax, more data)
    base_prompt = f"""Analiza el contenido y genera un roadmap de aprendizaje.

RESPONDE SOLO JSON:
{{
  "description": "Descripción breve",
  "nodes": [
    {{"title": "Tema", "description": "Qué aprenderás", "level": "beginner|intermediate|advanced", "order": 0, "prerequisites": []}}
  ]
}}

ESTRUCTURA (12 nodos total):
• beginner: 4 nodos - fundamentos
• intermediate: 4 nodos - aplicación práctica  
• advanced: 4 nodos - especialización

REGLAS:
• titles: 2-5 palabras
• order: 0-11 secuencial
• prerequisites: IMPORTANTE - Cada nodo intermediate/advanced DEBE tener al menos 1 prerequisito (use el 'order' de un nodo del nivel anterior). Ejemplo: [0, 1]

Título: {title}

Contenido:
{processed_content}

JSON:"""

    # Attempt 1
    roadmap_data = call_ai_with_retry(base_prompt)
    is_valid, counts = validate_roadmap_structure(roadmap_data, strict=True)
    
    if is_valid:
        return roadmap_data
    
    # Attempt 2: More specific
    missing = [lvl for lvl, cnt in counts.items() if cnt < 3]
    
    retry_prompt = f"""Tu tarea es GENERAR EL JSON COMPLETO del roadmap.

ERROR PREVIO: Faltan nodos. Se requieren estos conteos exactos:
- beginner: 4 nodos
- intermediate: 4 nodos
- advanced: 4 nodos

GENERA EL JSON SIGUIENDO ESTA ESTRUCTURA EXACTA:
{{
  "description": "Descripción...",
  "nodes": [
    {{"title": "T1", "description": "...", "level": "beginner", "order": 0, "prerequisites": []}},
    {{"title": "T2", "description": "...", "level": "beginner", "order": 1, "prerequisites": []}},
    {{"title": "T3", "description": "...", "level": "beginner", "order": 2, "prerequisites": []}},
    {{"title": "T4", "description": "...", "level": "beginner", "order": 3, "prerequisites": []}},
    {{"title": "T5", "description": "...", "level": "intermediate", "order": 4, "prerequisites": [3]}},
    ... (hasta completar los 12 nodos)
  ]
}}

NO expliques nada. SOLO JSON.

Título: {title}
Contenido:
{processed_content[:3000]}

JSON:"""

    roadmap_data = call_ai_with_retry(retry_prompt)
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
    if len(nodes) >= 6:
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
        
        # Repair prerequisites:
        # Beginner: No prerequisites
        # Others: Depend on the immediate previous node (Chain structure)
        # This is a safe default for a linear roadmap
        if new_level == "beginner":
            node['prerequisites'] = []
        else:
            # Simple chain: depends on i-1
            node['prerequisites'] = [i - 1]
            
    return nodes_sorted


# =============================================================================
# NODE CONTENT GENERATION
# =============================================================================

def generate_node_content(source_content: str, node_title: str, node_description: str) -> dict:
    """Generate detailed educational content for a specific node."""
    processed_content = truncate_content(source_content)

    prompt = f"""Genera contenido educativo para "{node_title}".

RESPONDE JSON:
{{"content": "## Introducción\\n\\nTexto...\\n\\n## Conceptos\\n\\n- **Concepto**: explicación\\n\\n## Tips\\n\\n- Tip práctico"}}

Estructura Markdown:
- ## Headers
- **Negritas** para conceptos
- Listas con -
- `código` si aplica

Tema: {node_title}
Contexto: {node_description}

Material:
{processed_content}

JSON:"""

    return call_ai_with_retry(prompt)
