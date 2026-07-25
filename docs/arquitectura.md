# Arquitectura de la Mesa de Ayuda IA

```text
Usuario / navegador
        |
        v
FastAPI: /chat y /chat-imagen
        |
        v
Agente Orquestador ReAct (LangGraph)
        |
        +-- Agente lógico de Beneficios
        |      +-- Retriever exclusivo
        |      +-- Colección Chroma: beneficios_compensaciones
        |
        +-- Agente lógico de Políticas
        |      +-- Retriever exclusivo
        |      +-- Colección Chroma: politicas_internas
        |
        +-- Agente lógico de Reclutamiento y Onboarding
        |      +-- Retriever exclusivo
        |      +-- Colección Chroma: reclutamiento_onboarding
        |
        +-- Agente de Acción
        |      +-- Valida datos, confirmación y duplicados
        |      +-- Escribe registro_solicitudes_rrhh.txt
        |
        +-- Agente Multimodal
               +-- Gemini con visión
               +-- Analiza imágenes asociadas al thread_id
```

## Separación de responsabilidades

- `agents/react_agent.py`: orquestación y herramientas especializadas.
- `rag/services.py`: recuperación y generación basada en contexto.
- `rag/vectorstores.py`: creación y carga de índices Chroma.
- `services/request_service.py`: reglas de negocio de solicitudes.
- `main.py`: API, métricas y trazabilidad.
- `templates/index.html`: interfaz web y panel lateral.

## Decisión arquitectónica

Los tres agentes RAG se implementan como agentes lógicos especializados expuestos al orquestador mediante tools. Cada uno tiene dominio, retriever, colección vectorial, documento y fuentes independientes. Esta decisión reduce complejidad para un prototipo, conserva aislamiento documental y facilita añadir nuevos dominios.
