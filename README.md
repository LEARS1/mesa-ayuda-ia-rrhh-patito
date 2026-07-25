# Mesa de Ayuda IA para RR. HH. — Patito S.A.

Prototipo funcional del proyecto final del Semillero de Inteligencia Artificial. Permite realizar consultas de Recursos Humanos en lenguaje natural, recuperar información desde tres bases documentales independientes, analizar imágenes y registrar solicitudes de vacaciones o dependientes.

## Objetivo

Demostrar una arquitectura de agentes con LangChain/LangGraph y Google Gemini que:

- identifique qué especialidad debe intervenir;
- responda con información recuperada de documentos ficticios;
- consolide consultas mixtas;
- exponga agentes y fuentes utilizados;
- evite inventar información fuera del alcance;
- ejecute acciones controladas con confirmación explícita.

## Tecnologías

- Python 3.10 o superior.
- FastAPI.
- LangChain y LangGraph.
- Google Gemini mediante `langchain-google-genai`.
- `ChatGoogleGenerativeAI` para conversación y visión.
- `GoogleGenerativeAIEmbeddings` para embeddings.
- Chroma como vector store local.
- HTML, CSS y JavaScript para la interfaz.

## Arquitectura

El componente central es un agente orquestador ReAct creado con LangGraph. El orquestador selecciona una o varias herramientas especializadas según la intención y el historial de la conversación.

```text
Interfaz web / API
        |
        v
Agente Orquestador ReAct
        |
        +-- Beneficios y Compensaciones -> Chroma independiente
        +-- Políticas Internas          -> Chroma independiente
        +-- Reclutamiento/Onboarding    -> Chroma independiente
        +-- Agente de Acción            -> registro TXT
        +-- Agente Multimodal           -> Gemini con visión
```

Los tres dominios RAG se implementan como agentes lógicos especializados accesibles mediante tools. Cada uno tiene una base documental, retriever, colección Chroma y trazabilidad de fuentes independientes. La descripción ampliada está en [`docs/arquitectura.md`](docs/arquitectura.md).

## Agentes implementados

### Agente Orquestador ReAct

- Recibe la consulta.
- Usa memoria separada por `thread_id`.
- Decide qué tools invocar.
- Puede llamar varios dominios en una consulta mixta.
- Consolida la respuesta final.

### Agente de Beneficios y Compensaciones

Consulta exclusivamente `data/01_Beneficios_Compensaciones.txt` para seguros, dependientes, bonos y compensaciones.

### Agente de Políticas Internas

Consulta exclusivamente `data/02_Reglamento_Interno.txt` para vacaciones, permisos, conducta y reglamento.

### Agente de Reclutamiento y Onboarding

Consulta exclusivamente `data/03_Reclutamiento_Onboarding.txt` para selección, referidos, inducción y nuevos ingresos.

### Agente de Acción

Registra solicitudes de vacaciones e inscripción de dependientes. Antes de escribir:

- recopila campos obligatorios;
- valida fechas y anticipación mínima;
- calcula días hábiles;
- detecta duplicados;
- solicita confirmación explícita;
- genera ID único y fecha/hora;
- maneja cancelación y errores.

### Agente Multimodal

Analiza JPG, JPEG, PNG o WEBP asociados al `thread_id` mediante Gemini con visión.

## Implementación RAG

### Chunking

Los documentos son pequeños y estructurados por secciones. Se separan por párrafos usando dobles saltos de línea. La ventaja es conservar unidades semánticas legibles y fuentes fáciles de explicar. La limitación es que documentos extensos requerirían un splitter por tokens con solapamiento.

### Embeddings y vector store

Cada chunk se transforma con `GoogleGenerativeAIEmbeddings` y se almacena en una colección Chroma dedicada:

- `beneficios_compensaciones`;
- `politicas_internas`;
- `reclutamiento_onboarding`.

### Recuperación

Cada retriever usa `top-k = 4`. Este valor ofrece contexto suficiente para documentos pequeños sin enviar demasiados fragmentos al modelo. En producción debe ajustarse mediante evaluación de precisión y cobertura.

### Control de alucinaciones

El modelo recibe instrucciones de responder únicamente con el contexto recuperado. Cuando no hay información suficiente debe responder:

> No encontré información suficiente en la base documental proporcionada.

## Trazabilidad

Cada respuesta de la API puede incluir:

- agentes participantes;
- herramientas utilizadas;
- documento fuente;
- número de chunk;
- advertencias;
- tiempo de respuesta;
- cantidad de herramientas y fuentes.

## Estructura del proyecto

```text
agents/                  Agente ReAct, acción y multimodal
api/                     Modelos de entrada
config/                  Configuración y variables de entorno
core/                    Estado y constantes
data/                    Tres documentos ficticios
 docs/                    Arquitectura, pruebas, riesgos y mejoras
 rag/                     Recuperación e índices vectoriales
 services/                Reglas de negocio de solicitudes
 templates/               Interfaz web
 tests/imagenes/          Imagen ficticia de demostración
 main.py                  API FastAPI
 .env.example             Plantilla sin secretos
 requirements.txt         Dependencias
 registro_solicitudes_rrhh.txt  Evidencia del agente de acción
```

