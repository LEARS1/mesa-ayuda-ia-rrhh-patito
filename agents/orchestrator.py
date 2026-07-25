import re

from core.constants import SYSTEM_PROMPT_ORQUESTADOR
from core.state import contexto_multimodal, solicitudes_pendientes
from utils.helpers import (
    convertir_contenido_a_texto,
    normalizar_texto
)
from agents.multimodal_agent import es_pregunta_sobre_imagen


# ============================================================
# CONSTANTES
# ============================================================

CONFIRMACIONES = {
    "si",
    "sí",
    "confirmo",
    "confirmar",
    "yes",
    "acepto",
    "de acuerdo",
    "correcto",
    "proceder",
    "adelante"
}


CANCELACIONES = {
    "no",
    "cancelar",
    "cancelo",
    "no confirmar",
    "rechazo",
    "cancelar solicitud",
    "no deseo continuar",
    "no quiero continuar"
}


# ============================================================
# UTILIDADES
# ============================================================

def normalizar_consulta(texto: str) -> str:

    return normalizar_texto(
        texto
    ).strip().lower()


# ============================================================
# DETECTAR CONFIRMACIÓN
# ============================================================

def es_confirmacion(
    texto: str
) -> bool:

    texto_normalizado = normalizar_consulta(
        texto
    )

    return texto_normalizado in CONFIRMACIONES


# ============================================================
# DETECTAR CANCELACIÓN
# ============================================================

def es_cancelacion(
    texto: str
) -> bool:

    texto_normalizado = normalizar_consulta(
        texto
    )

    return texto_normalizado in CANCELACIONES


# ============================================================
# DETECTAR CONSULTA INFORMATIVA
# ============================================================

def es_consulta_informativa(
    pregunta: str
) -> bool:

    texto = normalizar_consulta(
        pregunta
    )

    patrones = [

        # ----------------------------------------------------
        # SOLICITUDES DE INFORMACIÓN
        # ----------------------------------------------------

        r"\bpuedo solicitar\b",
        r"\bse puede solicitar\b",
        r"\bes posible solicitar\b",

        r"\bcómo puedo solicitar\b",
        r"\bcomo puedo solicitar\b",

        r"\bcómo se solicita\b",
        r"\bcomo se solicita\b",

        r"\bcómo solicitar\b",
        r"\bcomo solicitar\b",

        r"\bcómo puedo pedir\b",
        r"\bcomo puedo pedir\b",

        r"\bcómo se pide\b",
        r"\bcomo se pide\b",

        # ----------------------------------------------------
        # REQUISITOS
        # ----------------------------------------------------

        r"\bqué requisitos necesito\b",
        r"\bque requisitos necesito\b",

        r"\bcuáles son los requisitos\b",
        r"\bcuales son los requisitos\b",

        r"\bqué documentos necesito\b",
        r"\bque documentos necesito\b",

        r"\bqué necesito para solicitar\b",
        r"\bque necesito para solicitar\b",

        r"\bqué debo hacer para solicitar\b",
        r"\bque debo hacer para solicitar\b",

        # ----------------------------------------------------
        # PROCESOS
        # ----------------------------------------------------

        r"\bcuál es el proceso\b",
        r"\bcual es el proceso\b",

        r"\bcuál es el procedimiento\b",
        r"\bcual es el procedimiento\b",

        r"\bcuál es el trámite\b",
        r"\bcual es el tramite\b",

        # ----------------------------------------------------
        # CONSULTAS GENERALES
        # ----------------------------------------------------

        r"\bquiero saber\b",

        r"\bnecesito información\b",
        r"\bnecesito informacion\b",

        r"\binformación sobre\b",
        r"\binformacion sobre\b",

        r"\bexplícame\b",
        r"\bexplicame\b",

        r"\bpuedes explicar(?:me)?\b",

        r"\bqué es\b",
        r"\bque es\b",

        r"\bqué significa\b",
        r"\bque significa\b",

        # ----------------------------------------------------
        # PREGUNTAS DIRECTAS
        # ----------------------------------------------------

        r"\bcuánto\b",
        r"\bcuanto\b",

        r"\bcuántos\b",
        r"\bcuantos\b",

        r"\bcuándo\b",
        r"\bcuando\b",

        r"\bdónde\b",
        r"\bdonde\b",

        r"\bpor qué\b",
        r"\bporque\b",

        # ----------------------------------------------------
        # INICIO DE PREGUNTA
        # ----------------------------------------------------

        r"^¿?\s*(?:"
        r"qué|que|"
        r"cuál|cual|"
        r"cómo|como|"
        r"cuándo|cuando|"
        r"dónde|donde|"
        r"quién|quien|"
        r"cuánto|cuanto|"
        r"por qué|porque|"
        r"puedo|"
        r"se puede|"
        r"es posible|"
        r"hay"
        r")\b"

    ]

    return any(
        re.search(
            patron,
            texto
        )
        for patron in patrones
    )


