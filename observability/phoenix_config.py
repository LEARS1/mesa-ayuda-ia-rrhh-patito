"""Configuración opcional de Arize Phoenix para la mesa de ayuda.

La aplicación no depende de que Phoenix esté disponible. Si la observabilidad
está deshabilitada, el paquete no está instalado o el colector no responde,
el flujo principal continúa sin interrumpirse.
"""

from __future__ import annotations

import os
from contextlib import ExitStack, contextmanager, nullcontext
from typing import Iterator

from dotenv import load_dotenv

load_dotenv()

_TRACER_PROVIDER = None
_INICIALIZACION_INTENTADA = False
_ERROR_INICIALIZACION = ""


def _es_verdadero(valor: str | None) -> bool:
    return (valor or "").strip().lower() in {
        "1",
        "true",
        "yes",
        "si",
        "sí",
        "on",
    }


def phoenix_habilitado() -> bool:
    """Indica si Phoenix fue activado mediante variables de entorno."""
    return _es_verdadero(os.getenv("PHOENIX_ENABLED", "false"))


def inicializar_phoenix():
    """Registra OpenTelemetry/OpenInference antes de usar LangChain.

    La función es idempotente para evitar doble instrumentación durante imports.
    Con ``uvicorn --reload`` cada proceso hijo realiza su propia inicialización,
    que es el comportamiento esperado.
    """

    global _TRACER_PROVIDER
    global _INICIALIZACION_INTENTADA
    global _ERROR_INICIALIZACION

    if _INICIALIZACION_INTENTADA:
        return _TRACER_PROVIDER

    _INICIALIZACION_INTENTADA = True

    if not phoenix_habilitado():
        print("[PHOENIX] Observabilidad deshabilitada por configuración.")
        return None

    proyecto = os.getenv(
        "PHOENIX_PROJECT_NAME",
        "mesa-ayuda-rrhh-patito",
    ).strip()
    endpoint = os.getenv(
        "PHOENIX_COLLECTOR_ENDPOINT",
        "http://127.0.0.1:6006",
    ).strip()
    protocolo = os.getenv(
        "PHOENIX_PROTOCOL",
        "http/protobuf",
    ).strip()

    try:
        from phoenix.otel import register

        _TRACER_PROVIDER = register(
            project_name=proyecto,
            endpoint=endpoint,
            protocol=protocolo,
            auto_instrument=True,
            batch=True,
        )

        print("[PHOENIX] Observabilidad habilitada.")
        print(f"[PHOENIX] Proyecto: {proyecto}")
        print(f"[PHOENIX] Colector: {endpoint}")
        print("[PHOENIX] UI local esperada: http://127.0.0.1:6006")
        return _TRACER_PROVIDER

    except Exception as error:  # Phoenix nunca debe tumbar la API principal.
        _ERROR_INICIALIZACION = str(error)
        print("[PHOENIX] No se pudo inicializar la observabilidad.")
        print(f"[PHOENIX] Detalle: {_ERROR_INICIALIZACION}")
        return None


def estado_phoenix() -> dict:
    """Devuelve un estado seguro para diagnóstico, sin credenciales."""
    return {
        "habilitado": phoenix_habilitado(),
        "inicializado": _TRACER_PROVIDER is not None,
        "proyecto": os.getenv(
            "PHOENIX_PROJECT_NAME",
            "mesa-ayuda-rrhh-patito",
        ),
        "collector_endpoint": os.getenv(
            "PHOENIX_COLLECTOR_ENDPOINT",
            "http://127.0.0.1:6006",
        ),
        "protocolo": os.getenv(
            "PHOENIX_PROTOCOL",
            "http/protobuf",
        ),
        "error": _ERROR_INICIALIZACION or None,
    }


@contextmanager
def contexto_phoenix(
    *,
    session_id: str,
    canal: str,
    tags: list[str] | None = None,
    metadata: dict | None = None,
) -> Iterator[None]:
    """Propaga sesión, etiquetas y metadata a los spans internos.

    Solo se adjuntan metadatos operativos. No se deben incluir nombres,
    documentos, preguntas completas ni contenido de imágenes.
    """

    if _TRACER_PROVIDER is None:
        with nullcontext():
            yield
        return

    try:
        from phoenix.otel import using_metadata, using_session, using_tags

        metadata_segura = {
            "aplicacion": "mesa_ayuda_rrhh",
            "empresa": "Patito S.A.",
            "canal": canal,
            **(metadata or {}),
        }
        etiquetas = [
            "rrhh",
            "fastapi",
            "langgraph",
            canal,
            *(tags or []),
        ]

        stack = ExitStack()
        stack.enter_context(using_session(session_id=session_id))
        stack.enter_context(using_metadata(metadata_segura))
        stack.enter_context(using_tags(etiquetas))
    except Exception as error:
        # Un fallo al preparar tracing no debe afectar al usuario final.
        print(f"[PHOENIX] No se pudo aplicar el contexto de traza: {error}")
        with nullcontext():
            yield
        return

    with stack:
        yield
