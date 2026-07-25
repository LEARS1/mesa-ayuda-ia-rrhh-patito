import base64

from pathlib import Path

from langchain_core.messages import HumanMessage

from core.constants import (
    RESPUESTA_SIN_INFORMACION
)

from core.state import (
    contexto_multimodal
)

from utils.helpers import (
    normalizar_texto,
    convertir_contenido_a_texto
)


def obtener_mime_type(

    extension: str

) -> str | None:

    tipos = {

        ".jpg":
            "image/jpeg",

        ".jpeg":
            "image/jpeg",

        ".png":
            "image/png",

        ".webp":
            "image/webp"

    }


    return tipos.get(
        extension.lower()
    )


def analizar_imagen_con_gemini(

    ruta_imagen: Path,

    instruccion: str,

    llm_vision

) -> str:

    if not ruta_imagen.exists():

        raise FileNotFoundError(

            f"No se encontró la imagen: "
            f"{ruta_imagen}"

        )


    mime_type = obtener_mime_type(

        ruta_imagen.suffix

    )


    if not mime_type:

        raise ValueError(
            "Formato de imagen no compatible."
        )


    with open(

        ruta_imagen,

        "rb"

    ) as archivo:

        imagen_base64 = (

            base64.b64encode(

                archivo.read()

            ).decode(
                "utf-8"
            )

        )


    prompt = f"""

Eres un agente multimodal especializado
en Recursos Humanos de Patito S.A.

Analiza exclusivamente la imagen proporcionada.

INSTRUCCIÓN DEL USUARIO:

{instruccion}

REGLAS:

- Analiza únicamente la información visible.
- No inventes datos.
- No utilices información externa.
- Si un campo está vacío, indícalo.
- Si un dato no puede leerse, indícalo.
- Responde específicamente la pregunta.

Si la información no aparece, responde:

"{RESPUESTA_SIN_INFORMACION}"

Devuelve una respuesta clara y estructurada.

"""


    mensaje = HumanMessage(

        content=[

            {

                "type":
                    "text",

                "text":
                    prompt

            },

            {

                "type":
                    "image_url",

                "image_url": {

                    "url":
                        (
                            f"data:{mime_type};"
                            f"base64,"
                            f"{imagen_base64}"
                        )

                }

            }

        ]

    )


    respuesta = llm_vision.invoke(

        [

            mensaje

        ]

    )


    return convertir_contenido_a_texto(

        respuesta.content

    )


def es_pregunta_sobre_imagen(

    pregunta: str

) -> bool:

    texto = normalizar_texto(
        pregunta
    )


    palabras = [

        "cedula",

        "cédula",

        "numero de cedula",

        "número de cédula",

        "nombre del colaborador",

        "nombre del empleado",

        "nombre del dependiente",

        "fecha de nacimiento",

        "vinculo",

        "vínculo",

        "documento",

        "formulario",

        "imagen",

        "foto",

        "campo",

        "dato visible",

        "que dice",

        "qué dice",

        "aparece"

    ]


    return any(

        palabra in texto

        for palabra in palabras

    )


def responder_pregunta_sobre_imagen(

    thread_id: str,

    pregunta: str,

    llm_vision

) -> str:

    if thread_id not in contexto_multimodal:

        return (

            "No tengo una imagen asociada "
            "a esta conversación. "
            "Por favor, adjunta nuevamente "
            "el documento o la imagen."

        )


    datos_imagen = (

        contexto_multimodal[
            thread_id
        ]

    )


    ruta_imagen = Path(

        datos_imagen[
            "ruta_imagen"
        ]

    )


    instruccion = f"""

El usuario realiza una pregunta
de seguimiento sobre la imagen.

Pregunta actual:

{pregunta}

Responde únicamente utilizando
la información visible en la imagen.

Si el dato no aparece claramente,
indícalo.

"""


    return analizar_imagen_con_gemini(

        ruta_imagen,

        instruccion,

        llm_vision

    )