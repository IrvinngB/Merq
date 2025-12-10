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

    prompt = f"""Eres un experto en diseño de rutas de aprendizaje. Analiza el contenido y crea un roadmap educativo completo.

RESPONDE ÚNICAMENTE CON JSON VÁLIDO. Sin texto adicional.

Formato JSON requerido:
{{
  "description": "Descripción breve del roadmap",
  "nodes": [
    {{"title": "Tema", "description": "Qué aprenderás", "level": "beginner", "order": 0, "prerequisites": []}}
  ]
}}

ESTRUCTURA DEL ROADMAP:
- beginner (4-6 nodos): Fundamentos y conceptos básicos esenciales
- intermediate (4-6 nodos): Aplicación práctica y técnicas intermedias  
- advanced (3-5 nodos): Temas avanzados y especialización

REGLAS:
1. Total: 12-17 nodos bien distribuidos
2. Títulos concisos: 2-5 palabras máximo
3. Descripciones claras: 1 oración explicando qué se aprende
4. order: número secuencial empezando en 0
5. prerequisites: array con los "order" de nodos previos necesarios
   - beginner: siempre []
   - intermediate: [indices de 1-2 nodos beginner]
   - advanced: [indices de 1-2 nodos intermediate]

IMPORTANTE: Extrae los temas más relevantes del contenido proporcionado.

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