# ============================================================
# DETECTAR INTENCIÓN DE ACCIÓN
# ============================================================

def contiene_intencion_de_accion(
    pregunta: str
) -> bool:

    texto = normalizar_consulta(
        pregunta
    )

    # Una consulta informativa nunca debe convertirse
    # automáticamente en una acción nueva.
    if es_consulta_informativa(
        texto
    ):

        return False


    patrones = [

        # ----------------------------------------------------
        # ACCIONES GENERALES
        # ----------------------------------------------------

        r"\bregistrar(?:me|rme)?\b",

        r"\bcrear(?: una)? solicitud\b",

        r"\bgenerar una solicitud\b",

        r"\benviar una solicitud\b",

        r"\bingresar(?: una)? solicitud\b",

        r"\bguardar(?: la| mi)? solicitud\b",

        r"\bguardar\b",

        r"\bgrabar\b",

        # ----------------------------------------------------
        # INTENCIÓN EXPLÍCITA
        # ----------------------------------------------------

        r"\bquiero solicitar\b",
        r"\bdeseo solicitar\b",
        r"\bnecesito solicitar\b",

        r"\bsolicito\b",

        r"\bquiero pedir\b",
        r"\bdeseo pedir\b",
        r"\bnecesito pedir\b",

        r"\bquiero registrar\b",
        r"\bdeseo registrar\b",
        r"\bnecesito registrar\b",

        r"\bquiero ingresar\b",
        r"\bdeseo ingresar\b",
        r"\bnecesito ingresar\b",

        r"\bquiero crear\b",
        r"\bdeseo crear\b",
        r"\bnecesito crear\b",

        # ----------------------------------------------------
        # PROCESAMIENTO
        # ----------------------------------------------------

        r"\bejecutar\b",
        r"\bejecuta\b",

        r"\bprocesar\b",
        r"\bprocesa\b",

        r"\btramitar\b",
        r"\btramita\b",

        # ----------------------------------------------------
        # VACACIONES
        # ----------------------------------------------------

        r"\bquiero tomar mis vacaciones\b",
        r"\bdeseo tomar mis vacaciones\b",
        r"\bnecesito tomar mis vacaciones\b",

        r"\bquiero pedir vacaciones\b",
        r"\bdeseo pedir vacaciones\b",
        r"\bnecesito pedir vacaciones\b",

        r"\bquiero mis vacaciones\b",
        r"\bdeseo mis vacaciones\b",

        r"\bquiero salir de vacaciones\b",

        r"\bsolicitar mis vacaciones\b",
        r"\bsolicitar vacaciones\b",

        r"\bregistrar mis vacaciones\b",
        r"\bregistrar vacaciones\b",

        r"\bingresar mis vacaciones\b",

        r"\bcrear solicitud de vacaciones\b",

        r"\bsolicitud de vacaciones\b",

        # ----------------------------------------------------
        # DEPENDIENTES
        # ----------------------------------------------------

        r"\bregistrar dependiente\b",
        r"\bregistrar a mi dependiente\b",

        r"\binscribir dependiente\b",
        r"\binscribir a mi dependiente\b",

        r"\bagregar dependiente\b",
        r"\bagregar a mi dependiente\b",

        r"\bquiero agregar a mi "
        r"(?:hijo|hija|pareja|conyuge|cónyuge)\b",

        r"\bdeseo agregar a mi "
        r"(?:hijo|hija|pareja|conyuge|cónyuge)\b",

        r"\bquiero inscribir a mi "
        r"(?:hijo|hija|pareja|conyuge|cónyuge)\b"

    ]

    return any(
        re.search(
            patron,
            texto
        )
        for patron in patrones
    )


# ============================================================
# DETECTAR CATEGORÍAS
# ============================================================

def detectar_categorias_por_reglas(
    pregunta: str
) -> list:

    texto = normalizar_consulta(
        pregunta
    )

    categorias = []


    # ========================================================
    # BENEFICIOS
    # ========================================================

    palabras_beneficios = [

        "seguro medico",
        "seguro médico",
        "seguro corporativo",
        "seguro de salud",

        "dependiente",
        "dependientes",

        "pareja",
        "conyuge",
        "cónyuge",

        "familiar",
        "hijo",
        "hija",

        "beneficio",
        "beneficios",

        "bono",
        "bonos",

        "compensacion",
        "compensación",

        "salario",

        "remuneracion",
        "remuneración"

    ]


    if any(
        palabra in texto
        for palabra in palabras_beneficios
    ):

        categorias.append(
            "beneficios"
        )


    # ========================================================
    # POLÍTICAS
    # ========================================================

    palabras_politicas = [

        "vacaciones",
        "vacacion",

        "permiso",
        "permisos",

        "permiso no remunerado",

        "licencia",

        "codigo de conducta",
        "código de conducta",

        "reglamento interno",

        "conducta",

        "horario laboral",

        "faltas disciplinarias"

    ]


    if any(
        palabra in texto
        for palabra in palabras_politicas
    ):

        categorias.append(
            "politicas"
        )


    # ========================================================
    # RECLUTAMIENTO Y ONBOARDING
    # ========================================================

    palabras_onboarding = [

        "reclutamiento",

        "seleccion",
        "selección",

        "entrevista",

        "referido",
        "referidos",
        "referir",

        "onboarding",

        "induccion",
        "inducción",

        "nuevo ingreso",

        "nuevo colaborador"

    ]


    if any(
        palabra in texto
        for palabra in palabras_onboarding
    ):

        categorias.append(
            "onboarding"
        )


    return list(
        dict.fromkeys(
            categorias
        )
    )


