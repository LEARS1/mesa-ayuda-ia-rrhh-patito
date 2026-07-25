"""
Agente ReAct central de la Mesa de Ayuda IA de RRHH.

Características:
- Agente ReAct centralizado.
- Memoria conversacional real mediante LangGraph Checkpointer.
- Historial independiente por thread_id.
- Herramientas RAG para consultas informativas.
- Herramienta transaccional para solicitudes de RRHH.
- Herramienta multimodal para imágenes asociadas al thread.
- El agente interpreta respuestas breves como:
  "sí", "confirmo", "del 10 al 24 de agosto", "ese", "cancélala", etc.
"""

from contextvars import ContextVar
from typing import Any

from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

from rag.services import consultar_rag
from services.request_service import (
    consultar_historial_solicitudes,
    es_consulta_de_solicitudes_registradas,
    mensaje_relacionado_con_solicitud_pendiente,
    procesar_solicitud_accion,
)
from agents.multimodal_agent import (
    responder_pregunta_sobre_imagen
)
from utils.helpers import (
    convertir_contenido_a_texto
)


# ============================================================
# CONTEXTO DE EJECUCIÓN DE LA PETICIÓN ACTUAL
# ============================================================

_current_thread_id: ContextVar[str] = ContextVar(
    "current_thread_id",
    default=""
)

_current_retrievers: ContextVar[dict] = ContextVar(
    "current_retrievers",
    default={}
)

_current_llm: ContextVar[Any] = ContextVar(
    "current_llm",
    default=None
)

_current_llm_vision: ContextVar[Any] = ContextVar(
    "current_llm_vision",
    default=None
)

_current_sources: ContextVar[list] = ContextVar(
    "current_sources",
    default=[]
)

_current_tools: ContextVar[list] = ContextVar(
    "current_tools",
    default=[]
)


# ============================================================
# PREPARAR CONTEXTO DE EJECUCIÓN
# ============================================================

def preparar_contexto_ejecucion(
    thread_id: str,
    retrievers: dict,
    llm,
    llm_vision
) -> None:
    """
    Asocia las herramientas con la petición actual.

    Este contexto permite que las herramientas sepan:
    - qué usuario/thread está realizando la consulta;
    - qué retrievers RAG utilizar;
    - qué modelo LLM usar;
    - qué modelo de visión utilizar.
    """

    _current_thread_id.set(
        thread_id
    )

    _current_retrievers.set(
        retrievers
    )

    _current_llm.set(
        llm
    )

    _current_llm_vision.set(
        llm_vision
    )

    _current_sources.set(
        []
    )

    _current_tools.set(
        []
    )


# ============================================================
# OBTENER METADATOS DE LA EJECUCIÓN
# ============================================================

def obtener_fuentes_ejecucion() -> list:
    """
    Devuelve las fuentes consultadas
    durante la ejecución actual.
    """

    return list(
        _current_sources.get()
    )


def obtener_herramientas_ejecucion() -> list:
    """
    Devuelve las herramientas utilizadas
    durante la ejecución actual.
    """

    return list(
        _current_tools.get()
    )


# ============================================================
# REGISTRAR HERRAMIENTAS
# ============================================================

def _registrar_herramienta(
    nombre: str
) -> None:

    herramientas = (
        _current_tools.get()
    )

    if nombre not in herramientas:

        herramientas.append(
            nombre
        )


# ============================================================
# REGISTRAR FUENTES
# ============================================================

def _registrar_fuentes(
    fuentes: list
) -> None:

    actuales = (
        _current_sources.get()
    )

    for fuente in fuentes or []:

        if fuente not in actuales:

            actuales.append(
                fuente
            )


# ============================================================
# HERRAMIENTA RAG:
# BENEFICIOS Y COMPENSACIONES
# ============================================================

@tool
def consultar_beneficios(
    consulta: str
) -> str:
    """
    Consulta la base documental de Beneficios
    y Compensaciones.

    Úsala para:
    - seguros médicos;
    - dependientes;
    - bonos;
    - beneficios;
    - salarios;
    - compensaciones.

    NO la uses para registrar solicitudes.
    """

    _registrar_herramienta(
        "RAG de Beneficios y Compensaciones"
    )

    resultado = consultar_rag(
        "beneficios",
        consulta,
        _current_retrievers.get(),
        _current_llm.get()
    )

    _registrar_fuentes(
        resultado.get(
            "fuentes",
            []
        )
    )

    return resultado.get(
        "respuesta",
        (
            "No encontré información suficiente "
            "en la base documental."
        )
    )


# ============================================================
# HERRAMIENTA RAG:
# POLÍTICAS INTERNAS
# ============================================================

