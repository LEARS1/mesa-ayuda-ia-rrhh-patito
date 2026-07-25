"""Prueba rápida del aislamiento entre solicitudes, RAG e imágenes."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.state import solicitudes_pendientes
from services.request_service import mensaje_relacionado_con_solicitud_pendiente

THREAD = "prueba_cambio_intencion"

solicitudes_pendientes[THREAD] = {
    "tipo": "vacaciones",
    "nombre": "Usuario de Prueba",
    "fecha_inicio": "",
    "fecha_fin": "",
    "dias": 0,
    "jefe_aprobador": "",
    "dependiente": "",
    "vinculo": "",
    "documentos_respaldo": "",
    "confirmacion": "",
}

CASOS = {
    "¿Qué cubre el seguro médico?": False,
    "Analiza esta imagen": False,
    "¿Cuántos días de vacaciones tengo?": False,
    "Deseo saber qué solicitud está guardada hasta el momento": False,
    "Del 10 al 14 de agosto de 2026": True,
    "Mi jefe es Carlos López": True,
    "confirmo": True,
    "cancelar": True,
}

fallos = []
for mensaje, esperado in CASOS.items():
    obtenido = mensaje_relacionado_con_solicitud_pendiente(
        THREAD,
        mensaje,
    )
    estado = "OK" if obtenido == esperado else "FALLO"
    print(f"{estado}: {mensaje!r} -> {obtenido}")
    if obtenido != esperado:
        fallos.append((mensaje, esperado, obtenido))

solicitudes_pendientes.pop(THREAD, None)

if fallos:
    raise SystemExit(f"Fallaron {len(fallos)} casos: {fallos}")

print("OK: el cambio de intención funciona correctamente.")
