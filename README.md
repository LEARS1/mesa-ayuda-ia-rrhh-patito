# Mesa de Ayuda IA para RR. HH. — Patito S.A.

Prototipo funcional desarrollado para el proyecto final del **Semillero de Inteligencia Artificial**. La aplicación permite realizar consultas de Recursos Humanos en lenguaje natural, recuperar información desde tres bases documentales independientes, analizar imágenes y registrar solicitudes de vacaciones o inscripción de dependientes.

---

## 📌 Información de entrega

### 🔗 Repositorio público

**GitHub:** [https://github.com/LEARS1/mesa-ayuda-ia-rrhh-patito](https://github.com/LEARS1/mesa-ayuda-ia-rrhh-patito)

> El repositorio debe mantenerse configurado como **público** durante el proceso de evaluación.

### 🎥 Video de demostración

▶️ **[Ver video de demostración del proyecto](https://drive.google.com/file/d/1pw_crC4tPk6fZSQDKzxzNOxKIGbKgaq1/view?usp=sharing)**

**Duración máxima requerida:** 10 minutos.

El video presenta:

- arquitectura general y papel de LangChain/LangGraph;
- configuración de los tres agentes RAG;
- embeddings de Google Gemini e índices Chroma independientes;
- decisión del agente orquestador;
- consulta simple y consulta mixta;
- agente multimodal;
- agente de acción con validación y registro;
- control de alucinaciones;
- observabilidad con Arize Phoenix;
- riesgos, limitaciones y mejoras futuras.

### 👥 Integrantes

> Solo las personas mencionadas a continuación participaron en el desarrollo del proyecto.

- Israel Onofre
- Dolores Guevara

## 🎯 Objetivo

Demostrar una arquitectura de agentes con LangChain/LangGraph y Google Gemini que:

- identifique qué especialidad debe intervenir;
- responda con información recuperada de documentos ficticios;
- consolide consultas mixtas;
- muestre los agentes y las fuentes utilizadas;
- evite inventar información fuera del alcance;
- procese imágenes de documentos de RR. HH.;
- ejecute acciones controladas con validación y confirmación explícita;
- permita observar trazas, latencia, herramientas y errores mediante Phoenix.

---

## 🧠 Explicación sencilla del proyecto

El sistema funciona como una oficina virtual de Recursos Humanos:

- la **interfaz web** es la ventanilla de atención;
- **FastAPI** recibe la pregunta del usuario;
- el **orquestador** actúa como coordinador;
- los **agentes especializados** son empleados expertos en distintos temas;
- los **documentos TXT** son los manuales internos;
- **Chroma** es el archivador inteligente;
- **Gemini** interpreta la pregunta y redacta la respuesta;
- el **agente multimodal** revisa imágenes;
- el **agente de acción** registra solicitudes;
- **Phoenix** permite observar qué ocurrió dentro del sistema.

---

## 🛠️ Tecnologías utilizadas

- Python 3.10 o superior.
- FastAPI.
- LangChain.
- LangGraph.
- Google Gemini mediante `langchain-google-genai`.
- `ChatGoogleGenerativeAI` para conversación y visión.
- `GoogleGenerativeAIEmbeddings` para embeddings.
- Chroma como vector store local.
- Arize Phoenix y OpenInference para observabilidad.
- HTML, CSS y JavaScript para la interfaz.
- Git y GitHub para control de versiones y publicación.

---

## 🏗️ Arquitectura

El componente central es un agente orquestador ReAct. Este analiza la intención, consulta el historial de la conversación y selecciona una o varias herramientas especializadas.

```text
Usuario
  |
  v
Interfaz web / API FastAPI
  |
  v
Agente Orquestador ReAct
  |
  +-- Agente de Beneficios y Compensaciones
  |      +-- Documento propio
  |      +-- Embeddings Gemini
  |      +-- Colección Chroma independiente
  |
  +-- Agente de Políticas Internas
  |      +-- Documento propio
  |      +-- Embeddings Gemini
  |      +-- Colección Chroma independiente
  |
  +-- Agente de Reclutamiento y Onboarding
  |      +-- Documento propio
  |      +-- Embeddings Gemini
  |      +-- Colección Chroma independiente
  |
  +-- Agente Multimodal
  |      +-- Gemini con visión
  |
  +-- Agente de Acción
         +-- Validación
         +-- Confirmación
         +-- Registro TXT

Todas las ejecuciones pueden enviarse a Arize Phoenix.
```

La descripción técnica ampliada está disponible en [`docs/arquitectura.md`](docs/arquitectura.md).

---

## 🤖 Agentes implementados

### Agente Orquestador ReAct

- recibe la consulta;
- mantiene memoria separada por `thread_id`;
- clasifica la intención;
- decide qué herramientas invocar;
- puede llamar varios agentes en una consulta mixta;
- detecta imágenes;
- detecta solicitudes de acción;
- consolida la respuesta final;
- muestra agentes y fuentes participantes.

### Agente de Beneficios y Compensaciones

Consulta exclusivamente:

```text
data/01_Beneficios_Compensaciones.txt
```

Responde sobre:

- seguro médico;
- dependientes;
- bonos;
- beneficios;
- compensaciones.

### Agente de Políticas Internas

Consulta exclusivamente:

```text
data/02_Reglamento_Interno.txt
```

Responde sobre:

- vacaciones;
- permisos;
- conducta;
- reglamento interno;
- políticas laborales.

### Agente de Reclutamiento y Onboarding

Consulta exclusivamente:

```text
data/03_Reclutamiento_Onboarding.txt
```

Responde sobre:

- procesos de selección;
- programa de referidos;
- onboarding;
- inducción;
- nuevos ingresos.

### Agente Multimodal

Analiza imágenes JPG, JPEG, PNG o WEBP mediante Gemini con visión.

Puede:

- identificar campos;
- extraer información visible;
- detectar datos faltantes;
- validar formularios ficticios de RR. HH.

### Agente de Acción

Registra solicitudes de vacaciones o inscripción de dependientes.

Antes de escribir:

- recopila los campos obligatorios;
- solicita los datos faltantes;
- valida fechas y anticipación;
- calcula días hábiles;
- detecta duplicados;
- presenta un resumen;
- solicita confirmación explícita;
- genera un identificador único;
- guarda fecha y hora;
- maneja cancelaciones y errores.

El registro se almacena en:

```text
registro_solicitudes_rrhh.txt
```

---

## 📚 Implementación RAG

### Chunking

Los documentos ficticios son pequeños y están organizados por secciones. Se dividen por párrafos utilizando dobles saltos de línea.

Ventajas:

- conserva unidades semánticas legibles;
- facilita explicar las fuentes;
- reduce el contexto innecesario.

Limitación:

- documentos extensos requerirían un divisor por tokens con solapamiento.

### Embeddings

Cada fragmento se transforma mediante:

```python
GoogleGenerativeAIEmbeddings
```

Los embeddings representan el significado del texto en forma numérica.

### Vector store

Se utiliza Chroma con una colección independiente por dominio:

- `beneficios_compensaciones`;
- `politicas_internas`;
- `reclutamiento_onboarding`.

### Recuperación

Cada retriever utiliza:

```text
top-k = 4
```

Esto permite recuperar hasta cuatro fragmentos relevantes por consulta.

### Control de alucinaciones

El modelo debe responder únicamente con el contexto recuperado.

Cuando la información no existe, responde:

> No encontré información suficiente en la base documental proporcionada.

---

## 🔎 Trazabilidad

Cada respuesta puede incluir:

- agentes participantes;
- herramientas utilizadas;
- documento fuente;
- número o contenido del chunk;
- advertencias;
- tiempo de respuesta;
- cantidad de fuentes;
- cantidad de herramientas ejecutadas.

---

## 📁 Estructura del proyecto

```text
agents/                         Agentes ReAct, acción y multimodal
api/                            Modelos y componentes de API
config/                         Configuración y variables de entorno
core/                           Estado, constantes y memoria
data/                           Tres documentos ficticios
docs/                           Arquitectura, pruebas, riesgos y Phoenix
observability/                  Configuración de Arize Phoenix
rag/                            Embeddings, recuperación e índices
services/                       Reglas de negocio de solicitudes
templates/                      Interfaz web
tests/                          Pruebas automáticas
tests/imagenes/                 Imagen ficticia de demostración
uploads/                        Cargas temporales
utils/                          Funciones auxiliares
main.py                         Aplicación FastAPI
.env.example                    Plantilla sin secretos
.gitignore                      Archivos excluidos de Git
requirements.txt                Dependencias
registro_solicitudes_rrhh.txt   Evidencia del agente de acción
```

---

# ⚙️ Instrucciones de ejecución

## 1. Requisitos previos

Instalar:

- Python 3.10 o superior;
- Git;
- una API key válida de Google Gemini;
- conexión a Internet;
- PowerShell, CMD o una terminal compatible.

Comprobar Python:

```powershell
python --version
```

Comprobar Git:

```powershell
git --version
```

---

## 2. Clonar el repositorio

```powershell
git clone https://github.com/LEARS1/mesa-ayuda-ia-rrhh-patito.git
cd mesa-ayuda-ia-rrhh-patito
```

---

## 3. Crear el entorno virtual

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### Windows CMD

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 4. Instalar las dependencias

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## 5. Configurar las variables de entorno

Copiar la plantilla:

### PowerShell

```powershell
Copy-Item .env.example .env
```

### CMD

```cmd
copy .env.example .env
```

### Linux/macOS

```bash
cp .env.example .env
```

Abrir `.env` y colocar una clave válida:

```env
GOOGLE_API_KEY=COLOQUE_AQUI_SU_API_KEY
```

Configuración recomendada de modelos:

```env
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_VISION_MODEL=gemini-3.5-flash-lite
GEMINI_EMBEDDING_MODEL=gemini-embedding-2
```

Configuración de Phoenix:

```env
PHOENIX_ENABLED=true
PHOENIX_PROJECT_NAME=mesa-ayuda-rrhh-patito
PHOENIX_COLLECTOR_ENDPOINT=http://127.0.0.1:6006/v1/traces
PHOENIX_PROTOCOL=http/protobuf
```

> El archivo `.env` contiene secretos y nunca debe subirse a GitHub.

---

## 6. Ejecutar las pruebas

Con el entorno virtual activado:

```powershell
python tests\verificacion_estatica.py
python tests\verificacion_cambio_intencion.py
python tests\verificacion_phoenix.py
```

Resultados esperados:

```text
OK: estructura y entregables mínimos presentes.
OK: el cambio de intención funciona correctamente.
OK: integración estática de Phoenix completa.
```

---

## 7. Iniciar Arize Phoenix

Abrir una terminal y activar el entorno virtual:

```powershell
.\venv\Scripts\Activate.ps1
phoenix serve
```

Phoenix estará disponible en:

```text
http://127.0.0.1:6006
```

El endpoint OTLP HTTP utilizado por la aplicación es:

```text
http://127.0.0.1:6006/v1/traces
```

---

## 8. Iniciar la aplicación

Abrir una segunda terminal:

```powershell
cd C:\RUTA\AL\PROYECTO
.\venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload
```

La aplicación estará disponible en:

- Interfaz: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- Estado de Phoenix: `http://127.0.0.1:8000/observabilidad/estado`

En el primer inicio se generan o validan los índices Chroma.

---

## 9. Verificar Phoenix

Abrir:

```text
http://127.0.0.1:8000/observabilidad/estado
```

Resultado esperado:

```json
{
  "habilitado": true,
  "inicializado": true,
  "proyecto": "mesa-ayuda-rrhh-patito",
  "collector_endpoint": "http://127.0.0.1:6006/v1/traces",
  "protocolo": "http/protobuf",
  "error": null
}
```

Después de realizar una consulta, Phoenix debe recibir solicitudes en:

```text
POST /v1/traces
```

---

## 10. Probar el sistema

### Consulta simple

```text
¿Qué cubre el seguro médico corporativo?
```

### Consulta mixta

```text
¿Cuántos días de vacaciones me corresponden, qué cubre el seguro médico y cómo funciona el programa de referidos?
```

Se espera que intervengan:

- Políticas Internas;
- Beneficios y Compensaciones;
- Reclutamiento y Onboarding.

### Pregunta fuera del alcance

```text
¿Cuál será el precio de las acciones de Patito S.A. el próximo año?
```

Respuesta esperada:

```text
No encontré información suficiente en la base documental proporcionada.
```

### Solicitud de acción

```text
Quiero solicitar vacaciones.
```

Después proporcionar:

```text
Mi nombre es Usuario de Prueba.
Deseo vacaciones del 17 al 21 de agosto de 2026.
Mi jefe aprobador es Jefe de Prueba.
```

Confirmar con:

```text
Confirmo.
```

### Imagen de prueba

Usar:

```text
tests/imagenes/formulario_dependiente_prueba.png
```

Pregunta sugerida:

```text
Revisa este formulario e indica qué información está completa y qué datos faltan.
```

Más casos están disponibles en [`docs/ejemplos_pruebas.md`](docs/ejemplos_pruebas.md).

---

## 🌐 Endpoints principales

- `GET /`: interfaz web.
- `POST /chat`: consulta normal.
- `POST /chat-imagen`: consulta con imagen.
- `GET /solicitudes`: historial confirmado.
- `GET /solicitudes/estado/{thread_id}`: estado actual.
- `GET /solicitudes/panel/{thread_id}`: estado e historial.
- `GET /observabilidad/estado`: estado de Phoenix.

---

## 👁️ Observabilidad con Arize Phoenix

Al activar:

```env
PHOENIX_ENABLED=true
```

las ejecuciones de LangChain/LangGraph se envían a Phoenix y se agrupan mediante el mismo `thread_id` utilizado por la memoria conversacional.

Phoenix permite revisar:

- herramientas utilizadas;
- llamadas a Gemini;
- latencia;
- tokens;
- errores;
- sesiones;
- selección de agentes;
- trazas de consultas simples, mixtas, multimodales y de acción.

La metadata añadida es operativa y no debe contener:

- nombres reales;
- cédulas;
- documentos sensibles;
- rutas locales;
- imágenes en Base64.

Guía ampliada:

[`docs/observabilidad_phoenix.md`](docs/observabilidad_phoenix.md)

---

## 🔐 Seguridad y privacidad

- La API key se carga desde `.env`.
- `.env` no se sube a GitHub.
- `.env.example` no contiene secretos.
- `venv`, `chroma_db`, cachés y archivos temporales se excluyen con `.gitignore`.
- No deben utilizarse datos personales reales durante las pruebas.
- Los documentos e imágenes del proyecto son ficticios.
- Los logs deben evitar información sensible.
- El repositorio debe revisarse antes de cada entrega.

---

## ⚠️ Limitaciones

- Memoria conversacional almacenada en RAM.
- Persistencia de acciones mediante TXT.
- Sin autenticación ni autorización.
- Sin control de acceso por roles.
- Sin bloqueo transaccional para escrituras concurrentes.
- Dependencia de la disponibilidad y cuota de Gemini.
- Documentos de prueba pequeños.
- Prototipo académico, no solución productiva.

---

## 🚀 Riesgos y mejoras futuras

Para una versión productiva se propone:

- base de datos transaccional;
- autenticación;
- autorización por roles;
- permisos por agente y documento;
- cifrado de información;
- anonimización de trazas;
- auditoría;
- almacenamiento seguro de imágenes;
- evaluación automática de respuestas;
- feedback de usuarios;
- monitoreo de costos y tokens;
- alertas por errores y latencia;
- pruebas de carga;
- despliegue con Docker;
- gestión centralizada de secretos.

Consultar:

[`docs/riesgos_mejoras.md`](docs/riesgos_mejoras.md)


---

## 📄 Licencia y uso

Proyecto académico desarrollado exclusivamente con fines educativos para el Semillero de Inteligencia Artificial. Los documentos, nombres y datos utilizados son ficticios.
