from langchain_core.documents import Document

from config.settings import (
    DATA_DIR
)

from core.constants import (
    RESPUESTA_SIN_INFORMACION
)

from utils.helpers import (
    convertir_contenido_a_texto,
    limpiar_respuesta_modelo
)

from rag.vectorstores import (
    crear_o_cargar_vector_store
)


# ============================================================
# INICIALIZAR BASES DE CONOCIMIENTO
# ============================================================

def inicializar_bases_conocimiento(
    embeddings
):

    print(
        "\nInicializando bases de conocimiento RAG..."
    )


    # --------------------------------------------------------
    # BENEFICIOS Y COMPENSACIONES
    # --------------------------------------------------------

    vectorstore_beneficios = (
        crear_o_cargar_vector_store(

            DATA_DIR
            /
            "01_Beneficios_Compensaciones.txt",

            "beneficios_compensaciones",

            "01_Beneficios_Compensaciones.txt",

            embeddings

        )
    )


    # --------------------------------------------------------
    # POLÍTICAS INTERNAS
    # --------------------------------------------------------

    vectorstore_politicas = (
        crear_o_cargar_vector_store(

            DATA_DIR
            /
            "02_Reglamento_Interno.txt",

            "politicas_internas",

            "02_Reglamento_Interno.txt",

            embeddings

        )
    )


    # --------------------------------------------------------
    # RECLUTAMIENTO Y ONBOARDING
    # --------------------------------------------------------

    vectorstore_onboarding = (
        crear_o_cargar_vector_store(

            DATA_DIR
            /
            "03_Reclutamiento_Onboarding.txt",

            "reclutamiento_onboarding",

            "03_Reclutamiento_Onboarding.txt",

            embeddings

        )
    )


    print(
        "Bases de conocimiento "
        "inicializadas correctamente."
    )


    return {

        "beneficios":
            vectorstore_beneficios.as_retriever(

                search_kwargs={

                    "k": 4

                }

            ),


        "politicas":
            vectorstore_politicas.as_retriever(

                search_kwargs={

                    "k": 4

                }

            ),


        "onboarding":
            vectorstore_onboarding.as_retriever(

                search_kwargs={

                    "k": 4

                }

            )

    }


# ============================================================
# GENERAR RESPUESTA UTILIZANDO EL CONTEXTO RAG
# ============================================================