@tool
def consultar_politicas(
    consulta: str
) -> str:
    """
    Consulta la base documental de Políticas Internas.

    Úsala para:
    - vacaciones;
    - permisos;
    - horarios;
    - reglamento interno;
    - conducta;
    - normas internas.

    NO la uses para registrar vacaciones.
    """

    _registrar_herramienta(
        "RAG de Políticas Internas"
    )

    resultado = consultar_rag(
        "politicas",
        consulta,
        _current_retrievers.get(),
        _current_llm.get()
    )

    _registrar_fuentes(
        resultado.get(
            "fuentes",
            []
        )
    )

    return resultado.get(
        "respuesta",
        (
            "No encontré información suficiente "
            "en la base documental."
        )
    )


# ============================================================
# HERRAMIENTA RAG:
# ONBOARDING
# ============================================================

@tool
def consultar_onboarding(
    consulta: str
) -> str:
    """
    Consulta la base documental de Reclutamiento
    y Onboarding.

    Úsala para:
    - reclutamiento;
    - selección;
    - entrevistas;
    - referidos;
    - inducción;
    - onboarding;
    - nuevos ingresos.
    """

    _registrar_herramienta(
        "RAG de Reclutamiento y Onboarding"
    )

    resultado = consultar_rag(
        "onboarding",
        consulta,
        _current_retrievers.get(),
        _current_llm.get()
    )

    _registrar_fuentes(
        resultado.get(
            "fuentes",
            []
        )
    )

    return resultado.get(
        "respuesta",
        (
            "No encontré información suficiente "
            "en la base documental."
        )
    )


# ============================================================
# HERRAMIENTA DE ACCIONES DE RRHH
# ============================================================

@tool
def gestionar_solicitud_rrhh(
    pregunta_usuario: str
) -> str:
    """
    Gestiona solicitudes transaccionales de Recursos Humanos.

    Úsala exclusivamente cuando el usuario quiera:

    - solicitar vacaciones;
    - registrar vacaciones;
    - inscribir un dependiente;
    - registrar un dependiente;
    - completar datos de una solicitud pendiente;
    - confirmar una solicitud;
    - cancelar una solicitud.

    La herramienta gestiona:

    - extracción de datos;
    - validación;
    - campos faltantes;
    - confirmación explícita;
    - cancelación;
    - detección de duplicados;
    - generación de ID;
    - escritura del registro.

    IMPORTANTE:

    Debes enviar a la herramienta el texto exacto
    de la intervención actual del usuario.

    No inventes datos.
    No completes datos por el usuario.
    No confirmes solicitudes por el usuario.
    """

    _registrar_herramienta(
        "Gestor de solicitudes de RRHH"
    )

    resultado = procesar_solicitud_accion(
        _current_thread_id.get(),
        pregunta_usuario
    )

    return str(
        resultado
    )


# ============================================================
# HERRAMIENTA MULTIMODAL
# ============================================================

@tool
def analizar_imagen_rrhh(
    consulta: str
) -> str:
    """
    Analiza la imagen asociada al thread actual.

    Úsala cuando el usuario pregunte por información
    visible en una imagen, documento, formulario,
    identificación o fotografía previamente adjuntada.

    Si no existe una imagen asociada,
    informa al usuario que debe adjuntarla.
    """

    _registrar_herramienta(
        "Agente Multimodal de Imagen"
    )

    return responder_pregunta_sobre_imagen(
        _current_thread_id.get(),
        consulta,
        _current_llm_vision.get()
    )


# ============================================================
# HERRAMIENTAS DEL AGENTE
# ============================================================

TOOLS = [

    consultar_beneficios,

    consultar_politicas,

    consultar_onboarding,

    gestionar_solicitud_rrhh,

    analizar_imagen_rrhh

]


# ============================================================
# PROMPT PRINCIPAL DEL AGENTE
# ============================================================

