# 🗺️ Prompt Template para Generar Roadmaps Compatibles

Este documento contiene los prompts exactos que puedes usar con **Claude**, **GPT-4**, **Gemini** u otra IA para generar roadmaps compatibles con Merq cuando tienes un PDF muy grande o prefieres usar una IA externa.

---

## 📋 Flujo de Trabajo

1. **Sube tu PDF** a la IA externa (Claude, GPT, Gemini)
2. **Copia el prompt** de abajo y pégalo
3. **Copia la respuesta JSON** 
4. **Usa la API** de Merq para importar el roadmap (o créalo manualmente)

---

## 🚀 PROMPT 1: Generar Estructura del Roadmap

Copia este prompt y reemplaza `[TÍTULO DEL ROADMAP]` con el título que desees:

```
Eres un experto en diseño de rutas de aprendizaje. Analiza el contenido del documento que te proporcioné y crea un roadmap educativo completo.

RESPONDE ÚNICAMENTE CON JSON VÁLIDO. Sin texto adicional, sin explicaciones, solo el JSON.

Formato JSON requerido:
{
  "description": "Descripción breve del roadmap (1-2 oraciones)",
  "nodes": [
    {
      "title": "Nombre del Tema",
      "description": "Qué aprenderás en este tema (1 oración)",
      "level": "beginner|intermediate|advanced",
      "order": 0,
      "prerequisites": []
    }
  ]
}

ESTRUCTURA OBLIGATORIA DEL ROADMAP (MÍNIMO 3, MÁXIMO 8 nodos por nivel):

### Nivel Beginner (3-8 nodos) - OBLIGATORIO
- Fundamentos y conceptos básicos esenciales
- Lo que todo principiante necesita saber primero
- prerequisites: siempre [] (array vacío)

### Nivel Intermediate (3-8 nodos) - OBLIGATORIO
- Aplicación práctica y técnicas intermedias
- Construye sobre los fundamentos
- prerequisites: [indices de 1-2 nodos beginner relacionados]

### Nivel Advanced (3-8 nodos) - OBLIGATORIO
- Temas avanzados, especialización y casos de uso complejos
- Requiere dominio de temas intermedios
- Incluye optimización, mejores prácticas y aplicaciones avanzadas
- prerequisites: [indices de 1-2 nodos intermediate relacionados]

REGLAS CRÍTICAS:

1. OBLIGATORIO: Cada nivel DEBE tener MÍNIMO 3 nodos y MÁXIMO 8 nodos
2. Total de nodos: 9-24 bien distribuidos entre los 3 niveles
3. Títulos: Concisos, 2-5 palabras máximo
4. Descripciones: 1 oración clara explicando qué se aprende
5. order: Número secuencial empezando en 0, 1, 2, 3...
6. level: Solo puede ser "beginner", "intermediate" o "advanced" (en minúsculas)
7. prerequisites: 
   - Array de números que representan el "order" de nodos previos
   - beginner: siempre []
   - intermediate: [1-2 índices de nodos beginner]
   - advanced: [1-2 índices de nodos intermediate]

IMPORTANTE: 
- NUNCA generes menos de 3 nodos en NINGÚN nivel
- El nivel "advanced" es TAN IMPORTANTE como los otros
- Si no hay suficientes temas avanzados, genera temas de optimización, mejores prácticas o casos especiales

Título del roadmap: [TÍTULO DEL ROADMAP]

Genera el JSON:
```

---

## 📝 Ejemplo de Respuesta Esperada

```json
{
  "description": "Guía completa para aprender desarrollo web desde cero hasta nivel avanzado",
  "nodes": [
    {
      "title": "Fundamentos de HTML",
      "description": "Aprenderás la estructura básica de páginas web y etiquetas esenciales",
      "level": "beginner",
      "order": 0,
      "prerequisites": []
    },
    {
      "title": "CSS Básico",
      "description": "Dominarás estilos, selectores y diseño visual de páginas",
      "level": "beginner",
      "order": 1,
      "prerequisites": []
    },
    {
      "title": "JavaScript Fundamentos",
      "description": "Aprenderás variables, funciones y manipulación del DOM",
      "level": "beginner",
      "order": 2,
      "prerequisites": []
    },
    {
      "title": "Flexbox y Grid",
      "description": "Crearás layouts modernos y responsivos",
      "level": "intermediate",
      "order": 3,
      "prerequisites": [1]
    },
    {
      "title": "JavaScript Asíncrono",
      "description": "Manejarás Promises, async/await y peticiones HTTP",
      "level": "intermediate",
      "order": 4,
      "prerequisites": [2]
    },
    {
      "title": "React Básico",
      "description": "Construirás componentes y manejarás estado",
      "level": "intermediate",
      "order": 5,
      "prerequisites": [2, 3]
    },
    {
      "title": "APIs REST",
      "description": "Integrarás servicios externos y manejarás datos",
      "level": "advanced",
      "order": 6,
      "prerequisites": [4, 5]
    },
    {
      "title": "Testing Frontend",
      "description": "Escribirás tests unitarios y de integración",
      "level": "advanced",
      "order": 7,
      "prerequisites": [5]
    }
  ]
}
```

---

## 🔧 PROMPT 2: Generar Contenido de un Nodo

Una vez tengas el roadmap, puedes generar contenido detallado para cada nodo:

