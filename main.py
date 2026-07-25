# ============================================================
# PROYECTO FINAL - MESA DE AYUDA IA PARA RECURSOS HUMANOS
# PATITO S.A.
# ============================================================

import time
import traceback
import uuid
from datetime import datetime
from pathlib import Path

# Phoenix debe inicializarse antes de importar y utilizar LangChain/LangGraph.
from observability.phoenix_config import (
    contexto_phoenix,
    estado_phoenix,
    inicializar_phoenix,
)

inicializar_phoenix()

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)

from agents.multimodal_agent import (
    obtener_mime_type,
    responder_pregunta_sobre_imagen,
)
from agents.react_agent import ejecutar_agente
from api.models import Consulta
from config.settings import (
    EMBEDDING_MODEL,
    GOOGLE_API_KEY,
    MODEL_NAME,
    UPLOADS_DIR,
    VISION_MODEL_NAME,
)
from core.state import contexto_multimodal
from rag.services import inicializar_bases_conocimiento
from services.request_service import (
    obtener_estado_solicitud,
    obtener_resumen_panel,
    obtener_solicitudes_registradas,
)

BASE_DIR = Path(__file__).resolve().parent
INDEX_PATH = BASE_DIR / "templates" / "index.html"

llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    google_api_key=GOOGLE_API_KEY,
    max_retries=0,
)

llm_vision = ChatGoogleGenerativeAI(
    model=VISION_MODEL_NAME,
    google_api_key=GOOGLE_API_KEY,
    max_retries=0,
)

embeddings = GoogleGenerativeAIEmbeddings(
    model=EMBEDDING_MODEL,
    google_api_key=GOOGLE_API_KEY,
)

print("\n==========================================")
print("Inicializando bases de conocimiento RAG")
print("==========================================")
retrievers = inicializar_bases_conocimiento(embeddings)
print("Bases RAG inicializadas correctamente.")

app = FastAPI(
    title="Mesa de Ayuda IA - RRHH",
    description=(
        "Prototipo de agentes especializados "
        "para Recursos Humanos de Patito S.A."
    ),
    version="5.0.0",
)


MAPA_AGENTES_POR_HERRAMIENTA = {
    "RAG de Beneficios y Compensaciones":
        "Agente de Beneficios y Compensaciones",
    "RAG de Políticas Internas":
        "Agente de Políticas Internas",
    "RAG de Reclutamiento y Onboarding":
        "Agente de Reclutamiento y Onboarding",
    "Gestor de solicitudes de RRHH":
        "Agente de Acción",
    "Agente Multimodal de Imagen":
        "Agente Multimodal de Imagen",
}


def obtener_agentes_participantes(herramientas: list[str]) -> list[str]:
    """Convierte las herramientas ejecutadas en agentes trazables."""
    agentes = ["Agente Orquestador ReAct"]

    for herramienta in herramientas:
        agente = MAPA_AGENTES_POR_HERRAMIENTA.get(herramienta)
        if agente and agente not in agentes:
            agentes.append(agente)

    return agentes


def _respuesta_chat(
    resultado: dict,
    thread_id: str,
    duracion_segundos: float,
) -> dict:
    """Construye una respuesta uniforme y trazable."""
    herramientas = resultado.get("herramientas", [])
    fuentes = resultado.get("fuentes", [])

    advertencias = []
    if not fuentes and any(
        herramienta.startswith("RAG de")
        for herramienta in herramientas
    ):
        advertencias.append(
            "La consulta documental no produjo fuentes verificables."
        )

    return {
        "respuesta": resultado.get(
            "respuesta",
            "No se pudo obtener una respuesta.",
        ),
        "agentes_participantes":
            obtener_agentes_participantes(herramientas),
        "herramientas_utilizadas": [
            "LangGraph ReAct",
            "Memoria conversacional por thread_id",
            *herramientas,
        ],
        "fuentes": fuentes,
        "categoria": ["react"],
        "advertencias": advertencias,
        "metricas": {
            "tiempo_respuesta_segundos": round(duracion_segundos, 3),
            "cantidad_herramientas": len(herramientas),
            "cantidad_fuentes": len(fuentes),
        },
        "thread_id": thread_id,
        "solicitud_actual": obtener_estado_solicitud(thread_id),
    }