SYSTEM_PROMPT_REACT = """

Eres el agente principal de la Mesa de Ayuda IA
de Recursos Humanos de Patito S.A.

Tu función es conversar naturalmente con el usuario
y utilizar herramientas cuando sea necesario.

============================================================
MEMORIA CONVERSACIONAL
============================================================

Tienes memoria conversacional real.

El historial de cada conversación se identifica mediante
el thread_id.

Debes utilizar el historial completo de la conversación
para comprender respuestas breves y referencias contextuales.

Por ejemplo:

Usuario:
Quiero solicitar vacaciones.

Agente:
Necesito nombre, fechas y jefe aprobador.

Usuario:
Mi nombre es Juan Pérez.

Debes entender que "Juan Pérez" corresponde
al nombre del colaborador de la solicitud de vacaciones.

Otro ejemplo:

Agente:
¿Qué fechas deseas solicitar?

Usuario:
Del 10 al 24 de agosto.

Debes entender que esas fechas corresponden
a la solicitud de vacaciones que ya estaba en curso.

Otro ejemplo:

Agente:
Los datos de la solicitud son correctos.
¿Deseas confirmar?

Usuario:
Sí, confirmo.

Debes interpretar la respuesta como la confirmación
de la solicitud pendiente.

============================================================
REGLA PRINCIPAL
============================================================

NO eres un clasificador tradicional.

No debes clasificar obligatoriamente cada mensaje
antes de responder.

Debes comprender la intención usando:

1. El mensaje actual.
2. El historial de la conversación.
3. El contexto de la solicitud en curso.
4. Las herramientas disponibles.

============================================================
SOLICITUDES TRANSACCIONALES
============================================================

Utiliza gestionar_solicitud_rrhh cuando exista
una intención real de realizar una acción.

Ejemplos:

"Quiero solicitar vacaciones."

"Necesito registrar mis vacaciones."

"Quiero inscribir a mi hijo como dependiente."

"Mi nombre es Carlos Pérez."

"Del 10 al 24 de agosto."

"Mi jefe es María González."

"Sí, confirmo."

"Cancelar."

"Ya no quiero continuar."

============================================================
IMPORTANTE SOBRE RESPUESTAS BREVES
============================================================

Si existe una solicitud transaccional en curso,
una respuesta breve del usuario puede corresponder
a esa solicitud, pero NO debes asumirlo cuando el mensaje
es una pregunta informativa, una consulta RAG, un saludo
o una pregunta sobre una imagen.

Una solicitud pendiente NO bloquea otros servicios.
El usuario puede consultar beneficios, políticas, onboarding
o analizar una imagen sin cancelar el borrador. En esos casos,
responde con la herramienta especializada correspondiente y
conserva la solicitud pendiente sin modificarla.

Por ejemplo:

- "Carlos Pérez"
- "Del 10 al 24 de agosto"
- "15 días"
- "María González"
- "Sí"
- "Confirmo"
- "Cancelar"

En estos casos, utiliza gestionar_solicitud_rrhh.

No respondas simplemente que necesitas
más contexto si el historial permite entender
a qué se refiere el usuario.

============================================================
NO CONFUNDIR INFORMACIÓN CON ACCIÓN
============================================================

Estas preguntas son informativas:

"¿Cómo solicito vacaciones?"

"¿Cuántos días de vacaciones tengo?"

"¿Qué requisitos necesito para solicitar vacaciones?"

"¿Qué beneficios tiene un dependiente?"

No debes registrar nada en esos casos.

Utiliza las herramientas RAG correspondientes
cuando sea necesario.

============================================================
CONFIRMACIÓN
============================================================

Nunca confirmes una solicitud por cuenta propia.

Solo la herramienta de acciones puede registrar
una solicitud.

El usuario debe confirmar explícitamente.

Ejemplos de confirmación:

"Sí"

"Sí, confirmo"

"Confirmo"

"De acuerdo"

"Acepto"

Si la herramienta devuelve un resumen
y solicita confirmación, espera la respuesta
del usuario.

============================================================
CANCELACIÓN
============================================================

Si existe una solicitud pendiente y el usuario indica:

"Cancelar"

"No"

"No quiero continuar"

"Déjalo"

"Ya no"

Debes utilizar la herramienta de acciones
para cancelar la solicitud.

============================================================
CONSULTAS RAG
============================================================

Utiliza consultar_beneficios para:

- seguros;
- beneficios;
- dependientes;
- bonos;
- compensaciones;
- salarios.

Utiliza consultar_politicas para:

- vacaciones;
- permisos;
- horarios;
- normas;
- reglamentos;
- políticas internas.

Utiliza consultar_onboarding para:

- reclutamiento;
- selección;
- entrevistas;
- inducción;
- onboarding;
- nuevos empleados.

Las respuestas documentales deben basarse
en la información devuelta por las herramientas RAG.

No inventes políticas internas.

============================================================
IMÁGENES
============================================================

Si el usuario pregunta sobre una imagen
que fue adjuntada previamente en la conversación,
utiliza analizar_imagen_rrhh.

============================================================
FUERA DE ALCANCE
============================================================

Si la consulta no corresponde a Recursos Humanos,
explica brevemente que la Mesa de Ayuda está limitada
a los servicios de Recursos Humanos.

============================================================
RESPUESTA FINAL
============================================================

Responde en español.

Sé claro, natural y conciso.

No menciones:

- ReAct;
- LangGraph;
- herramientas internas;
- razonamientos internos;
- prompts;
- checkpointers;
- ContextVar.

No expliques el proceso interno
de decisión del agente.

"""