# ============================================================
# DETECTAR DATO CONCRETO DE CONTINUACIÓN
# ============================================================

def _tiene_dato_concreto_de_continuacion(
    pregunta: str,
    datos_pendientes: dict
) -> bool:

    texto = normalizar_consulta(
        pregunta
    )

    tipo = (
        datos_pendientes
        .get(
            "tipo",
            ""
        )
        .strip()
        .lower()
    )


    # ========================================================
    # VACACIONES
    # ========================================================

    if tipo == "vacaciones":

        patrones_fecha = [

            # ------------------------------------------------
            # Del 10 al 24 de agosto
            # ------------------------------------------------

            r"\bdel\s+"
            r"\d{1,2}\s+"
            r"(?:al|hasta)\s+"
            r"\d{1,2}\s+"
            r"de\s+"
            r"[a-záéíóúñ]+",

            # ------------------------------------------------
            # 10 al 24 de agosto
            # ------------------------------------------------

            r"\b\d{1,2}\s+"
            r"(?:al|hasta)\s+"
            r"\d{1,2}\s+"
            r"de\s+"
            r"[a-záéíóúñ]+",

            # ------------------------------------------------
            # Desde el 10 de agosto hasta el 24 de agosto
            # ------------------------------------------------

            r"\bdesde\s+"
            r"(?:el\s+)?"
            r"\d{1,2}\s+"
            r"de\s+"
            r"[a-záéíóúñ]+\s+"
            r"(?:hasta|al)\s+"
            r"(?:el\s+)?"
            r"\d{1,2}\s+"
            r"de\s+"
            r"[a-záéíóúñ]+",

            # ------------------------------------------------
            # 10/08 al 24/08
            # 10/08/2026 al 24/08/2026
            # ------------------------------------------------

            r"\b\d{1,2}[/-]\d{1,2}"
            r"(?:[/-]\d{4})?"
            r"\s+"
            r"(?:al|hasta)"
            r"\s+"
            r"\d{1,2}[/-]\d{1,2}"
            r"(?:[/-]\d{4})?",

            # ------------------------------------------------
            # Desde 10/08 hasta 24/08
            # ------------------------------------------------

            r"\bdesde\s+"
            r"\d{1,2}[/-]\d{1,2}"
            r"(?:[/-]\d{4})?"
            r"\s+"
            r"(?:hasta|al)"
            r"\s+"
            r"\d{1,2}[/-]\d{1,2}"
            r"(?:[/-]\d{4})?"

        ]


        patrones_dias = [

            r"\b\d+\s+d[ií]as\b",

            r"\bpor\s+\d+\s+d[ií]as\b",

            r"\bdurante\s+\d+\s+d[ií]as\b"

        ]


        patrones_datos = [

            r"\b(?:mi nombre es|nombre:)\s+.+",

            r"\b(?:mi jefe es|jefe:|aprobador:)\s+.+"

        ]


        if any(
            re.search(
                patron,
                texto
            )
            for patron in patrones_fecha
        ):

            print(
                "[ORQUESTADOR] "
                "Rango de fechas detectado como dato de solicitud"
            )

            return True


        if any(
            re.search(
                patron,
                texto
            )
            for patron in patrones_dias
        ):

            print(
                "[ORQUESTADOR] "
                "Cantidad de días detectada como dato de solicitud"
            )

            return True


        if any(
            re.search(
                patron,
                texto
            )
            for patron in patrones_datos
        ):

            return True


    # ========================================================
    # DEPENDIENTE
    # ========================================================

    if tipo == "dependiente":

        patrones = [

            r"\b(?:mi nombre es|nombre:|colaborador:)\s+.+",

            r"\b(?:dependiente|familiar)"
            r"\s*(?:es|:)\s*.+",

            r"\b(?:vínculo|vinculo|parentesco)"
            r"\s*(?:es|:)\s*.+",

            r"\bdocumentos"
            r"(?: de respaldo)?"
            r"\s*(?:son|:)\s*.+"

        ]


        return any(
            re.search(
                patron,
                texto
            )
            for patron in patrones
        )


    return False


