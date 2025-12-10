# Guía de Instalación - Merq

## Requisitos previos

- **Docker** y **Docker Compose**
- **Git**
- **GPU NVIDIA** (opcional, mejora rendimiento de Ollama)

---

## Windows

### 1. Instalar Docker Desktop

1. Descargar desde [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
2. Ejecutar el instalador
3. Reiniciar el sistema
4. Abrir Docker Desktop y esperar a que inicie

### 2. Clonar el repositorio

```powershell
git clone https://github.com/IrvinngB/Merq.git
cd Merq
```

### 3. Configurar variables de entorno

```powershell
copy .env.example .env
```

Editar `.env` si es necesario (los valores por defecto funcionan).

### 4. Levantar los servicios

```powershell
docker compose up -d --build
```

### 5. Ejecutar migraciones

```powershell
docker compose exec api alembic upgrade head
```

### 6. Descargar modelo de IA

```powershell
docker compose exec ollama ollama pull gemma2:2b
```

### 7. Acceder a la aplicación

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

---

## Linux (Ubuntu/Debian)

### 1. Instalar Docker

```bash
# Actualizar paquetes
sudo apt update

# Instalar dependencias
sudo apt install -y ca-certificates curl gnupg

# Agregar clave GPG de Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Agregar repositorio
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Agregar usuario al grupo docker (evita usar sudo)
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Clonar el repositorio

```bash
git clone https://github.com/IrvinngB/Merq.git
cd Merq
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

### 4. Levantar los servicios

```bash
docker compose up -d --build
```

### 5. Ejecutar migraciones

```bash
docker compose exec api alembic upgrade head
```

### 6. Descargar modelo de IA

```bash
docker compose exec ollama ollama pull gemma2:2b
```

### 7. Acceder a la aplicación

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

---

## Linux con GPU NVIDIA (Opcional)

Para mejor rendimiento de Ollama:

### 1. Instalar NVIDIA Container Toolkit

```bash
# Agregar repositorio
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt update
sudo apt install -y nvidia-container-toolkit

# Configurar Docker para usar NVIDIA
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### 2. Modificar docker-compose.yml

Descomentar la sección de GPU en el servicio `ollama`:

```yaml
ollama:
  image: ollama/ollama:latest
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

---

## Comandos útiles

### Ver logs

```bash
# Todos los servicios
docker compose logs -f

# Servicio específico
docker compose logs -f api
docker compose logs -f frontend
docker compose logs -f ollama
```

### Reiniciar servicios

```bash
docker compose restart
docker compose restart api
```

### Detener servicios

```bash
docker compose down
```

### Eliminar todo (incluyendo volúmenes)

```bash
docker compose down -v
```

### Reconstruir después de cambios

```bash
docker compose up -d --build
```

---

## Solución de problemas

### Error: "Cannot connect to Docker daemon"

**Windows**: Asegúrate de que Docker Desktop esté corriendo.

**Linux**: 
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### Error: "Port already in use"

Cambiar puertos en `.env` o detener el servicio que usa el puerto:

```bash
# Ver qué usa el puerto
lsof -i :5173
lsof -i :8000

# Matar proceso
kill -9 <PID>
```

### Ollama muy lento

- Usa GPU si está disponible
- Usa un modelo más pequeño: `ollama pull gemma2:2b`
- Aumenta la RAM asignada a Docker

### Error en migraciones

```bash
# Resetear base de datos
docker compose down -v
docker compose up -d db
docker compose exec api alembic upgrade head
```

---

## Estructura de servicios

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| frontend | 5173 | Vue 3 + Vite |
| api | 8000 | FastAPI |
| db | 5432 | PostgreSQL |
| ollama | 11434 | IA Local |