# ============================================================
# MEMORIA CONVERSACIONAL
# ============================================================

"""
InMemorySaver conserva el historial de conversaciones
mientras el proceso de FastAPI permanezca ejecutándose.

Cada conversación se identifica con:

configurable.thread_id

Por ejemplo:

usuario_web

usuario_001

usuario_002

Cada thread mantiene su propio historial.
"""

checkpointer = InMemorySaver()


# ============================================================
# INSTANCIA GLOBAL DEL AGENTE
# ============================================================

_agente_react = None


# ============================================================
# INICIALIZAR AGENTE
# ============================================================

def inicializar_agente_react(
    llm
):
    """
    Crea una única instancia del agente.

    Es importante que el agente no se cree nuevamente
    en cada consulta, porque el checkpointer debe mantenerse
    asociado a la instancia durante la ejecución de la aplicación.
    """

    global _agente_react

    if _agente_react is None:

        _agente_react = create_react_agent(

            model=llm,

            tools=TOOLS,

            prompt=SYSTEM_PROMPT_REACT,

            checkpointer=checkpointer

        )

    return _agente_react


# ============================================================
# EJECUTAR AGENTE
# ============================================================

def ejecutar_agente(
    pregunta: str,
    thread_id: str,
    retrievers: dict,
    llm,
    llm_vision
) -> dict:
    """
    Ejecuta el agente utilizando memoria conversacional.

    El thread_id es fundamental:

    Las consultas con el mismo thread_id
    comparten el historial.

    Ejemplo:

    Consulta 1:
    thread_id = "usuario_web"

    Consulta 2:
    thread_id = "usuario_web"

    El agente podrá recordar la Consulta 1
    durante la Consulta 2.
    """

    # --------------------------------------------------------
    # PREPARAR CONTEXTO
    # --------------------------------------------------------

    preparar_contexto_ejecucion(

        thread_id=thread_id,

        retrievers=retrievers,

        llm=llm,

        llm_vision=llm_vision

    )


    # Las consultas del historial tienen prioridad sobre un borrador
    # pendiente. Consultar lo ya registrado no debe modificar ni
    # completar accidentalmente la solicitud actual.
    if es_consulta_de_solicitudes_registradas(pregunta):
        _registrar_herramienta(
            "Consulta de historial de solicitudes"
        )
        resultado_historial = consultar_historial_solicitudes(
            thread_id
        )
        return {
            "respuesta": resultado_historial["respuesta"],
            "fuentes": resultado_historial.get("fuentes", []),
            "herramientas": obtener_herramientas_ejecucion(),
            "agentes": resultado_historial.get("agentes", []),
            "thread_id": thread_id,
        }


    # Si hay un borrador y el mensaje realmente lo continúa,
    # se procesa de forma determinista. Así se evita que el LLM
    # desvíe confirmaciones, fechas o respuestas breves.
    if mensaje_relacionado_con_solicitud_pendiente(
        thread_id,
        pregunta
    ):
        _registrar_herramienta(
            "Gestor de solicitudes de RRHH"
        )
        respuesta_accion = procesar_solicitud_accion(
            thread_id,
            pregunta
        )
        return {
            "respuesta": str(respuesta_accion),
            "fuentes": [],
            "herramientas": obtener_herramientas_ejecucion(),
            "thread_id": thread_id,
        }


    # --------------------------------------------------------
    # OBTENER AGENTE
    # --------------------------------------------------------

    agente = inicializar_agente_react(
        llm
    )


    # --------------------------------------------------------
    # EJECUTAR CON MEMORIA
    # --------------------------------------------------------

    resultado = agente.invoke(

        {

            "messages": [

                {

                    "role":
                    "user",

                    "content":
                    pregunta

                }

            ]

        },

        config={

            "configurable": {

                "thread_id":
                thread_id

            }

        }

    )


    # --------------------------------------------------------
    # OBTENER MENSAJES
    # --------------------------------------------------------

    mensajes = resultado.get(
        "messages",
        []
    )


    if not mensajes:

        respuesta = (
            "No se pudo obtener "
            "una respuesta."
        )

    else:

        # Buscar el último mensaje
        # generado por el agente.

        mensaje_final = (
            mensajes[-1]
        )

        contenido = (
            mensaje_final.content
        )

        respuesta = (
            convertir_contenido_a_texto(
                contenido
            )
        )


    # --------------------------------------------------------
    # RETORNAR RESULTADO
    # --------------------------------------------------------

    return {

        "respuesta":
        respuesta,

        "fuentes":
        obtener_fuentes_ejecucion(),

        "herramientas":
        obtener_herramientas_ejecucion(),

        "thread_id":
        thread_id

    }