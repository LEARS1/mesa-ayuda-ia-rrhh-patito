"""Agente de acción de RR. HH.

La lógica de negocio y el estado de las solicitudes se centralizan en
services.request_service para evitar dos máquinas de estados diferentes.
"""

from services.request_service import (
    procesar_solicitud_accion,
)


def procesar_accion(
    thread_id: str,
    pregunta: str
) -> dict:
    """Adaptador compatible con la interfaz anterior del agente de acción."""

    respuesta = procesar_solicitud_accion(
        thread_id,
        pregunta
    )

    texto = str(respuesta)
    registrada = texto.lower().startswith(
        "solicitud registrada correctamente"
    )

    requiere_confirmacion = (
        "¿deseas confirmar" in texto.lower()
        or "responde 'confirmo'" in texto.lower()
    )

    return {
        "respuesta": texto,
        "registrada": registrada,
        "requiere_confirmacion": requiere_confirmacion,
    }