# ============================================================
# DETECTAR CONTINUACIÓN
# ============================================================

def es_continuacion_de_solicitud_pendiente(
    pregunta: str,
    datos_pendientes: dict
) -> bool:

    return _tiene_dato_concreto_de_continuacion(
        pregunta,
        datos_pendientes
    )


# ============================================================
# CLASIFICAR CONSULTA
# ============================================================

def clasificar_consulta(
    pregunta: str,
    thread_id: str,
    llm
) -> list:

    texto = pregunta.strip()


    # ========================================================
    # 1. CONFIRMACIÓN
    # ========================================================

    if es_confirmacion(
        texto
    ):

        print(
            "[ORQUESTADOR] "
            "Confirmación detectada"
        )

        return [
            "accion"
        ]


    # ========================================================
    # 2. CANCELACIÓN
    # ========================================================

    if es_cancelacion(
        texto
    ):

        print(
            "[ORQUESTADOR] "
            "Cancelación detectada"
        )

        return [
            "accion"
        ]


    # ========================================================
    # 3. IMAGEN
    # ========================================================

    if (
        thread_id in contexto_multimodal
        and
        es_pregunta_sobre_imagen(
            texto
        )
    ):

        print(
            "[ORQUESTADOR] "
            "Consulta sobre imagen detectada"
        )

        return [
            "imagen"
        ]


    # ========================================================
    # 4. ANALIZAR CONSULTA ACTUAL
    # ========================================================

    categorias = detectar_categorias_por_reglas(
        texto
    )

    es_informativa = es_consulta_informativa(
        texto
    )

    tiene_accion = contiene_intencion_de_accion(
        texto
    )


    # ========================================================
    # 5. CONTINUACIÓN DE SOLICITUD PENDIENTE
    # ========================================================

    if thread_id in solicitudes_pendientes:

        datos_pendientes = solicitudes_pendientes.get(
            thread_id
        )


        if (
            isinstance(
                datos_pendientes,
                dict
            )
            and
            es_continuacion_de_solicitud_pendiente(
                texto,
                datos_pendientes
            )
        ):

            print(
                "[ORQUESTADOR] "
                "Continuación válida de solicitud pendiente detectada"
            )

            print(
                "[ORQUESTADOR] "
                f"Datos pendientes: "
                f"{list(datos_pendientes.keys())}"
            )

            return [
                "accion"
            ]


    # ========================================================
    # 6. CONSULTA INFORMATIVA
    # ========================================================

    if es_informativa:

        print(
            "[ORQUESTADOR] "
            "Consulta informativa detectada"
        )


        if categorias:

            print(
                "[ORQUESTADOR] "
                f"Categorías detectadas: "
                f"{categorias}"
            )

            return list(
                dict.fromkeys(
                    categorias
                )
            )


    # ========================================================
    # 7. ACCIÓN NUEVA EXPLÍCITA
    # ========================================================

    if tiene_accion:

        print(
            "[ORQUESTADOR] "
            "Intención de acción detectada"
        )


        if "accion" not in categorias:

            categorias.append(
                "accion"
            )


        categorias = list(
            dict.fromkeys(
                categorias
            )
        )


        print(
            "[ORQUESTADOR] "
            f"Categorías detectadas: "
            f"{categorias}"
        )


        return categorias


    # ========================================================
    # 8. CONSULTA TEMÁTICA
    # ========================================================

    if categorias:

        print(
            "[ORQUESTADOR] "
            f"Categorías detectadas: "
            f"{categorias}"
        )

        return list(
            dict.fromkeys(
                categorias
            )
        )


    # ========================================================
    # 9. RESPALDO CON GEMINI
    # ========================================================

    prompt = (

        SYSTEM_PROMPT_ORQUESTADOR

        + "\n\nCONSULTA DEL USUARIO:\n"

        + texto

        + "\n\nCATEGORÍA:"

    )


    respuesta = llm.invoke(
        prompt
    )


    categoria = convertir_contenido_a_texto(
        respuesta.content
    )


    categoria = re.sub(
        r"[^a-záéíóúñ]",
        "",
        categoria.strip().lower()
    )


    # ========================================================
    # 10. INTERPRETAR RESPUESTA DE GEMINI
    # ========================================================

    if "beneficio" in categoria:

        return [
            "beneficios"
        ]


    if "politica" in categoria:

        return [
            "politicas"
        ]


    if "onboarding" in categoria:

        return [
            "onboarding"
        ]


    if "imagen" in categoria:

        return [
            "imagen"
        ]


    if "accion" in categoria:

        return [
            "accion"
        ]


    # ========================================================
    # 11. FUERA DE ALCANCE
    # ========================================================

    return []