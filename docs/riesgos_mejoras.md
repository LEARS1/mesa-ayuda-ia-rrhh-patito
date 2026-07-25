# Riesgos, limitaciones y mejoras futuras

## Riesgos actuales

- La memoria conversacional es en RAM y se pierde al reiniciar.
- El TXT no es adecuado para escrituras concurrentes de producción.
- La disponibilidad depende de la API de Gemini.
- Chroma local no ofrece alta disponibilidad.
- Un modelo generativo puede interpretar de forma incorrecta una intención ambigua.

## Controles incorporados

- Temperatura cero.
- Respuestas RAG limitadas al contexto recuperado.
- Colecciones vectoriales separadas.
- Confirmación explícita para acciones.
- Validación de campos, fechas y duplicados.
- Secretos mediante variables de entorno.
- Trazabilidad de agentes, tools, fuentes y chunks.

## Mejoras productivas

- Sustituir TXT por PostgreSQL con transacciones.
- Persistir checkpointer y borradores por usuario autenticado.
- Incorporar roles y permisos por documento/agente.
- Cifrar datos y definir retención/borrado.
- Añadir rate limiting y autenticación.
- Evaluar recuperación con un conjunto de preguntas etiquetado.
- Medir tokens, coste, latencia, errores y satisfacción.
- Incorporar botones de feedback y revisión humana.
