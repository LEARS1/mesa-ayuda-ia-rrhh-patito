# Ejemplos de pruebas y respuestas esperadas

## 1. Beneficios

**Pregunta:** ¿Qué cubre el seguro médico corporativo?

**Esperado:** usa el Agente de Beneficios, responde solo con el manual correspondiente e indica documento y chunks.

## 2. Políticas internas

**Pregunta:** ¿Cuántos días de vacaciones corresponden al año?

**Esperado:** usa el Agente de Políticas y cita `02_Reglamento_Interno.txt`.

## 3. Reclutamiento y onboarding

**Pregunta:** ¿Cómo funciona el programa de referidos y qué incluye el onboarding?

**Esperado:** usa el Agente de Reclutamiento y Onboarding.

## 4. Consulta mixta obligatoria

**Pregunta:** ¿Cuántos días de vacaciones tengo, qué cubre el seguro médico y cómo funciona el programa de referidos?

**Esperado:** intervienen Políticas, Beneficios y Reclutamiento/Onboarding; la respuesta se consolida y presenta fuentes de las tres bases.

## 5. Fuera del alcance

**Pregunta:** ¿Cuál será el precio de las acciones de Patito S.A.?

**Esperado:** `No encontré información suficiente en la base documental proporcionada.`

## 6. Agente de acción

1. `Quiero solicitar vacaciones.`
2. `Mi nombre es Usuario de Prueba.`
3. `Del 17 al 21 de agosto de 2026.`
4. `Mi jefe aprobador es Jefe de Prueba.`
5. `Confirmo.`

**Esperado:** solicita datos faltantes, muestra resumen, pide confirmación, genera ID único y escribe una sola línea en el TXT.

## 7. Duplicado

Repetir la misma solicitud de vacaciones.

**Esperado:** rechaza el segundo registro.

## 8. Multimodal

Adjuntar `tests/imagenes/formulario_dependiente_prueba.png` y preguntar: `¿Está completo y qué datos faltan?`

**Esperado:** usa el Agente Multimodal y describe únicamente información visible.
