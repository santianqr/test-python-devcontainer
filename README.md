# WhatsApp AI Assistant

Una aplicación FastAPI simple que usa LangChain con OpenAI para responder mensajes de WhatsApp.

## Características

- ✅ **FastAPI** para la API REST
- ✅ **LangChain** para integración con OpenAI  
- ✅ **Respuestas optimizadas** para WhatsApp (cortas y conversacionales)
- ✅ **Configuración simple** con variables de entorno
- ✅ **Código limpio** siguiendo estándares Python 3.11+ (ruff, mypy, black)
- ✅ **Gestión de dependencias** con uv

## Requisitos

- Python 3.11+
- OpenAI API Key
- uv (gestor de paquetes)

## Instalación

1. **Instala las dependencias con uv:**
```bash
uv sync --extra dev --extra ds
```

2. **Configura las variables de entorno:**
```bash
# Opción 1: Usar el script interactivo (RECOMENDADO)
uv run python setup_env.py

# Opción 2: Crear manualmente el archivo .env
cp env_example .env
# Luego edita .env con tus credenciales reales
```

3. **Inicializa la base de datos:**
```bash
# Configuración completa automática
uv run python init_complete.py

# O paso a paso:
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

**Response:**
```json
{
  "message": "API is working!",
  "test_chat_endpoint": "/chat",
  "sample_request": {
    "message": "Hola, ¿cómo estás?",
    "sender": "user"
  }
}
```

## Pruebas

### Con curl:
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

### Con Postman:
1. **URL base:** `http://localhost:8000`
2. **Método:** `POST` para `/chat`
3. **Headers:** `Content-Type: application/json`
4. **Body:** JSON con `message` y `sender`

## Verificación de la Base de Datos

### Comprobar tablas y embeddings:
```bash
# Verificar estado completo de la BD
uv run python check_db.py

# Configurar variables de entorno
uv run python setup_env.py

# Inicialización completa
uv run python init_complete.py
```

## Desarrollo

### Herramientas de calidad de código:
```bash
# Linting
uv run ruff check .

# Type checking  
uv run mypy .

# Formateo
uv run black .
```

### Estructura del proyecto:
```
├── main.py           # Aplicación FastAPI principal
├── pyproject.toml    # Configuración del proyecto y dependencias
├── uv.lock          # Lock file de dependencias (versionado)
├── .env             # Variables de entorno (no versionado)
├── env_example      # Ejemplo de configuración
└── README.md        # Este archivo
```

## Configuración

El proyecto sigue las mejores prácticas de Python:
- **Tipos modernos**: `dict[str, str]` en lugar de `Dict[str, str]`
- **Imports organizados**: stdlib → third-party → local
- **Sin comentarios `#`**: Solo docstrings para documentación
- **Configuración en pyproject.toml**: ruff, mypy, black configurados