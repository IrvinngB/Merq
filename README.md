# Merq — Roadmaps de Aprendizaje con IA

> Genera roadmaps interactivos de aprendizaje a partir de PDFs o texto usando IA local (Ollama).

## Descripción

**Merq** transforma documentos PDF o texto en roadmaps de aprendizaje visuales e interactivos. La IA analiza el contenido y genera:

- **Roadmap visual** con nodos conectados
- **Tres niveles** (Principiante → Intermedio → Avanzado)
- **Contenido por nodo** generado bajo demanda
- **Conexiones** que muestran prerequisitos

### Características

- **IA Local**: Usa Ollama con Gemma 2, sin APIs externas
- **Grafo interactivo**: Zoom, pan y navegación por nodos
- **Generación bajo demanda**: Contenido generado al hacer click
- **Markdown**: Formato rico con código, listas, negritas

---

## ¿Cómo funciona?

### 1. Sube un PDF o pega texto
```
📄 "Introducción a Machine Learning.pdf"
```

### 2. La IA genera el roadmap
```
🤖 Análisis del contenido
→ Extracción de temas principales
→ Organización por niveles
→ Definición de prerequisitos
```

### 3. Visualiza el grafo interactivo
```
PRINCIPIANTE
├─ Nodo 1: ¿Qué es ML?
├─ Nodo 2: Tipos de aprendizaje
└─ Nodo 3: Datos y features

INTERMEDIO
├─ Nodo 4: Regresión lineal
├─ Nodo 5: Clasificación
└─ Nodo 6: Validación

AVANZADO
├─ Nodo 7: Redes neuronales
└─ Nodo 8: Deep learning
```

### 4. Explora cada nodo
- Click en un nodo → Panel lateral con contenido
- Genera contenido detallado bajo demanda
- Markdown con formato profesional

---

## Tecnologías

### Backend
- **FastAPI** - API REST
- **PostgreSQL** - Base de datos
- **SQLAlchemy** - ORM
- **Ollama** - IA local (Gemma 2)
- **PyPDF2** - Extracción de texto

### Frontend
- **Vue 3** - Framework
- **Pinia** - Estado global
- **Tailwind CSS** - Estilos
- **Marked** - Renderizado Markdown

### Infraestructura
- **Docker Compose** - Orquestación
- **NVIDIA Container Toolkit** - GPU para Ollama

---

## Instalación

### Requisitos
- Docker y Docker Compose
- GPU NVIDIA (opcional, mejora rendimiento)

### Pasos

1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/merq.git
cd merq
```

2. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env si es necesario
```

3. Levantar servicios
```bash
docker compose up -d --build
```

4. Descargar modelo de IA
```bash
docker compose exec ollama ollama pull gemma2:2b
```

5. Acceder a la aplicación
- Frontend: http://localhost:5173
- API: http://localhost:8000/docs

---

## Uso

1. **Registrarse** en la plataforma
2. **Crear roadmap** → Subir PDF o pegar texto
3. **Esperar generación** (~1-2 minutos)
4. **Explorar** el grafo interactivo
5. **Click en nodos** para ver/generar contenido

---

## Estructura del proyecto

```
merq/
├── backend/
│   ├── app/
│   │   ├── models/       # Modelos SQLAlchemy
│   │   ├── routers/      # Endpoints API
│   │   ├── services/     # Lógica de negocio
│   │   └── core/         # Configuración
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/          # Clientes API
│   │   ├── components/   # Componentes Vue
│   │   ├── stores/       # Pinia stores
│   │   └── views/        # Vistas
│   └── package.json
└── docker-compose.yml
```

---

## API Endpoints

### Roadmaps
- `GET /roadmaps/` - Listar roadmaps
- `GET /roadmaps/{id}` - Obtener roadmap con nodos
- `POST /roadmaps/` - Crear roadmap
- `DELETE /roadmaps/{id}` - Eliminar roadmap

### Nodos
- `GET /roadmaps/{id}/nodes/` - Listar nodos
- `PATCH /roadmaps/{id}/nodes/{node_id}` - Actualizar nodo

### IA
- `POST /ai/generate-roadmap` - Generar roadmap desde archivo
- `POST /ai/nodes/{id}/generate-content` - Generar contenido de nodo

---

## Licencia

Proyecto académico con fines educativos.
# Merq
