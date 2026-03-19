# Merq — Roadmaps de Aprendizaje con IA

> Genera roadmaps de aprendizaje interactivos y personalizados a partir de PDFs o texto usando IA local (Ollama). Sin APIs externas, sin costos recurrentes.

## 📋 Tabla de contenidos

- [Descripción](#descripción)
- [Características](#características)
- [Tecnologías](#tecnologías)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Estructura del proyecto](#estructura-del-proyecto)
- [API Endpoints](#api-endpoints)
- [Configuración](#configuración)
- [Desarrollo](#desarrollo)
- [Solución de problemas](#solución-de-problemas)

## 📚 Descripción

**Merq** transforma documentos PDF o texto en roadmaps de aprendizaje visuales, interactivos y personalizados. La IA analiza el contenido y genera:

- **Roadmap visual con grafo interactivo** - Zoom, pan y navegación intuitiva por nodos
- **Tres niveles de aprendizaje** - Principiante → Intermedio → Avanzado organizados jerárquicamente
- **Contenido bajo demanda** - Explicaciones detalladas generadas al hacer click en cada nodo
- **Prerequisitos y conexiones** - Visualiza dependencias entre temas automáticamente
- **Markdown enriquecido** - Código, listas, imágenes, negritas y todos los estilos

### Características principales

✨ **IA Local**: Usa Ollama con Gemma 2 7B, sin dependencia de APIs externas  
🎨 **Interfaz intuitiva**: Grafo interactivo con zoom, pan y selección de nodos  
⚡ **Generación bajo demanda**: Contenido generado dinámicamente al navegar  
📝 **Formato rich**: Markdown con código resaltado, ejemplos y referencias  
🔐 **Privacidad**: Todos los datos procesados localmente  
🚀 **Escalable**: Docker Compose para fácil deployment

## 🔄 Flujo de uso

### 1. Carga de contenido
Sube un PDF o pega texto directamente en la plataforma:
- PDFs: Extrae automáticamente todo el texto
- Texto plano: Analiza directamente el contenido

### 2. Generación de roadmap
La IA analiza el contenido y genera:
```
📊 Análisis → Extracción de temas → Organización por niveles → Mapeo de dependencias
```

Ejemplo de estructura generada:
```
NIVEL: PRINCIPIANTE
├─ Conceptos fundamentales: ¿Qué es Machine Learning?
├─ Tipos de aprendizaje: Supervisado vs No supervisado
└─ Preparación de datos: Features y etiquetas

NIVEL: INTERMEDIO
├─ Regresión lineal: Predicción de valores continuos
├─ Clasificación: Logística y árboles de decisión
└─ Validación cruzada: Evaluación de modelos

NIVEL: AVANZADO
├─ Redes neuronales: Arquitecturas y backpropagation
└─ Deep learning: CNNs, RNNs y transformers
```

### 3. Visualización interactiva
- **Grafo visual** con zoom, pan y selección de nodos
- **Colores por nivel** para identificar rápidamente dificultad
- **Líneas de conexión** que muestran prerequisitos

### 4. Exploración de nodos
- Click en nodo → Abre panel lateral con contenido
- Genera explicaciones detalladas bajo demanda
- Markdown formateado con ejemplos de código

## 🛠️ Tecnologías

### Backend (Python)
| Tecnología | Uso |
|-----------|-----|
| **FastAPI** | Framework REST API moderno con validación automática |
| **PostgreSQL** | Base de datos relacional con soporte JSONB |
| **SQLAlchemy** | ORM para consultas seguras y migraciones |
| **Alembic** | Versionado de esquema de base de datos |
| **Ollama** | Ejecución local de modelos LLM (Gemma 2 7B) |
| **PyPDF2** | Extracción de texto desde archivos PDF |
| **Pydantic** | Validación de datos y serialización |

### Frontend (Vue 3)
| Tecnología | Uso |
|-----------|-----|
| **Vue 3** | Framework reactivo con Composition API |
| **TypeScript** | Type safety en JavaScript |
| **Pinia** | State management centralizado |
| **Tailwind CSS** | Estilos utilitarios y responsive design |
| **Vite** | Build tool ultrarrápido |
| **Marked** | Renderizado de Markdown |
| **D3.js / Vis.js** | Visualización de grafos interactivos |

### Infraestructura
| Tecnología | Uso |
|-----------|-----|
| **Docker** | Containerización de servicios |
| **Docker Compose** | Orquestación local |
| **NVIDIA Container Toolkit** | Aceleración GPU para Ollama (opcional) |
| **PostgreSQL Container** | Base de datos versionada |

---

## 📋 Requisitos

**Mínimos:**
- Docker 20.10+
- Docker Compose 2.0+
- 8GB RAM
- 10GB espacio en disco (para modelo Gemma 2)

**Recomendados:**
- GPU NVIDIA con CUDA (mejora rendimiento 5-10x)
- 16GB RAM
- SSD con 30GB disponibles

**Sistemas soportados:**
- Linux (Ubuntu 20.04+, Debian)
- macOS (Intel/Apple Silicon)
- Windows 11+ (con WSL 2)

## 🚀 Instalación

### Paso 1: Clonar repositorio
```bash
git clone https://github.com/tu-usuario/merq.git
cd merq
```

### Paso 2: Variables de entorno
```bash
cp .env.example .env
```
Edita `.env` según tu configuración:
```env
# Backend
DATABASE_URL=postgresql://user:password@db:5432/merq
OLLAMA_BASE_URL=http://ollama:11434
CORS_ORIGINS=["http://localhost:5173"]

# Frontend
VITE_API_URL=http://localhost:8000

# Opcional: NVIDIA GPU
CUDA_VISIBLE_DEVICES=0
```

### Paso 3: Levantar servicios
```bash
# Build y start en background
docker compose up -d --build

# Verificar que todos los servicios corren
docker compose ps
```

Espera 30-60 segundos para que PostgreSQL esté listo.

### Paso 4: Descargar modelo de IA
```bash
# Descargar Gemma 2 7B (requiere ~5GB)
docker compose exec ollama ollama pull gemma2:7b

# Verificar que está disponible
docker compose exec ollama ollama list
```

### Paso 5: Acceder a la aplicación
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Paso 6: Crear usuario y base de datos
```bash
# Ejecutar migraciones Alembic
docker compose exec backend alembic upgrade head

# Crear usuario admin (opcional)
docker compose exec backend python -c "from app.core.security import create_admin; create_admin()"
```

✅ **¡Listo!** Accede a http://localhost:5173 y registrate.


---

## 📖 Uso

### Workflow Típico

1. **Registrarse** - Crea una cuenta en la plataforma
   ```
   Email: usuario@example.com
   Contraseña: (segura)
   ```

2. **Crear roadmap** - Sube PDF o pega texto
   - Opción 1: Cargar archivo PDF
   - Opción 2: Pegar texto directamente
   - Máximo 10MB de contenido

3. **Esperar generación** (~1-2 minutos según contenido)
   - La IA analiza el contenido
   - Genera estructura de temas
   - Crea conexiones entre nodos
   - Mostrará barra de progreso

4. **Explorar grafo interactivo**
   - Zoom con rueda del ratón
   - Pan: arrastra con clic central
   - Click en nodo: selecciona y muestra detalles

5. **Generar contenido detallado**
   - Click en nodo → Panel lateral se abre
   - Contenido se genera bajo demanda
   - Markdown formateado con ejemplos

### Atajos de Teclado
| Tecla | Acción |
|-------|--------|
| `Ctrl+Scroll` | Zoom in/out |
| `Espacio + Drag` | Pan (aunque también con clic central) |
| `Escape` | Deseleccionar nodo |
| `Número` | Cambiar a nivel (1=Principiante, 2=Intermedio, 3=Avanzado) |

---

## 📁 Estructura del proyecto

```
merq/
├── backend/
│   ├── app/
│   │   ├── models/           # Modelos SQLAlchemy (User, Roadmap, Node, etc)
│   │   ├── routers/          # Endpoints API
│   │   │   ├── ai.py         # Generación de roadmaps y contenido
│   │   │   ├── auth.py       # Autenticación y autorización
│   │   │   ├── roadmaps.py   # CRUD de roadmaps
│   │   │   └── ...
│   │   ├── services/         # Lógica de negocio
│   │   │   ├── ai_service.py         # Integración con Ollama
│   │   │   ├── roadmap_service.py    # Lógica de roadmaps
│   │   │   └── ...
│   │   ├── schemas/          # Validación Pydantic
│   │   └── core/
│   │       ├── config.py     # Variables de entorno
│   │       ├── database.py   # Conexión PostgreSQL
│   │       └── security.py   # JWT y hashing
│   ├── requirements.txt      # Dependencias Python
│   ├── alembic/              # Migraciones de BD
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/              # Clientes API (Axios)
│   │   ├── components/
│   │   │   ├── layout/       # Header, Sidebar
│   │   │   ├── roadmap/      # Grafo, nodos
│   │   │   └── common/       # Reutilizables
│   │   ├── stores/           # Pinia (auth, roadmaps)
│   │   ├── views/            # Vistas principales
│   │   ├── types/            # TypeScript interfaces
│   │   ├── composables/      # Hooks reutilizables
│   │   └── router/           # Rutas Vue Router
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml        # Orquestación servicios
├── .env.example              # Variables de entorno
└── README.md
```

---

## 🔌 API Endpoints

La API está documentada en http://localhost:8000/docs (Swagger) o http://localhost:8000/redoc (ReDoc)

### Autenticación
- `POST /auth/register` - Registrar nuevo usuario
- `POST /auth/login` - Login (retorna JWT token)
- `POST /auth/refresh` - Renovar token
- `POST /auth/logout` - Logout

### Roadmaps
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/roadmaps/` | Listar todos los roadmaps del usuario |
| `POST` | `/roadmaps/` | Crear nuevo roadmap |
| `GET` | `/roadmaps/{id}` | Obtener roadmap con todos sus nodos |
| `PATCH` | `/roadmaps/{id}` | Actualizar metadatos de roadmap |
| `DELETE` | `/roadmaps/{id}` | Eliminar roadmap y todos sus nodos |

### Nodos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/roadmaps/{id}/nodes/` | Listar nodos de un roadmap |
| `GET` | `/roadmaps/{id}/nodes/{node_id}` | Obtener nodo específico |
| `PATCH` | `/roadmaps/{id}/nodes/{node_id}` | Actualizar nodo |
| `DELETE` | `/roadmaps/{id}/nodes/{node_id}` | Eliminar nodo |

### Generación con IA
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/ai/generate-roadmap` | Generar roadmap desde PDF/texto |
| `POST` | `/ai/nodes/{id}/generate-content` | Generar contenido detallado para nodo |
| `POST` | `/ai/nodes/{id}/regenerate` | Regenerar contenido de nodo |

### Usuarios
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/users/me` | Obtener perfil del usuario actual |
| `PATCH` | `/users/me` | Actualizar perfil |
| `DELETE` | `/users/me` | Eliminar cuenta de usuario |

---

## ⚙️ Configuración

### Variables de entorno principales

```env
# DATABASE
DATABASE_URL=postgresql://user:password@db:5432/merq

# SECURITY
SECRET_KEY=your-secret-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OLLAMA
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=gemma2:7b

# CORS
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# LOGGING
LOG_LEVEL=INFO
```

### Configuración de Ollama

Para usar un modelo diferente:
```bash
# Descargar modelo alternativo
docker compose exec ollama ollama pull mistral:latest

# Actualizar .env
OLLAMA_MODEL=mistral:latest
```

### Base de datos

Para conectarse directamente a PostgreSQL:
```bash
docker compose exec db psql -U merq
```

---

## 👨‍💻 Desarrollo

### Setup local sin Docker

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Ejecutar servicios en desarrollo

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Ollama (o usar contenedor Docker)
ollama serve
```

### Ejecutar pruebas

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run test
npm run test:unit
```

### Linting y formateo

```bash
# Backend
cd backend
flake8 app/
black app/

# Frontend
cd frontend
npm run lint
npm run format
```

### Crear nueva migración de BD

```bash
cd backend
alembic revision --autogenerate -m "descripción del cambio"
alembic upgrade head
```

---

## 🐛 Solución de problemas

### Problema: "Error de conexión a PostgreSQL"
**Solución:**
```bash
# Verificar que el contenedor está corriendo
docker compose ps

# Ver logs de la BD
docker compose logs db

# Si sigue fallando, reiniciar
docker compose down
docker compose up -d --build
sleep 30  # Esperar a que inicie PostgreSQL
```

### Problema: "Ollama no responde / Timeout"
**Solución:**
```bash
# Verificar que Ollama está funcionando
docker compose exec ollama ollama list

# Reset de Ollama
docker compose restart ollama

# Ver logs
docker compose logs ollama
```

### Problema: "Puerto 8000 o 5173 ya en uso"
**Solución:**
```bash
# Cambiar puertos en .env o docker-compose.yml
# O terminar proceso que ocupa el puerto:
# En Windows:
netstat -ano | findstr :8000
taskkill /PID <PIDNUMBER> /F

# En Linux/Mac:
lsof -i :8000
kill -9 <PID>
```

### Problema: "GPU no se detecta en Ollama"
**Solución:** Instalar NVIDIA Container Toolkit y reiniciar Docker daemon
```bash
# Verificar GPU
docker compose exec ollama nvidia-smi

# Si no aparece, revisar docker-compose.yml y confirmar runtime: nvidia
```

### Problema: "Error de CORS desde frontend"
**Solución:**
```env
# Actualizar .env
CORS_ORIGINS=["http://localhost:5173"]  # Ajusta según tu puerto
```

### Problema: "Modelo Gemma 2 requiere demasiada RAM"
**Solución:** Usar modelo más pequeño
```bash
# Usar Mistral (más ligero)
docker compose exec ollama ollama pull mistral:7b

# Actualizar .env
OLLAMA_MODEL=mistral:7b
```

---

## 📚 Documentación adicional

- [Documentación API](http://localhost:8000/docs) - Swagger UI interactivo
- [IMPLEMENTACION_PROVIDERS.md](./IMPLEMENTACION_PROVIDERS.md) - Detalles de integración IA
- [Postman Collection](./postman/) - Ejemplos de requests (si disponible)

---

## 👥 Contribuciones

Este es un proyecto académico. Para reportar bugs o sugerir features, abre un issue en GitHub.

---

## 📄 Licencia

Proyecto académico con fines educativos.
