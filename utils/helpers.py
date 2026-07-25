import re


def normalizar_texto(
    texto: str
) -> str:

    if not texto:

        return ""

    texto = texto.strip().lower()

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto


def convertir_contenido_a_texto(
    contenido
) -> str:

    if contenido is None:

        return ""


    if isinstance(
        contenido,
        str
    ):

        return contenido


    if isinstance(
        contenido,
        list
    ):

        partes = []


        for elemento in contenido:

            if isinstance(
                elemento,
                str
            ):

                partes.append(
                    elemento
                )


            elif isinstance(
                elemento,
                dict
            ):

                if "text" in elemento:

                    partes.append(
                        str(
                            elemento["text"]
                        )
                    )


        return "".join(
            partes
        )


    return str(
        contenido
    )


def limpiar_respuesta_modelo(
    texto: str
) -> str:

    if not texto:

        return ""


    texto = texto.strip()


    texto = texto.replace(
        "```json",
        ""
    )


    texto = texto.replace(
        "```",
        ""
    )


    return texto.strip()