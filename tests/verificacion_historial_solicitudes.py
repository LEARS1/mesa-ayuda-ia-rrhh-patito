"""Verifica que consultar el historial no complete un borrador pendiente."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.state import solicitudes_pendientes
from services.request_service import (
    consultar_historial_solicitudes,
    es_consulta_de_solicitudes_registradas,
    mensaje_relacionado_con_solicitud_pendiente,
)

THREAD = "prueba_historial_solicitudes"

solicitudes_pendientes[THREAD] = {
    "tipo": "vacaciones",
    "nombre": "",
    "fecha_inicio": "",
    "fecha_fin": "",
    "dias": 0,
    "jefe_aprobador": "",
    "dependiente": "",
    "vinculo": "",
    "documentos_respaldo": "",
    "confirmacion": "",
}

consultas = [
    "Deseo saber qué solicitud está guardada hasta el momento",
    "¿Qué solicitudes tengo registradas?",
    "Muéstrame mis solicitudes",
    "Historial de solicitudes",
]

for consulta in consultas:
    assert es_consulta_de_solicitudes_registradas(consulta), consulta
    assert not mensaje_relacionado_con_solicitud_pendiente(THREAD, consulta), consulta

resultado = consultar_historial_solicitudes(THREAD)
assert "borrador pendiente" in resultado["respuesta"].lower()
assert solicitudes_pendientes[THREAD]["nombre"] == ""

solicitudes_pendientes.pop(THREAD, None)
print("OK: la consulta del historial no modifica el borrador pendiente.")