def responder_con_contexto(

    pregunta: str,

    documentos: list[Document],

    area: str,

    llm

) -> dict:


    # --------------------------------------------------------
    # VALIDAR DOCUMENTOS
    # --------------------------------------------------------

    if not documentos:

        return {

            "respuesta":
                RESPUESTA_SIN_INFORMACION,

            "fuentes": [],

            "encontro_informacion":
                False

        }


    # --------------------------------------------------------
    # CONSTRUIR CONTEXTO
    # --------------------------------------------------------

    contexto = "\n\n".join(

        documento.page_content

        for documento in documentos

    )


    # --------------------------------------------------------
    # OBTENER FUENTES
    # --------------------------------------------------------

    fuentes = []


    for documento in documentos:


        fuente = {

            "documento":
                documento.metadata.get(

                    "documento",

                    "Desconocido"

                ),

            "chunk":
                documento.metadata.get(

                    "chunk",

                    "Desconocido"

                )

        }


        if fuente not in fuentes:

            fuentes.append(

                fuente

            )


    # --------------------------------------------------------
    # PROMPT RAG PARA CONSULTAS SIMPLES Y MIXTAS
    # --------------------------------------------------------

    prompt = f"""

Eres un asistente especializado en el área de:

{area}

Debes responder la consulta del usuario utilizando
ÚNICAMENTE la información del contexto documental.

La consulta puede contener uno o varios temas.

Tu tarea es:

1. Leer toda la pregunta del usuario.
2. Identificar qué parte o partes de la pregunta
   están relacionadas con el área "{area}".
3. Utilizar la información del contexto documental
   para responder esas partes.
4. Ignorar únicamente los temas que pertenecen a
   otras áreas especializadas.
5. Si la información disponible responde parcialmente
   la pregunta, proporciona esa respuesta parcial.
6. No rechaces la pregunta completa solamente porque
   contenga otros temas.
7. No inventes información.
8. No utilices conocimiento externo.
9. No supongas información que no aparezca en el contexto.
10. Si el contexto contiene información relevante,
    debes utilizarla para responder.

IMPORTANTE:

Si existe información relacionada con cualquier parte
de la pregunta dentro del contexto, NO debes responder:

"{RESPUESTA_SIN_INFORMACION}"

Solo debes responder:

"{RESPUESTA_SIN_INFORMACION}"

cuando el contexto no contenga absolutamente ninguna
información relacionada con el área "{area}".

PREGUNTA COMPLETA DEL USUARIO:

{pregunta}

ÁREA ESPECIALIZADA:

{area}

CONTEXTO DOCUMENTAL:

{contexto}

RESPONDE DE FORMA CLARA Y DIRECTA ÚNICAMENTE
SOBRE LA PARTE DE LA PREGUNTA RELACIONADA
CON EL ÁREA "{area}".

"""


    # --------------------------------------------------------
    # CONSULTAR AL MODELO
    # --------------------------------------------------------

    respuesta = llm.invoke(

        prompt

    )


    # --------------------------------------------------------
    # CONVERTIR RESPUESTA
    # --------------------------------------------------------

    texto = convertir_contenido_a_texto(

        respuesta.content

    )


    texto = limpiar_respuesta_modelo(

        texto

    )


    # --------------------------------------------------------
    # VALIDAR RESPUESTA
    # --------------------------------------------------------

    if not texto:

        texto = (

            RESPUESTA_SIN_INFORMACION

        )


    encontro_informacion = (

        texto.strip().lower()

        !=

        RESPUESTA_SIN_INFORMACION.strip().lower()

    )


    return {

        "respuesta":
            texto,

        "fuentes":
            fuentes,

        "encontro_informacion":
            encontro_informacion

    }


# ============================================================
# CONSULTAR BASE RAG SEGÚN LA CATEGORÍA
# ============================================================

def consultar_rag(

    categoria: str,

    pregunta: str,

    retrievers: dict,

    llm

) -> dict:


    nombres = {

        "beneficios":
            "Beneficios y Compensaciones",

        "politicas":
            "Políticas Internas",

        "onboarding":
            "Reclutamiento y Onboarding"

    }


    # --------------------------------------------------------
    # VALIDAR CATEGORÍA
    # --------------------------------------------------------

    if categoria not in retrievers:

        return {

            "respuesta":
                RESPUESTA_SIN_INFORMACION,

            "fuentes": [],

            "encontro_informacion":
                False

        }


    print(

        f"[RAG] Consultando "

        f"{nombres.get(categoria, categoria)}"

    )


    # --------------------------------------------------------
    # RECUPERAR DOCUMENTOS
    # --------------------------------------------------------

    documentos = (

        retrievers[categoria].invoke(

            pregunta

        )

    )


    # --------------------------------------------------------
    # MOSTRAR CONTEXTO RECUPERADO
    # --------------------------------------------------------

    print(

        "\n[RAG] Documentos recuperados:"

    )


    for documento in documentos:

        print(

            "\n----------------------------------------"

        )

        print(

            documento.page_content

        )


    # --------------------------------------------------------
    # GENERAR RESPUESTA
    # --------------------------------------------------------

    resultado = responder_con_contexto(

        pregunta,

        documentos,

        nombres[categoria],

        llm

    )


    # --------------------------------------------------------
    # MOSTRAR RESULTADO
    # --------------------------------------------------------

    print(

        f"\n[RAG] Resultado completo de "

        f"{categoria}:"

    )


    print(

        resultado

    )


    return resultado