## Instalación

### 1. Crear entorno virtual

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

En Linux/macOS:

```bash
python -m venv venv
source venv/bin/activate
```

### 2. Instalar dependencias

```powershell
python -m pip install -r requirements.txt
```

### 3. Configurar secretos

Copiar `.env.example` como `.env`:

```powershell
Copy-Item .env.example .env
```

Editar `.env` y colocar la clave real:

```env
GOOGLE_API_KEY=su_clave_real
```

Nunca subir `.env` al repositorio.

### 4. Ejecutar

```powershell
python -m uvicorn main:app --reload
```

Abrir:

- Interfaz: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`

En el primer inicio se generan los índices Chroma. La carpeta `chroma_db` no debe versionarse.

## Endpoints principales

- `POST /chat`: consulta normal.
- `POST /chat-imagen`: consulta con imagen.
- `GET /solicitudes`: historial confirmado.
- `GET /solicitudes/estado/{thread_id}`: estado actual.
- `GET /solicitudes/panel/{thread_id}`: estado e historial para la interfaz.

## Ejemplos

### Consulta simple

```text
¿Qué cubre el seguro médico corporativo?
```

### Consulta mixta

```text
¿Cuántos días de vacaciones tengo, qué cubre el seguro médico y cómo funciona el programa de referidos?
```

Se espera que intervengan los agentes de Políticas, Beneficios y Reclutamiento/Onboarding.

### Solicitud de acción

```text
Quiero solicitar vacaciones.
Mi nombre es Usuario de Prueba.
Del 17 al 21 de agosto de 2026.
Mi jefe aprobador es Jefe de Prueba.
Confirmo.
```

Más casos en [`docs/ejemplos_pruebas.md`](docs/ejemplos_pruebas.md).

## Imagen de prueba

Usar:

```text
tests/imagenes/formulario_dependiente_prueba.png
```

Ejemplo:

```text
¿Está completo este formulario y qué datos faltan?
```

## Seguridad y privacidad

- La API key se carga desde `.env`.
- `.env`, `venv`, `chroma_db` y archivos temporales no se versionan.
- No deben usarse datos personales reales durante la demostración.
- Los logs deben evitar preguntas completas o documentos sensibles.
- Las imágenes de prueba son ficticias.

## Limitaciones

- Memoria conversacional en RAM.
- Persistencia de acciones mediante TXT.
- Sin autenticación ni autorización.
- Sin bloqueo transaccional para escrituras concurrentes.
- Dependencia de disponibilidad y cuota de Gemini.
- Prototipo académico, no solución productiva.

## Monitoreo propuesto

La API mide latencia, cantidad de tools y fuentes. Para una versión productiva se propone:

- callbacks para tokens y coste de Gemini;
- tasa de errores por endpoint y agente;
- precisión de recuperación con conjunto evaluado;
- feedback positivo/negativo del usuario;
- alertas por latencia y fallos de Chroma;
- anonimización y política de retención.

## Riesgos y mejoras futuras

Consultar [`docs/riesgos_mejoras.md`](docs/riesgos_mejoras.md).

## Entregables recomendados

- Código fuente en GitHub.
- README y `.env.example`.
- Tres documentos ficticios.
- Proceso reproducible de índices.
- Ejemplos de pruebas y consulta mixta.
- Imagen ficticia y TXT generado.
- Arquitectura y riesgos.
- Video de máximo 10 minutos.

## Mejora de cambio de intención

Una solicitud pendiente no bloquea las demás funciones. El sistema distingue entre:

- respuestas que completan, confirman o cancelan el borrador;
- consultas informativas de beneficios, políticas u onboarding;
- análisis de una imagen recién adjuntada.

Las consultas independientes conservan el borrador sin modificarlo. Las imágenes recién adjuntadas se envían directamente al agente multimodal para evitar que el historial transaccional cambie su intención.

## Observabilidad con Arize Phoenix

El proyecto incorpora trazabilidad opcional con Phoenix y OpenInference. Al
activar `PHOENIX_ENABLED=true`, las ejecuciones de LangChain/LangGraph se envían
a Phoenix y se agrupan por el mismo `thread_id` utilizado por la memoria del
chat.

### Ejecutar Phoenix

En una terminal:

```powershell
phoenix serve
```

En otra terminal:

```powershell
python -m uvicorn main:app --reload
```

Abrir:

- Phoenix: `http://127.0.0.1:6006`
- Aplicación: `http://127.0.0.1:8000`
- Estado de tracing: `http://127.0.0.1:8000/observabilidad/estado`

Las consultas de texto usan etiquetas `chat_texto` y las imágenes
`chat_imagen`. La metadata añadida es operativa y no incluye nombres,
documentos de identidad, rutas locales ni contenido Base64.

La guía completa está en
[`docs/observabilidad_phoenix.md`](docs/observabilidad_phoenix.md).

### Verificación

```powershell
python tests\verificacion_phoenix.py
```

Resultado esperado:

```text
OK: integración estática de Phoenix completa.
```
