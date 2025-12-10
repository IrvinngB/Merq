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
    return "\n\n".join(text_parts)


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


def generate_roadmap(content: str, title: str) -> dict:
    """
    Genera un roadmap de aprendizaje estructurado por niveles.
    Cada nodo representa un tema/concepto a investigar.
    """
    processed_content = truncate_content(content)

    prompt = f"""Eres un experto en diseño curricular y rutas de aprendizaje. Analiza el contenido y crea un roadmap educativo completo y detallado.

IMPORTANTE: Responde ÚNICAMENTE con JSON válido. Sin explicaciones ni texto adicional.

Estructura JSON requerida:
{{
  "description": "Descripción general del roadmap (2-3 oraciones)",
  "nodes": [
    {{"title": "Nombre del tema", "description": "Breve descripción de qué aprender", "level": "beginner", "order": 0, "prerequisites": []}}
  ]
}}

NIVELES (distribuir equitativamente):
- beginner: Fundamentos y conceptos básicos (4-5 nodos)
- intermediate: Aplicación práctica y profundización (4-5 nodos)  
- advanced: Temas avanzados y especialización (3-4 nodos)

REGLAS ESTRICTAS:
1. Genera entre 12-15 nodos en total
2. Cada nivel DEBE tener al menos 4 nodos
3. Los títulos deben ser concisos (3-6 palabras)
4. Las descripciones deben explicar qué se aprenderá (1-2 oraciones)
5. prerequisites: array de índices (order) de nodos que deben completarse antes
6. Los nodos beginner tienen prerequisites: []
7. Los nodos intermediate dependen de nodos beginner
8. Los nodos advanced dependen de nodos intermediate o beginner
9. Crea conexiones lógicas entre temas relacionados

EJEMPLO de nodo bien estructurado:
{{"title": "Variables y tipos de datos", "description": "Aprende a declarar variables, tipos primitivos y conversiones de datos", "level": "beginner", "order": 0, "prerequisites": []}}

Título del roadmap: {title}

Contenido a analizar:
{processed_content}

JSON:"""

    return call_ollama_with_retry(prompt)


def generate_node_content(source_content: str, node_title: str, node_description: str) -> dict:
    """
    Genera el contenido detallado de un nodo específico.
    Incluye qué investigar, recursos sugeridos y puntos clave.
    """
    processed_content = truncate_content(source_content)

    prompt = f"""Genera contenido educativo para el tema "{node_title}".

IMPORTANTE: Responde SOLO con JSON válido.

El campo "content" debe usar Markdown con:
- **Negritas** para conceptos clave
- Listas con viñetas para puntos importantes
- `código` para términos técnicos
- Secciones claras con ## headers

Formato JSON requerido:
{{"content": "## Descripción\\n\\nExplicación del tema...\\n\\n## Qué investigar\\n\\n- Punto 1\\n- Punto 2\\n\\n## Recursos sugeridos\\n\\n- Recurso 1\\n- Recurso 2\\n\\n## Conceptos clave\\n\\n- **Concepto**: explicación"}}

Tema: {node_title}
Descripción: {node_description}

Material de referencia:
{processed_content}

JSON:"""

    return call_ollama_with_retry(prompt)