@app.post("/chat")
async def chat_rrhh(consulta: Consulta):
    pregunta = consulta.pregunta.strip()
    thread_id = consulta.thread_id.strip()

    if not pregunta:
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")
    if not thread_id:
        raise HTTPException(status_code=400, detail="El thread_id no puede estar vacío.")

    try:
        inicio = time.perf_counter()
        with contexto_phoenix(
            session_id=thread_id,
            canal="chat_texto",
            tags=["texto", "agente-react"],
            metadata={
                "endpoint": "/chat",
                "tiene_imagen": False,
            },
        ):
            resultado = ejecutar_agente(
                pregunta=pregunta,
                thread_id=thread_id,
                retrievers=retrievers,
                llm=llm,
                llm_vision=llm_vision,
            )
        duracion = time.perf_counter() - inicio
        return _respuesta_chat(resultado, thread_id, duracion)
    except Exception as error:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando la consulta: {error}",
        ) from error


@app.post("/chat-imagen")
async def chat_con_imagen(
    pregunta: str = Form(...),
    imagen: UploadFile = File(...),
    thread_id: str = Form("usuario_web"),
):
    try:
        extension = Path(imagen.filename or "").suffix.lower()
        mime_type = obtener_mime_type(extension)
        if not mime_type:
            raise HTTPException(
                status_code=400,
                detail="Formato no compatible. Use JPG, JPEG, PNG o WEBP.",
            )

        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        nombre_seguro = f"{uuid.uuid4().hex}{extension}"
        ruta_imagen = UPLOADS_DIR / nombre_seguro
        ruta_imagen.write_bytes(await imagen.read())

        contexto_multimodal[thread_id] = {
            "ruta_imagen": str(ruta_imagen),
            "mime_type": mime_type,
            "analisis": "",
            "nombre_archivo": imagen.filename,
            "timestamp": datetime.now().isoformat(),
        }

        # Una imagen recién adjuntada se procesa de forma directa con
        # el agente multimodal. Una solicitud pendiente se conserva,
        # pero no puede secuestrar esta intención.
        inicio = time.perf_counter()
        with contexto_phoenix(
            session_id=thread_id,
            canal="chat_imagen",
            tags=["multimodal", "gemini-vision"],
            metadata={
                "endpoint": "/chat-imagen",
                "tiene_imagen": True,
                "mime_type": mime_type,
            },
        ):
            texto_respuesta = responder_pregunta_sobre_imagen(
                thread_id=thread_id,
                pregunta=pregunta or "Analiza esta imagen.",
                llm_vision=llm_vision,
            )
        duracion = time.perf_counter() - inicio
        resultado = {
            "respuesta": texto_respuesta,
            "fuentes": [
                {
                    "documento": imagen.filename,
                    "tipo": "imagen proporcionada por el usuario",
                }
            ],
            "herramientas": ["Agente Multimodal de Imagen"],
        }
        respuesta = _respuesta_chat(resultado, thread_id, duracion)
        respuesta["archivo_procesado"] = imagen.filename
        return respuesta
    except HTTPException:
        raise
    except Exception as error:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando la imagen: {error}",
        ) from error


@app.get("/solicitudes")
async def listar_solicitudes():
    """Lista las solicitudes confirmadas guardadas en el archivo persistente."""
    solicitudes = obtener_solicitudes_registradas()
    return {
        "total": len(solicitudes),
        "solicitudes": list(reversed(solicitudes)),
    }


@app.get("/solicitudes/estado/{thread_id}")
async def estado_solicitud(thread_id: str):
    """Devuelve el borrador o último resultado de un thread."""
    return obtener_estado_solicitud(thread_id)


@app.get("/solicitudes/panel/{thread_id}")
async def panel_solicitudes(thread_id: str):
    """Devuelve estado actual e historial para actualizar el panel lateral."""
    resumen = obtener_resumen_panel(thread_id)
    resumen["solicitudes_registradas"] = list(
        reversed(resumen["solicitudes_registradas"])
    )
    return resumen


@app.get("/observabilidad/estado")
async def observabilidad_estado():
    """Expone el estado de Phoenix sin mostrar secretos."""
    return estado_phoenix()


@app.get("/")
async def home():
    if not INDEX_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail=f"No se encontró la interfaz web: {INDEX_PATH}",
        )
    return FileResponse(INDEX_PATH)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