```
Genera contenido educativo detallado para el tema "[TÍTULO DEL NODO]".

RESPONDE ÚNICAMENTE CON JSON VÁLIDO.

El campo "content" debe ser Markdown bien estructurado con:
- ## Headers para secciones
- **Negritas** para conceptos importantes
- Listas con viñetas (-)
- `código` para términos técnicos si aplica

Estructura del contenido:
1. Breve introducción al tema (2-3 párrafos)
2. Conceptos clave a dominar (lista de 4-6 conceptos)
3. Pasos o puntos importantes (lista numerada)
4. Tips prácticos (2-4 tips)

Contexto del tema: [DESCRIPCIÓN DEL NODO]

Formato JSON exacto:
{
  "content": "## Introducción\n\nExplicación clara del tema...\n\n## Conceptos Clave\n\n- **Concepto 1**: explicación\n- **Concepto 2**: explicación\n\n## Puntos Importantes\n\n1. Primer punto\n2. Segundo punto\n\n## Tips Prácticos\n\n- Tip 1\n- Tip 2"
}

Genera el JSON:
```

---

## 🔌 Cómo Importar a Merq

### Opción 1: Usando la API directamente

```bash
# 1. Crear el roadmap
curl -X POST "http://localhost:8000/api/roadmaps/?creator_id=1" \
  -H "Content-Type: application/json" \
  -d '{"title": "Mi Roadmap", "description": "Descripción del roadmap"}'

# Respuesta: {"id": 1, "title": "Mi Roadmap", ...}

# 2. Crear cada nodo (reemplaza roadmap_id y datos)
curl -X POST "http://localhost:8000/api/roadmaps/1/nodes/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fundamentos de HTML",
    "description": "Aprenderás la estructura básica",
    "level": "beginner",
    "order_index": 0,
    "position_x": 0,
    "position_y": 0
  }'

# 3. Crear conexiones entre nodos
curl -X POST "http://localhost:8000/api/roadmaps/1/connections" \
  -H "Content-Type: application/json" \
  -d '{"from_node_id": 1, "to_node_id": 4}'
```

### Opción 2: Script Python de Importación

```python
import requests
import json

API_URL = "http://localhost:8000/api"
CREATOR_ID = 1  # Tu ID de usuario

def import_roadmap(json_data: dict, title: str):
    # 1. Crear roadmap
    roadmap = requests.post(
        f"{API_URL}/roadmaps/?creator_id={CREATOR_ID}",
        json={"title": title, "description": json_data.get("description", "")}
    ).json()
    
    roadmap_id = roadmap["id"]
    node_map = {}  # order -> node_id
    
    # 2. Crear nodos
    for node in json_data["nodes"]:
        created = requests.post(
            f"{API_URL}/roadmaps/{roadmap_id}/nodes/",
            json={
                "title": node["title"],
                "description": node["description"],
                "level": node["level"],
                "order_index": node["order"],
                "position_x": 0,
                "position_y": 0
            }
        ).json()
        node_map[node["order"]] = created["id"]
    
    # 3. Crear conexiones basadas en prerequisites
    for node in json_data["nodes"]:
        if node.get("prerequisites"):
            for prereq_order in node["prerequisites"]:
                if prereq_order in node_map:
                    requests.post(
                        f"{API_URL}/roadmaps/{roadmap_id}/connections",
                        json={
                            "from_node_id": node_map[prereq_order],
                            "to_node_id": node_map[node["order"]]
                        }
                    )
    
    print(f"✅ Roadmap importado: ID {roadmap_id} con {len(node_map)} nodos")
    return roadmap_id

# Uso:
with open("roadmap_generado.json", "r") as f:
    data = json.load(f)
    import_roadmap(data, "Mi Roadmap Importado")
```

---

## 📊 Tabla de Referencia Rápida

| Campo | Tipo | Valores Permitidos | Ejemplo |
|-------|------|-------------------|---------|
| `title` | string | 2-5 palabras | `"JavaScript Básico"` |
| `description` | string | 1 oración | `"Aprenderás variables y funciones"` |
| `level` | string | `beginner`, `intermediate`, `advanced` | `"beginner"` |
| `order` | number | 0, 1, 2, 3... (secuencial) | `0` |
| `prerequisites` | array | Array de números `order` | `[0, 2]` o `[]` |

---

## ⚠️ Errores Comunes a Evitar

1. **❌ No incluir texto fuera del JSON**
   ```
   Aquí está el roadmap:  ← NO
   {"description": ...}
   ```

2. **❌ Nivel incorrecto**
   ```json
   "level": "Beginner"  ← NO (debe ser minúsculas)
   "level": "beginner"  ← SÍ
   ```

3. **❌ Prerequisites en beginner**
   ```json
   {"level": "beginner", "prerequisites": [0]}  ← NO
   {"level": "beginner", "prerequisites": []}   ← SÍ
   ```

4. **❌ Order no secuencial**
   ```json
   "order": 0, "order": 2, "order": 5  ← NO
   "order": 0, "order": 1, "order": 2  ← SÍ
   ```

---

## 🎯 Tips para Mejores Resultados

1. **Sé específico con el título** - Un buen título ayuda a la IA a enfocar el contenido
2. **Revisa el JSON** - Asegúrate de que sea válido antes de importar
3. **Ajusta los prerequisites** - Si la IA no los genera bien, ajústalos manualmente para un mejor flujo
4. **Distribuye bien los nodos** - Intenta tener balance entre los 3 niveles

---

*Generado para Merq - Plataforma de Roadmaps de Aprendizaje*
