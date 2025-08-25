# WhatsApp AI Assistant

Una aplicación FastAPI avanzada que usa LangChain con OpenAI para responder mensajes de WhatsApp con memoria conversacional y base de conocimientos vectorial.

## Características

- ✅ **FastAPI** para la API REST
- ✅ **LangChain** para integración con OpenAI  
- ✅ **PostgreSQL + pgvector** para persistencia y búsqueda vectorial
- ✅ **Memoria conversacional** persistente por chat
- ✅ **Base de conocimientos** con embeddings para RAG
- ✅ **Herramientas personalizadas** para gestión de propiedades
- ✅ **Configuración automática** con scripts de inicialización
- ✅ **DevContainer** con PostgreSQL incluido
- ✅ **Código limpio** siguiendo estándares Python 3.11+ (ruff, mypy, black)
- ✅ **Gestión de dependencias** con uv

## Requisitos

- Docker (para devcontainer)
- OpenAI API Key
- uv (gestor de paquetes) - se instala automáticamente

## Instalación

### Opción 1: DevContainer (Recomendado)

1. **Abre el proyecto en VS Code** y acepta abrir en DevContainer
2. **Configura tu entorno:**
```bash
# Configuración automática completa
uv run python init_complete.py

# O paso a paso:
uv run python setup_env.py  # Configurar .env
uv run python init_db.py    # Inicializar base de datos
```

### Opción 2: Instalación Local

1. **Instala PostgreSQL** con extensión pgvector
2. **Instala las dependencias:**
```bash
uv sync --extra dev --extra ds
```
3. **Configura PostgreSQL:**
```sql
CREATE DATABASE whatsapp_ai;
CREATE EXTENSION vector;
```
4. **Configura variables de entorno:**
```bash
cp env_example .env
# Edita .env con tu configuración de PostgreSQL y OpenAI API key
```
5. **Inicializa la base de datos:**
```bash
uv run python init_db.py
```

## Uso

1. **Ejecuta la aplicación:**
```bash
uv run python main.py
```

2. **La API estará disponible en:** `http://localhost:8000`

3. **Documentación automática:** `http://localhost:8000/docs`

## Endpoints

### 🏠 GET `/`
Información básica de la API.

**Response:**
```json
{
  "message": "WhatsApp AI Assistant API",
  "status": "active",
  "endpoints": "/chat, /health"
}
```

### 💬 POST `/chat`
**Endpoint principal** - Envía un mensaje y recibe una respuesta de la IA.

**Request:**
```json
{
  "message": "Hola, ¿cómo estás?",
  "sender": "user"
}
```

**Response:**
```json
{
  "response": "¡Hola! Muy bien, gracias. ¿Y tú? ¿Qué tal tu día?",
  "model_used": "gpt-3.5-turbo",
  "success": true
}
```

### 🏥 GET `/health`
Verifica el estado de la aplicación y la conexión con OpenAI.

**Response:**
```json
{
  "status": "healthy",
  "openai": "connected"
}
```

### 🧪 GET `/test`
Endpoint simple para probar que la API funciona.

## Arquitectura

### Base de Datos
- **PostgreSQL 15** con extensión **pgvector**
- **Tablas principales:**
  - `conversations`: Historial de conversaciones por chat
  - `business_knowledge`: Base de conocimientos con embeddings vectoriales

### Funcionalidades Avanzadas
- **🧠 Memoria Conversacional**: Cada chat mantiene su propio historial
- **🔍 RAG (Retrieval Augmented Generation)**: Búsqueda semántica en base de conocimientos
- **🛠️ Herramientas Personalizadas**: Sistema extensible de tools para LangChain
- **📊 Embeddings**: Vectorización automática con OpenAI embeddings

### DevContainer
- **PostgreSQL** pre-configurado y listo para usar
- **Scripts de inicialización** automática
- **Extensiones VS Code** optimizadas para el desarrollo

## Scripts Disponibles

### `setup_env.py`
Configuración interactiva del entorno (.env y OpenAI API key)

### `init_db.py`
Inicialización completa de la base de datos con:
- Verificación de conectividad a PostgreSQL
- Creación de tablas y extensiones
- Configuración de índices vectoriales
- Datos de ejemplo

### `init_complete.py`
Configuración completa automática (setup_env + init_db)

## Desarrollo

### Estructura del Proyecto
```
├── .devcontainer/          # Configuración DevContainer
│   ├── devcontainer.json   # Configuración VS Code
│   ├── docker-compose.yml  # PostgreSQL + App
│   └── init-scripts/       # Scripts SQL de inicialización
├── database.py             # Modelos SQLAlchemy
├── vector_store.py         # Gestión de embeddings
├── memory.py               # Memoria conversacional
├── tools.py                # Herramientas personalizadas
├── main.py                 # Aplicación FastAPI
└── init_*.py              # Scripts de configuración
```

## Verificación

### Comprobar PostgreSQL
```bash
# Verificar conexión a la base de datos
uv run python -c "from database import test_connection; print(test_connection())"
```

### Probar la API
```bash
# Prueba básica
curl http://localhost:8000/test

# Verificar salud
curl http://localhost:8000/health

# Enviar mensaje
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola, ¿cómo estás?", "sender": "user"}'
```

## Solución de Problemas

### PostgreSQL no se conecta
```bash
# Verificar que PostgreSQL esté corriendo
docker ps

# Reiniciar devcontainer si es necesario
# En VS Code: Ctrl+Shift+P → "Rebuild Container"
```

### Error con pgvector
```bash
# El script de inicialización instala pgvector automáticamente
# Si hay problemas, verificar los logs:
docker logs <postgres_container_id>
```

### Error con OpenAI API
```bash
# Verificar que la API key esté configurada
grep OPENAI_API_KEY .env

# Probar conexión:
uv run python -c "import openai; print('OpenAI OK')"
```

## Desarrollo

### Herramientas de calidad:
```bash
# Linting y formateo
uv run ruff check .
uv run black .
uv run mypy .
```

### Variables de entorno importantes:
- `DATABASE_URL`: Conexión a PostgreSQL
- `OPENAI_API_KEY`: Clave API de OpenAI
- `OPENAI_MODEL`: Modelo de chat (default: gpt-3.5-turbo)
- `OPENAI_EMBEDDING_MODEL`: Modelo de embeddings (default: text-embedding-3-small)