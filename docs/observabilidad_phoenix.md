# Observabilidad con Arize Phoenix

Phoenix se integra como una capa opcional sobre LangChain/LangGraph. No reemplaza
la interfaz, Chroma ni el panel de solicitudes. Registra trazas para analizar:

- llamadas al modelo Gemini;
- decisiones del agente ReAct;
- herramientas invocadas;
- recuperación RAG;
- latencia y consumo de tokens reportado por el proveedor;
- errores y secuencias de ejecución;
- sesiones agrupadas por `thread_id`.

## Arquitectura de ejecución

```text
Terminal 1: phoenix serve
             |
             | OTLP HTTP
             v
Terminal 2: FastAPI + LangGraph + Gemini + Chroma
```

Phoenix se inicializa antes de los imports de LangChain mediante
`observability/phoenix_config.py`. La instrumentación es opcional y tolerante a
fallos: si Phoenix no está instalado, está deshabilitado o el colector no está
disponible, la aplicación principal continúa funcionando.

## Instalación

```powershell
python -m pip install -r requirements.txt
```

## Configuración

En `.env`:

```env
PHOENIX_ENABLED=true
PHOENIX_PROJECT_NAME=mesa-ayuda-rrhh-patito
PHOENIX_COLLECTOR_ENDPOINT=http://127.0.0.1:6006
PHOENIX_PROTOCOL=http/protobuf
```

Para ejecutar sin Phoenix:

```env
PHOENIX_ENABLED=false
```

## Inicio local

Terminal 1:

```powershell
phoenix serve
```

Phoenix queda disponible normalmente en `http://127.0.0.1:6006`.

Terminal 2:

```powershell
python -m uvicorn main:app --reload
```

La aplicación queda en `http://127.0.0.1:8000`.

## Estado de la integración

Puede consultarse sin exponer credenciales:

```text
GET http://127.0.0.1:8000/observabilidad/estado
```

Respuesta esperada:

```json
{
  "habilitado": true,
  "inicializado": true,
  "proyecto": "mesa-ayuda-rrhh-patito",
  "collector_endpoint": "http://127.0.0.1:6006",
  "protocolo": "http/protobuf",
  "error": null
}
```

## Sesiones y etiquetas

Cada petición utiliza el `thread_id` como `session_id` en Phoenix. Así se pueden
agrupar todos los turnos de una conversación. Se añaden etiquetas operativas:

- `chat_texto`, `texto`, `agente-react` para `/chat`;
- `chat_imagen`, `multimodal`, `gemini-vision` para `/chat-imagen`.

La metadata contiene únicamente canal, endpoint, presencia de imagen y MIME.
No se agregan nombres, documentos de identidad, preguntas completas, rutas del
equipo ni imágenes en Base64.

## Pruebas recomendadas

1. Consulta RAG simple de beneficios.
2. Consulta mixta con los tres dominios.
3. Solicitud de vacaciones con confirmación.
4. Imagen de formulario incompleto.
5. Pregunta fuera del alcance.
6. Cambio de intención mientras existe una solicitud pendiente.

En Phoenix se debe comprobar:

- tool correcta;
- cantidad de llamadas al modelo;
- fuentes y retriever usados;
- latencia por span;
- errores;
- agrupación por sesión;
- que imagen y acción no se mezclen incorrectamente.

## Costos

Phoenix puede mostrar costos cuando reconoce el modelo o cuando se configura un
precio personalizado en **Settings > Models**. Los precios cambian con el
tiempo; deben verificarse en la documentación oficial de Google antes de
configurarlos. Las trazas anteriores normalmente no se recalculan al añadir un
precio después.

## Limitaciones

- Phoenix local debe ejecutarse como proceso separado.
- La telemetría aumenta ligeramente el consumo de recursos.
- El contenido de prompts y respuestas puede aparecer en las trazas; para una
  versión productiva se deben aplicar políticas de enmascaramiento y retención.
- `uvicorn --reload` crea procesos nuevos; cada proceso inicializa su propio
  tracer de forma esperada.
