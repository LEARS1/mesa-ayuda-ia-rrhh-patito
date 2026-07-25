# ============================================================
# services/request_service.py
# ============================================================

import re
import uuid

from datetime import datetime, date
from pathlib import Path

from core.state import (
    solicitudes_pendientes,
    solicitudes_ultimas
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

REGISTRO_PATH = (
    BASE_DIR
    / "registro_solicitudes_rrhh.txt"
)


# ============================================================
# CAMPOS OBLIGATORIOS
# ============================================================

CAMPOS_VACACIONES = [
    "nombre",
    "fecha_inicio",
    "fecha_fin",
    "dias",
    "jefe_aprobador"
]


CAMPOS_DEPENDIENTE = [
    "nombre",
    "dependiente",
    "vinculo",
    "documentos_respaldo"
]


# ============================================================
# UTILIDADES
# ============================================================

def normalizar_texto(
    texto: str
) -> str:
    """
    Normaliza un texto para facilitar
    las comparaciones.
    """

    if not texto:
        return ""

    texto = texto.strip().lower()

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto


# ============================================================
# REGISTROS
# ============================================================

def leer_registros() -> list[str]:
    """
    Lee las solicitudes previamente registradas.

    Devuelve una lista donde cada elemento
    representa una solicitud registrada.
    """

    if not REGISTRO_PATH.exists():

        return []


    try:

        with open(
            REGISTRO_PATH,
            "r",
            encoding="utf-8"
        ) as archivo:

            return [

                linea.strip()

                for linea in archivo

                if linea.strip()

            ]


    except OSError:

        return []


# ============================================================
# NUEVO:
# LECTURA ESTRUCTURADA DE SOLICITUDES REGISTRADAS
# ============================================================

def obtener_solicitudes_registradas() -> list[dict]:
    """
    Lee el archivo de registros y convierte
    cada solicitud en un diccionario estructurado.

    Esta función será utilizada posteriormente
    por la herramienta ReAct para que el agente
    pueda consultar las solicitudes registradas.

    Ejemplo de salida:

    [
        {
            "id": "REQ-202607-AB12CD34",
            "fecha_registro": "2026-07-25 14:30:00",
            "tipo": "VACACIONES",
            "colaborador": "Juan Pérez",
            "inicio": "2026-08-10",
            "fin": "2026-08-24",
            "dias": "11",
            "jefe_aprobador": "Carlos López"
        }
    ]
    """

    registros = leer_registros()

    solicitudes = []


    for registro in registros:

        try:

            partes = [

                parte.strip()

                for parte in registro.split("|")

            ]


            if len(partes) < 3:

                continue


            solicitud = {

                "id": partes[0],

                "fecha_registro": partes[1],

                "tipo": partes[2],

                "datos": {}

            }


            # ====================================================
            # SOLICITUD DE VACACIONES
            # ====================================================

            if (

                solicitud["tipo"].upper()

                ==

                "VACACIONES"

            ):

                for parte in partes[3:]:

                    if ":" not in parte:

                        continue


                    clave, valor = (

                        parte.split(
                            ":",
                            1
                        )

                    )


                    clave = (

                        clave
                        .strip()
                        .lower()

                    )


                    valor = (

                        valor
                        .strip()

                    )


                    if clave == "colaborador":

                        solicitud[
                            "datos"
                        ][
                            "nombre"
                        ] = valor


                    elif clave == "inicio":

                        solicitud[
                            "datos"
                        ][
                            "fecha_inicio"
                        ] = valor


                    elif clave == "fin":

                        solicitud[
                            "datos"
                        ][
                            "fecha_fin"
                        ] = valor


                    elif clave == "días":

                        solicitud[
                            "datos"
                        ][
                            "dias"
                        ] = valor


                    elif clave == "jefe aprobador":

                        solicitud[
                            "datos"
                        ][
                            "jefe_aprobador"
                        ] = valor


            # ====================================================
            # SOLICITUD DE DEPENDIENTE
            # ====================================================

            elif (

                solicitud["tipo"].upper()

                ==

                "DEPENDIENTE"

            ):

                for parte in partes[3:]:

                    if ":" not in parte:

                        continue


                    clave, valor = (

                        parte.split(
                            ":",
                            1
                        )

                    )


                    clave = (

                        clave
                        .strip()
                        .lower()

                    )


                    valor = (

                        valor
                        .strip()

                    )


                    if clave == "colaborador":

                        solicitud[
                            "datos"
                        ][
                            "nombre"
                        ] = valor


                    elif clave == "dependiente":

                        solicitud[
                            "datos"
                        ][
                            "dependiente"
                        ] = valor


                    elif clave == "vínculo":

                        solicitud[
                            "datos"
                        ][
                            "vinculo"
                        ] = valor


                    elif clave == "documentos":

                        solicitud[
                            "datos"
                        ][
                            "documentos_respaldo"
                        ] = valor


            solicitudes.append(
                solicitud
            )


        except Exception:

            # Si una línea está corrupta,
            # no se detiene la lectura de
            # las demás solicitudes.

            continue


    return solicitudes


# ============================================================
# FORMATEAR SOLICITUDES PARA EL AGENTE
# ============================================================

def formatear_solicitudes_registradas(
    solicitudes: list[dict]
) -> str:
    """
    Convierte las solicitudes estructuradas
    en un texto fácil de leer para el agente
    y para el usuario.
    """

    if not solicitudes:

        return (

            "No existen solicitudes "
            "registradas actualmente."

        )


    respuesta = (

        "Solicitudes registradas:\n\n"

    )


    for indice, solicitud in enumerate(
        solicitudes,
        start=1
    ):

        respuesta += (

            f"{indice}. "

            f"ID: "
            f"{solicitud.get('id', '')}\n"

            f"   Fecha de registro: "
            f"{solicitud.get('fecha_registro', '')}\n"

            f"   Tipo: "
            f"{solicitud.get('tipo', '')}\n"

        )


        datos = solicitud.get(
            "datos",
            {}
        )


        for clave, valor in datos.items():

            respuesta += (

                f"   {clave}: "
                f"{valor}\n"

            )


        respuesta += "\n"


    return respuesta


# ============================================================
# GENERACIÓN DE ID
# ============================================================

def generar_id_solicitud() -> str:
    """
    Genera un identificador único
    para la solicitud.
    """

    fecha = datetime.now().strftime(
        "%Y%m"
    )


    identificador = (

        uuid.uuid4()
        .hex[:8]
        .upper()

    )


    return (

        f"REQ-{fecha}-{identificador}"

    )


# ============================================================
# VALIDACIÓN DE FECHAS
# ============================================================

MESES_ES = {

    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "setiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12

}


def validar_fecha(
    fecha_texto: str
) -> date | None:
    """
    Convierte fechas numéricas
    a objetos date.
    """

    if not fecha_texto:

        return None


    formatos = [

        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y"

    ]


    for formato in formatos:

        try:

            return datetime.strptime(
                fecha_texto.strip(),
                formato
            ).date()


        except ValueError:

            continue


    return None


def calcular_dias_habiles(
    fecha_inicio: date,
    fecha_fin: date
) -> int:
    """
    Cuenta días de lunes a viernes,
    incluyendo ambos extremos.
    """

    if fecha_fin < fecha_inicio:

        return 0


    dias = 0

    fecha_actual = fecha_inicio


    while fecha_actual <= fecha_fin:

        if fecha_actual.weekday() < 5:

            dias += 1


        fecha_actual = date.fromordinal(

            fecha_actual.toordinal()
            + 1

        )


    return dias


def _crear_fecha_sin_anio(
    dia: int,
    mes: int,
    hoy: date | None = None
) -> date:
    """
    Crea una fecha sin año
    usando el año actual.
    """

    hoy = hoy or date.today()

    anio = hoy.year


    fecha = date(
        anio,
        mes,
        dia
    )


    if fecha < hoy:

        fecha = date(
            anio + 1,
            mes,
            dia
        )


    return fecha


def extraer_fecha_texto(
    texto: str,
    hoy: date | None = None
) -> date | None:
    """
    Reconoce:

    DD/MM/YYYY
    DD-MM-YYYY
    DD de mes
    DD de mes de YYYY
    """

    texto = normalizar_texto(
        texto
    )


    fecha = validar_fecha(
        texto
    )


    if fecha is not None:

        return fecha


    patron = re.fullmatch(

        r"(\d{1,2})\s+de\s+"
        r"([a-záéíóúñ]+)"
        r"(?:\s+de\s+(\d{4}))?",

        texto,

        re.IGNORECASE

    )


    if not patron:

        patron = re.fullmatch(

            r"(\d{1,2})\s+"
            r"([a-záéíóúñ]+)"
            r"(?:\s+(\d{4}))?",

            texto,

            re.IGNORECASE

        )


    if not patron:

        return None


    dia = int(
        patron.group(1)
    )


    mes = MESES_ES.get(

        patron.group(2).lower()

    )


    anio = patron.group(3)


    if mes is None:

        return None


    try:

        if anio:

            return date(

                int(anio),
                mes,
                dia

            )


        return _crear_fecha_sin_anio(

            dia,
            mes,
            hoy

        )


    except ValueError:

        return None


def extraer_rango_fechas(
    texto: str
) -> tuple[str, str]:
    """
    Extrae rangos como:

    del 10 al 24 de agosto

    10 de agosto al 24 de agosto

    10/08/2026 al 24/08/2026
    """

    texto_normalizado = normalizar_texto(
        texto
    )


    hoy = date.today()


    # ========================================================
    # FECHAS NUMÉRICAS
    # ========================================================

    patron_numerico = re.search(

        r"(?:del|desde)?\s*"

        r"(\d{1,2}[/-]\d{1,2}"
        r"(?:[/-]\d{4})?)"

        r"\s+(?:al|hasta)\s+"

        r"(\d{1,2}[/-]\d{1,2}"
        r"(?:[/-]\d{4})?)",

        texto_normalizado,

        re.IGNORECASE

    )


    if patron_numerico:

        inicio_raw = (
            patron_numerico.group(1)
        )


        fin_raw = (
            patron_numerico.group(2)
        )


        def completar_anio(
            valor: str,
            referencia: date
        ) -> str:

            partes = re.split(
                r"[/-]",
                valor
            )


            if len(partes) == 3:

                return valor


            return (

                f"{valor}/"
                f"{referencia.year}"

            )


        inicio = extraer_fecha_texto(

            completar_anio(
                inicio_raw,
                hoy
            )

        )


        fin = extraer_fecha_texto(

            completar_anio(
                fin_raw,
                inicio or hoy
            )

        )


        if inicio and fin:

            return (

                inicio.strftime(
                    "%Y-%m-%d"
                ),

                fin.strftime(
                    "%Y-%m-%d"
                )

            )


    # ========================================================
    # MISMO MES
    # ========================================================

    patron_mismo_mes = re.search(

        r"(?:del|desde)?\s*"

        r"(\d{1,2})\s+"

        r"(?:al|hasta)\s+"

        r"(\d{1,2})\s+de\s+"

        r"([a-záéíóúñ]+)"

        r"(?:\s+de\s+(\d{4}))?",

        texto_normalizado,

        re.IGNORECASE

    )


    if patron_mismo_mes:

        dia_inicio = int(
            patron_mismo_mes.group(1)
        )


        dia_fin = int(
            patron_mismo_mes.group(2)
        )


        mes = MESES_ES.get(

            patron_mismo_mes.group(
                3
            ).lower()

        )


        anio = (
            patron_mismo_mes.group(4)
        )


        if mes:

            try:

                if anio:

                    fecha_inicio = date(

                        int(anio),
                        mes,
                        dia_inicio

                    )


                    fecha_fin = date(

                        int(anio),
                        mes,
                        dia_fin

                    )


                else:

                    fecha_inicio = (
                        _crear_fecha_sin_anio(
                            dia_inicio,
                            mes,
                            hoy
                        )
                    )


                    fecha_fin = date(

                        fecha_inicio.year,
                        mes,
                        dia_fin

                    )


                if fecha_fin >= fecha_inicio:

                    return (

                        fecha_inicio.strftime(
                            "%Y-%m-%d"
                        ),

                        fecha_fin.strftime(
                            "%Y-%m-%d"
                        )

                    )


            except ValueError:

                pass


    # ========================================================
    # DOS FECHAS CON MESES
    # ========================================================

    patron_dos_fechas = re.search(

        r"(?:del|desde)?\s*"

        r"(\d{1,2})\s+de\s+"

        r"([a-záéíóúñ]+)"

        r"(?:\s+de\s+(\d{4}))?"

        r"\s+(?:al|hasta)\s+"

        r"(\d{1,2})\s+de\s+"

        r"([a-záéíóúñ]+)"

        r"(?:\s+de\s+(\d{4}))?",

        texto_normalizado,

        re.IGNORECASE

    )


    if patron_dos_fechas:

        mes_inicio = MESES_ES.get(

            patron_dos_fechas
            .group(2)
            .lower()

        )


        mes_fin = MESES_ES.get(

            patron_dos_fechas
            .group(5)
            .lower()

        )


        if mes_inicio and mes_fin:

            anio_inicio = int(

                patron_dos_fechas
                .group(3)

                or

                hoy.year

            )


            anio_fin = int(

                patron_dos_fechas
                .group(6)

                or

                anio_inicio

            )


            try:

                fecha_inicio = date(

                    anio_inicio,
                    mes_inicio,
                    int(
                        patron_dos_fechas
                        .group(1)
                    )

                )


                fecha_fin = date(

                    anio_fin,
                    mes_fin,
                    int(
                        patron_dos_fechas
                        .group(4)
                    )

                )


                if fecha_fin >= fecha_inicio:

                    return (

                        fecha_inicio.strftime(
                            "%Y-%m-%d"
                        ),

                        fecha_fin.strftime(
                            "%Y-%m-%d"
                        )

                    )


            except ValueError:

                pass


    return "", ""


# ============================================================
# NORMALIZAR FECHA PARA REGISTRO
# ============================================================

def normalizar_fecha(
    fecha_texto: str
) -> str:
    """
    Convierte una fecha válida
    al formato YYYY-MM-DD.
    """

    fecha = validar_fecha(
        fecha_texto
    )


    if fecha is None:

        return fecha_texto


    return fecha.strftime(
        "%Y-%m-%d"
    )


# ============================================================
# DETECCIÓN DE DUPLICADOS
# ============================================================

def existe_solicitud_duplicada(
    tipo: str,
    nombre: str,
    fecha_inicio: str = "",
    fecha_fin: str = "",
    dependiente: str = ""
) -> bool:
    """
    Verifica si existe una solicitud
    igual previamente registrada.
    """

    registros = leer_registros()


    tipo_normalizado = normalizar_texto(
        tipo
    )


    nombre_normalizado = normalizar_texto(
        nombre
    )


    fecha_inicio_normalizada = (

        normalizar_fecha(
            fecha_inicio
        )

    )


    fecha_fin_normalizada = (

        normalizar_fecha(
            fecha_fin
        )

    )


    dependiente_normalizado = (

        normalizar_texto(
            dependiente
        )

    )


    for registro in registros:

        registro_normalizado = (

            normalizar_texto(
                registro
            )

        )


        if tipo_normalizado not in (
            registro_normalizado
        ):

            continue


        if nombre_normalizado not in (
            registro_normalizado
        ):

            continue


        # ====================================================
        # DUPLICADO DE VACACIONES
        # ====================================================

        if tipo_normalizado == "vacaciones":

            misma_fecha_inicio = (

                fecha_inicio_normalizada

                in

                registro_normalizado

            )


            misma_fecha_fin = (

                fecha_fin_normalizada

                in

                registro_normalizado

            )


            if (

                misma_fecha_inicio

                and

                misma_fecha_fin

            ):

                return True


        # ====================================================
        # DUPLICADO DE DEPENDIENTE
        # ====================================================

        elif tipo_normalizado == "dependiente":

            if (

                dependiente_normalizado

                in

                registro_normalizado

            ):

                return True


    return False


# ============================================================
# VALIDACIÓN DE SOLICITUD DE VACACIONES
# ============================================================

def validar_solicitud_vacaciones(
    nombre: str,
    fecha_inicio: str,
    fecha_fin: str,
    dias: int,
    jefe_aprobador: str
) -> list[str]:
    """
    Valida todos los datos obligatorios
    de una solicitud de vacaciones.
    """

    faltantes = []


    if not nombre.strip():

        faltantes.append(
            "nombre del colaborador"
        )


    if not fecha_inicio.strip():

        faltantes.append(
            "fecha de inicio"
        )


    if not fecha_fin.strip():

        faltantes.append(
            "fecha de finalización"
        )


    if dias <= 0:

        faltantes.append(
            "número de días válido"
        )


    if not jefe_aprobador.strip():

        faltantes.append(
            "jefe que aprueba"
        )


    # ========================================================
    # FECHA DE INICIO
    # ========================================================

    fecha_inicio_obj = validar_fecha(
        fecha_inicio
    )


    if fecha_inicio_obj is None:

        if fecha_inicio.strip():

            faltantes.append(
                "fecha de inicio válida"
            )


    else:

        dias_anticipacion = (

            fecha_inicio_obj
            - date.today()
        ).days


        if dias_anticipacion < 15:

            faltantes.append(

                "al menos 15 días "
                "de anticipación"

            )


    # ========================================================
    # FECHA DE FINALIZACIÓN
    # ========================================================

    fecha_fin_obj = validar_fecha(
        fecha_fin
    )


    if fecha_fin_obj is None:

        if fecha_fin.strip():

            faltantes.append(

                "fecha de finalización "
                "válida"

            )


    elif fecha_inicio_obj is not None:

        if fecha_fin_obj < fecha_inicio_obj:

            faltantes.append(

                "fecha de finalización "
                "posterior a la fecha "
                "de inicio"

            )


    return faltantes


# ============================================================
# VALIDACIÓN DE DEPENDIENTE
# ============================================================

def validar_solicitud_dependiente(
    nombre: str,
    dependiente: str,
    vinculo: str,
    documentos_respaldo: str
) -> list[str]:
    """
    Valida los datos obligatorios
    para inscribir un dependiente.
    """

    faltantes = []


    if not nombre.strip():

        faltantes.append(
            "nombre del colaborador"
        )


    if not dependiente.strip():

        faltantes.append(
            "nombre del dependiente"
        )


    if not vinculo.strip():

        faltantes.append(
            "vínculo"
        )


    if not documentos_respaldo.strip():

        faltantes.append(
            "documentos de respaldo"
        )


    return faltantes


# ============================================================
# CONFIRMACIÓN
# ============================================================

def es_confirmacion(
    texto: str
) -> bool:
    """
    Determina si el usuario confirmó
    explícitamente una solicitud.
    """

    confirmaciones_validas = [

        "si",
        "sí",
        "confirmo",
        "confirmar",
        "yes",
        "acepto",
        "de acuerdo",
        "correcto"

    ]


    texto_normalizado = normalizar_texto(
        texto
    )


    return (

        texto_normalizado
        in
        confirmaciones_validas

    )


# ============================================================
# CANCELACIÓN
# ============================================================

def es_cancelacion(
    texto: str
) -> bool:
    """
    Determina si el usuario canceló
    la solicitud.
    """

    cancelaciones_validas = [

        "no",
        "cancelar",
        "cancelo",
        "no confirmar",
        "rechazo"

    ]


    texto_normalizado = normalizar_texto(
        texto
    )


    return (

        texto_normalizado
        in
        cancelaciones_validas

    )


# ============================================================
# CREAR RESUMEN DE SOLICITUD
# ============================================================

def crear_resumen_solicitud_pendiente(
    datos: dict
) -> str:
    """
    Genera el resumen que se muestra
    antes de confirmar.
    """

    tipo = datos.get(
        "tipo",
        ""
    )


    # ========================================================
    # VACACIONES
    # ========================================================

    if tipo == "vacaciones":

        return (

            "\n"

            "Los datos de la solicitud son:\n\n"

            "Tipo: VACACIONES\n\n"

            f"Colaborador: "
            f"{datos.get('nombre', '')}\n\n"

            f"Fecha de inicio: "
            f"{datos.get('fecha_inicio', '')}\n\n"

            f"Fecha de fin: "
            f"{datos.get('fecha_fin', '')}\n\n"

            f"Días: "
            f"{datos.get('dias', '')}\n\n"

            f"Jefe aprobador: "
            f"{datos.get('jefe_aprobador', '')}\n\n"

            "¿Deseas confirmar el registro?\n\n"

            "Responde 'confirmo' "
            "para registrar o "
            "'cancelar' para cancelar."

        )


    # ========================================================
    # DEPENDIENTE
    # ========================================================

    if tipo == "dependiente":

        return (

            "\n"

            "Los datos de la solicitud "
            "son:\n\n"

            "Tipo: INSCRIPCIÓN "
            "DE DEPENDIENTE\n\n"

            f"Colaborador: "
            f"{datos.get('nombre', '')}\n\n"

            f"Dependiente: "
            f"{datos.get('dependiente', '')}\n\n"

            f"Vínculo: "
            f"{datos.get('vinculo', '')}\n\n"

            "Documentos de respaldo:\n"

            f"{datos.get('documentos_respaldo', '')}\n\n"

            "¿Deseas confirmar el registro?\n\n"

            "Responde 'confirmo' "
            "para registrar o "
            "'cancelar' para cancelar."

        )


    return (

        "No se pudo identificar "
        "el tipo de solicitud."

    )


# ============================================================
# REGISTRAR SOLICITUD DE RR. HH.
# ============================================================

def registrar_solicitud_rrhh(
    tipo: str,
    nombre: str,
    fecha_inicio: str = "",
    fecha_fin: str = "",
    dias: int = 0,
    jefe_aprobador: str = "",
    dependiente: str = "",
    vinculo: str = "",
    documentos_respaldo: str = "",
    confirmacion: str = ""
) -> str:
    """
    Valida y registra una solicitud
    de Recursos Humanos.
    """

    tipo_normalizado = normalizar_texto(
        tipo
    )


    # ========================================================
    # VACACIONES
    # ========================================================

    if tipo_normalizado == "vacaciones":

        faltantes = (

            validar_solicitud_vacaciones(

                nombre=nombre,

                fecha_inicio=fecha_inicio,

                fecha_fin=fecha_fin,

                dias=dias,

                jefe_aprobador=jefe_aprobador

            )

        )


        if faltantes:

            return (

                "No se puede registrar "
                "la solicitud.\n\n"

                "Faltan o son inválidos:\n\n"

                "- "

                + "\n- ".join(
                    faltantes
                )

            )


        fecha_inicio = normalizar_fecha(
            fecha_inicio
        )


        fecha_fin = normalizar_fecha(
            fecha_fin
        )


        if existe_solicitud_duplicada(

            tipo="vacaciones",

            nombre=nombre,

            fecha_inicio=fecha_inicio,

            fecha_fin=fecha_fin

        ):

            return (

                "La solicitud parece "
                "estar duplicada. "
                "No se realizará un "
                "nuevo registro."

            )


        if not es_confirmacion(
            confirmacion
        ):

            return (

                "La solicitud no puede "
                "registrarse porque no "
                "se recibió una "
                "confirmación explícita."

            )


        solicitud_id = (
            generar_id_solicitud()
        )


        timestamp = (

            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        )


        registro = (

            f"{solicitud_id} | "

            f"{timestamp} | "

            f"VACACIONES | "

            f"Colaborador: {nombre} | "

            f"Inicio: {fecha_inicio} | "

            f"Fin: {fecha_fin} | "

            f"Días: {dias} | "

            f"Jefe aprobador: "
            f"{jefe_aprobador}"

        )


    # ========================================================
    # DEPENDIENTE
    # ========================================================

    elif tipo_normalizado == "dependiente":

        faltantes = (

            validar_solicitud_dependiente(

                nombre=nombre,

                dependiente=dependiente,

                vinculo=vinculo,

                documentos_respaldo=(
                    documentos_respaldo
                )

            )

        )


        if faltantes:

            return (

                "No se puede registrar "
                "la solicitud.\n\n"

                "Faltan:\n\n"

                "- "

                + "\n- ".join(
                    faltantes
                )

            )


        if existe_solicitud_duplicada(

            tipo="dependiente",

            nombre=nombre,

            dependiente=dependiente

        ):

            return (

                "La solicitud parece "
                "estar duplicada. "
                "No se realizará un "
                "nuevo registro."

            )


        if not es_confirmacion(
            confirmacion
        ):

            return (

                "La solicitud no puede "
                "registrarse porque no "
                "se recibió una "
                "confirmación explícita."

            )


        solicitud_id = (
            generar_id_solicitud()
        )


        timestamp = (

            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        )


        registro = (

            f"{solicitud_id} | "

            f"{timestamp} | "

            f"DEPENDIENTE | "

            f"Colaborador: {nombre} | "

            f"Dependiente: {dependiente} | "

            f"Vínculo: {vinculo} | "

            f"Documentos: "
            f"{documentos_respaldo}"

        )


    else:

        return (

            "Tipo de solicitud no válido. "

            "Utiliza 'vacaciones' o "
            "'dependiente'."

        )


    # ========================================================
    # ESCRITURA DEL REGISTRO
    # ========================================================

    try:

        with open(

            REGISTRO_PATH,

            "a",

            encoding="utf-8"

        ) as archivo:

            archivo.write(

                registro
                + "\n"

            )


        return (

            "Solicitud registrada "
            "correctamente.\n\n"

            f"ID único: "
            f"{solicitud_id}\n"

            f"Fecha y hora: "
            f"{timestamp}"

        )


    except OSError as error:

        return (

            "Error al escribir "
            "la solicitud: "

            f"{error}"

        )


# ============================================================
# EXTRACCIÓN DE DATOS DE VACACIONES
# ============================================================

def extraer_datos_vacaciones(
    texto: str
) -> dict:
    """
    Extrae los datos de una solicitud
    de vacaciones.
    """

    datos = {

        "nombre": "",

        "fecha_inicio": "",

        "fecha_fin": "",

        "dias": 0,

        "jefe_aprobador": ""

    }


    # ========================================================
    # NOMBRE
    # ========================================================

    patron_nombre = re.search(

        r"(?:mi nombre es|"
        r"nombre es|"
        r"nombre del colaborador es|"
        r"colaborador es|"
        r"colaborador:|"
        r"nombre:)"

        r"\s*(.+?)"

        r"(?=,|\.|solicitar|"
        r"quiero|deseo|"
        r"desde|del|$)",

        texto,

        re.IGNORECASE

    )


    if patron_nombre:

        datos["nombre"] = (

            patron_nombre
            .group(1)
            .strip()
            .rstrip(",.")

        )


    # ========================================================
    # FECHAS
    # ========================================================

    (

        datos["fecha_inicio"],

        datos["fecha_fin"]

    ) = extraer_rango_fechas(
        texto
    )


    # ========================================================
    # DÍAS
    # ========================================================

    patron_dias = re.search(

        r"(\d+)\s+d[ií]as",

        texto,

        re.IGNORECASE

    )


    if patron_dias:

        datos["dias"] = int(

            patron_dias
            .group(1)

        )


    if (

        datos["dias"] <= 0

        and

        datos["fecha_inicio"]

        and

        datos["fecha_fin"]

    ):

        fecha_inicio_obj = validar_fecha(

            datos["fecha_inicio"]

        )


        fecha_fin_obj = validar_fecha(

            datos["fecha_fin"]

        )


        if (

            fecha_inicio_obj

            and

            fecha_fin_obj

        ):

            datos["dias"] = (

                calcular_dias_habiles(

                    fecha_inicio_obj,

                    fecha_fin_obj

                )

            )


    # ========================================================
    # JEFE APROBADOR
    # ========================================================

    patron_jefe = re.search(

        r"(?:mi jefe aprobador es|"
        r"jefe aprobador es|"
        r"mi jefe es|"
        r"jefe es|"
        r"jefe aprobador:|"
        r"jefe:)"

        r"\s*(.+?)(?:\.|$)",

        texto,

        re.IGNORECASE

    )


    if patron_jefe:

        datos["jefe_aprobador"] = (

            patron_jefe
            .group(1)
            .strip()
            .rstrip(",.")

        )


    return datos


# ============================================================
# EXTRACCIÓN DE DATOS DE DEPENDIENTE
# ============================================================

def extraer_datos_dependiente(
    texto: str
) -> dict:
    """
    Extrae los datos necesarios
    para registrar un dependiente.
    """

    datos = {

        "nombre": "",

        "dependiente": "",

        "vinculo": "",

        "documentos_respaldo": ""

    }


    # ========================================================
    # NOMBRE DEL COLABORADOR
    # ========================================================

    patron_nombre = re.search(

        r"(?:mi nombre es|"
        r"nombre es|"
        r"nombre del colaborador es|"
        r"colaborador es|"
        r"colaborador:)"

        r"\s*(.+?)"

        r"(?=,|\.|"
        r"quiero|"
        r"deseo|"
        r"inscribir|"
        r"registrar|"
        r"agregar|"
        r"$)",

        texto,

        re.IGNORECASE

    )


    if patron_nombre:

        datos["nombre"] = (

            patron_nombre
            .group(1)
            .strip()
            .rstrip(",.")

        )


    # ========================================================
    # NOMBRE DEL DEPENDIENTE
    # ========================================================

    patron_dependiente = re.search(

        r"(?:dependiente|"
        r"familiar)"

        r"\s*(?:es|:)?\s*"

        r"([A-Za-zÁÉÍÓÚáéíóúÑñ ]+?)"

        r"(?=,|\.|"
        r"vínculo|"
        r"vinculo|"
        r"parentesco|"
        r"documentos|$)",

        texto,

        re.IGNORECASE

    )


    if patron_dependiente:

        datos["dependiente"] = (

            patron_dependiente
            .group(1)
            .strip()

        )


    # ========================================================
    # VÍNCULO
    # ========================================================

    patron_vinculo = re.search(

        r"(?:vínculo|"
        r"vinculo|"
        r"parentesco)"

        r"\s*(?:es|:)?\s*"

        r"([^,.]+)",

        texto,

        re.IGNORECASE

    )


    if patron_vinculo:

        datos["vinculo"] = (

            patron_vinculo
            .group(1)
            .strip()

        )


    # ========================================================
    # DOCUMENTOS
    # ========================================================

    patron_documentos = re.search(

        r"(?:documentos|"
        r"documentos de respaldo)"

        r"\s*(?:son|:)?\s*"

        r"(.+)$",

        texto,

        re.IGNORECASE

    )


    if patron_documentos:

        datos["documentos_respaldo"] = (

            patron_documentos
            .group(1)
            .strip()

        )


    return datos


# ============================================================
# ESTADO ESTRUCTURADO PARA LA INTERFAZ
# ============================================================

def _campos_faltantes_estado(datos: dict) -> list[str]:
    """Devuelve los campos todavía incompletos sin aplicar reglas de negocio."""
    tipo = datos.get("tipo", "")

    if tipo == "vacaciones":
        campos = CAMPOS_VACACIONES
    elif tipo == "dependiente":
        campos = CAMPOS_DEPENDIENTE
    else:
        return []

    faltantes = []
    for campo in campos:
        valor = datos.get(campo)
        if valor in (None, "", 0, False):
            faltantes.append(campo)
    return faltantes


def construir_estado_solicitud(
    datos: dict,
    estado: str = "recopilando_datos",
    solicitud_id: str = "",
    fecha_registro: str = "",
    mensaje: str = ""
) -> dict:
    """Convierte una solicitud interna en una respuesta segura para el frontend."""
    datos_limpios = {
        clave: valor
        for clave, valor in datos.items()
        if clave != "confirmacion"
    }

    faltantes = (
        _campos_faltantes_estado(datos_limpios)
        if estado in {"recopilando_datos", "pendiente_confirmacion"}
        else []
    )

    return {
        "activa": True,
        "id": solicitud_id,
        "estado": estado,
        "tipo": datos_limpios.get("tipo", ""),
        "datos": datos_limpios,
        "campos_faltantes": faltantes,
        "fecha_registro": fecha_registro,
        "mensaje": mensaje
    }


def obtener_estado_solicitud(thread_id: str) -> dict:
    """Obtiene la solicitud pendiente o el último resultado del thread."""
    thread_id = (thread_id or "").strip()

    if not thread_id:
        return {
            "activa": False,
            "estado": "sin_solicitud",
            "tipo": "",
            "datos": {},
            "campos_faltantes": [],
            "id": "",
            "fecha_registro": "",
            "mensaje": ""
        }

    if thread_id in solicitudes_pendientes:
        datos = solicitudes_pendientes[thread_id]
        faltantes = _campos_faltantes_estado(datos)
        estado = "recopilando_datos" if faltantes else "pendiente_confirmacion"
        return construir_estado_solicitud(datos, estado=estado)

    if thread_id in solicitudes_ultimas:
        return dict(solicitudes_ultimas[thread_id])

    return {
        "activa": False,
        "estado": "sin_solicitud",
        "tipo": "",
        "datos": {},
        "campos_faltantes": [],
        "id": "",
        "fecha_registro": "",
        "mensaje": ""
    }


def obtener_resumen_panel(thread_id: str) -> dict:
    """Entrega en una sola respuesta el estado actual y el historial."""
    return {
        "solicitud_actual": obtener_estado_solicitud(thread_id),
        "solicitudes_registradas": obtener_solicitudes_registradas()
    }


# ============================================================
# RELACIÓN DEL MENSAJE CON UNA SOLICITUD PENDIENTE
# ============================================================

def mensaje_relacionado_con_solicitud_pendiente(
    thread_id: str,
    pregunta: str
) -> bool:
    """Determina si el mensaje actual debe continuar el borrador.

    Evita que una consulta informativa, un saludo o una pregunta sobre
    una imagen sea absorbida por una solicitud transaccional pendiente.
    """
    if thread_id not in solicitudes_pendientes:
        return False

    texto = normalizar_texto(pregunta)
    if not texto:
        return False

    if es_confirmacion(texto) or es_cancelacion(texto):
        return True

    # Preguntas claramente informativas deben seguir al orquestador/RAG.
    prefijos_informativos = (
        "como ", "cómo ", "que ", "qué ", "cual ", "cuál ",
        "cuanto ", "cuánto ", "cuantos ", "cuántos ",
        "donde ", "dónde ", "cuando ", "cuándo ", "por que ",
        "por qué ", "explica", "informame", "infórmame"
    )
    if texto.startswith(prefijos_informativos) or "?" in pregunta:
        return False

    palabras_consulta_independiente = (
        "seguro medico", "seguro médico", "beneficios", "bono",
        "referidos", "reclutamiento", "onboarding", "induccion",
        "inducción", "horario", "reglamento", "permiso",
        "imagen", "foto", "formulario", "que dice", "qué dice"
    )
    if any(palabra in texto for palabra in palabras_consulta_independiente):
        return False

    datos = solicitudes_pendientes[thread_id]
    tipo = datos.get("tipo", "")

    if tipo == "vacaciones":
        extraidos = extraer_datos_vacaciones(pregunta)
        if any(extraidos.get(campo) for campo in CAMPOS_VACACIONES):
            return True

        # Respuestas breves con fechas, días o jefe suelen completar el flujo.
        if re.search(r"\d{1,2}[/-]\d{1,2}|\d+\s+d[ií]as|\b(del|desde|hasta|al)\b", texto):
            return True
        if any(palabra in texto for palabra in ("jefe", "aprobador", "mi nombre", "colaborador")):
            return True

        # Nombre o jefe dado como respuesta breve, sin forma interrogativa.
        palabras = pregunta.strip().split()
        if 1 <= len(palabras) <= 5 and all(
            re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ'-]+", palabra)
            for palabra in palabras
        ):
            return True

    elif tipo == "dependiente":
        extraidos = extraer_datos_dependiente(pregunta)
        if any(extraidos.get(campo) for campo in CAMPOS_DEPENDIENTE):
            return True
        if any(
            palabra in texto
            for palabra in (
                "dependiente", "familiar", "vinculo", "vínculo",
                "parentesco", "documentos", "mi nombre", "colaborador"
            )
        ):
            return True

        palabras = pregunta.strip().split()
        if 1 <= len(palabras) <= 5 and all(
            re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ'-]+", palabra)
            for palabra in palabras
        ):
            return True

    return False


# ============================================================
# PROCESAR SOLICITUDES DE ACCIÓN
# ============================================================

def procesar_solicitud_accion(
    thread_id: str,
    pregunta: str
) -> str:
    """
    Procesa solicitudes de:

    - Vacaciones
    - Inscripción de dependientes

    La solicitud se mantiene pendiente
    hasta que todos los datos sean válidos
    y el usuario confirme explícitamente.
    """

    print(
        "\n=========================================="
    )


    print(
        "[ACCION] Procesando solicitud"
    )


    print(
        f"[ACCION] Thread: {thread_id}"
    )


    print(
        "=========================================="
    )


    texto_normalizado = normalizar_texto(
        pregunta
    )


    # ========================================================
    # 1. SOLICITUD PENDIENTE
    # ========================================================

    if thread_id in solicitudes_pendientes:

        print(
            "[ACCION] Existe una "
            "solicitud pendiente"
        )


        datos_pendientes = (

            solicitudes_pendientes[
                thread_id
            ]

        )


        if not mensaje_relacionado_con_solicitud_pendiente(
            thread_id,
            pregunta
        ):
            print(
                "[ACCION] Mensaje independiente; "
                "el borrador se conserva sin cambios"
            )
            return (
                "Tu solicitud pendiente se mantiene guardada, pero este "
                "mensaje parece corresponder a otra consulta. Puedes "
                "continuar la solicitud con los datos faltantes, escribir "
                "'confirmo' o escribir 'cancelar'."
            )


        # ====================================================
        # CONFIRMACIÓN
        # ====================================================

        if es_confirmacion(
            pregunta
        ):

            print(
                "[ACCION] Confirmación recibida"
            )


            datos_pendientes[
                "confirmacion"
            ] = "confirmo"


            resultado = (

                registrar_solicitud_rrhh(

                    **datos_pendientes

                )

            )


            if (

                "registrada correctamente"

                in

                normalizar_texto(
                    resultado
                )

            ):

                patron_id = re.search(
                    r"ID único:\s*([^\s]+)",
                    resultado,
                    re.IGNORECASE
                )

                patron_fecha = re.search(
                    r"Fecha y hora:\s*(.+)$",
                    resultado,
                    re.IGNORECASE | re.MULTILINE
                )

                solicitud_id = (
                    patron_id.group(1).strip()
                    if patron_id
                    else ""
                )

                fecha_registro = (
                    patron_fecha.group(1).strip()
                    if patron_fecha
                    else datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )

                solicitudes_ultimas[thread_id] = (
                    construir_estado_solicitud(
                        datos_pendientes,
                        estado="registrada",
                        solicitud_id=solicitud_id,
                        fecha_registro=fecha_registro,
                        mensaje="Solicitud registrada correctamente."
                    )
                )

                del solicitudes_pendientes[
                    thread_id
                ]


            return resultado


        # ====================================================
        # CANCELACIÓN
        # ====================================================

        if es_cancelacion(
            pregunta
        ):

            print(
                "[ACCION] Solicitud cancelada"
            )


            solicitudes_ultimas[thread_id] = (
                construir_estado_solicitud(
                    datos_pendientes,
                    estado="cancelada",
                    mensaje=(
                        "La solicitud fue cancelada y no se registró."
                    )
                )
            )


            del solicitudes_pendientes[
                thread_id
            ]


            return (

                "La solicitud ha sido "
                "cancelada. No se realizó "
                "ningún registro."

            )


        # ====================================================
        # COMPLETAR DATOS PENDIENTES
        # ====================================================

        tipo = datos_pendientes.get(
            "tipo"
        )


        if tipo == "vacaciones":

            nuevos_datos = (

                extraer_datos_vacaciones(
                    pregunta
                )

            )


            for campo in CAMPOS_VACACIONES:

                if (

                    not datos_pendientes.get(
                        campo
                    )

                    and

                    nuevos_datos.get(
                        campo
                    )

                ):

                    datos_pendientes[
                        campo
                    ] = nuevos_datos[
                        campo
                    ]


        elif tipo == "dependiente":

            nuevos_datos = (

                extraer_datos_dependiente(
                    pregunta
                )

            )


            for campo in CAMPOS_DEPENDIENTE:

                if (

                    not datos_pendientes.get(
                        campo
                    )

                    and

                    nuevos_datos.get(
                        campo
                    )

                ):

                    datos_pendientes[
                        campo
                    ] = nuevos_datos[
                        campo
                    ]


        # ====================================================
        # VALIDAR DATOS ACTUALIZADOS
        # ====================================================

        if tipo == "vacaciones":

            faltantes = (

                validar_solicitud_vacaciones(

                    nombre=datos_pendientes[
                        "nombre"
                    ],

                    fecha_inicio=(
                        datos_pendientes[
                            "fecha_inicio"
                        ]
                    ),

                    fecha_fin=(
                        datos_pendientes[
                            "fecha_fin"
                        ]
                    ),

                    dias=datos_pendientes[
                        "dias"
                    ],

                    jefe_aprobador=(
                        datos_pendientes[
                            "jefe_aprobador"
                        ]
                    )

                )

            )


        else:

            faltantes = (

                validar_solicitud_dependiente(

                    nombre=datos_pendientes[
                        "nombre"
                    ],

                    dependiente=(
                        datos_pendientes[
                            "dependiente"
                        ]
                    ),

                    vinculo=datos_pendientes[
                        "vinculo"
                    ],

                    documentos_respaldo=(
                        datos_pendientes[
                            "documentos_respaldo"
                        ]
                    )

                )

            )


        if faltantes:

            return (

                "La solicitud todavía "
                "necesita la siguiente "
                "información:\n\n"

                "- "

                + "\n- ".join(
                    faltantes
                )

            )


        return (

            crear_resumen_solicitud_pendiente(

                datos_pendientes

            )

        )


    # ========================================================
    # 2. DETECTAR TIPO DE SOLICITUD
    # ========================================================

    es_vacaciones = (

        "vacaciones"
        in texto_normalizado

        or

        "vacacion"
        in texto_normalizado

    )


    es_dependiente = (

        (

            "dependiente"
            in texto_normalizado

        )

        or

        (

            "familiar"
            in texto_normalizado

        )

        or

        (

            "inscribir"
            in texto_normalizado

            and

            (

                "seguro"
                in texto_normalizado

                or

                "beneficio"
                in texto_normalizado

            )

        )

    )


    # ========================================================
    # 3. SOLICITUD DE VACACIONES
    # ========================================================

    if es_vacaciones:

        nuevos_datos = (

            extraer_datos_vacaciones(
                pregunta
            )

        )


        datos = {

            "tipo": "vacaciones",

            "nombre": nuevos_datos[
                "nombre"
            ],

            "fecha_inicio": nuevos_datos[
                "fecha_inicio"
            ],

            "fecha_fin": nuevos_datos[
                "fecha_fin"
            ],

            "dias": nuevos_datos[
                "dias"
            ],

            "jefe_aprobador": nuevos_datos[
                "jefe_aprobador"
            ],

            "dependiente": "",

            "vinculo": "",

            "documentos_respaldo": "",

            "confirmacion": ""

        }


        faltantes = (

            validar_solicitud_vacaciones(

                nombre=datos[
                    "nombre"
                ],

                fecha_inicio=datos[
                    "fecha_inicio"
                ],

                fecha_fin=datos[
                    "fecha_fin"
                ],

                dias=datos[
                    "dias"
                ],

                jefe_aprobador=datos[
                    "jefe_aprobador"
                ]

            )

        )


        if faltantes:

            solicitudes_pendientes[
                thread_id
            ] = datos


            return (

                "Para continuar con "
                "la solicitud de "
                "vacaciones necesito:\n\n"

                "- "

                + "\n- ".join(
                    faltantes
                )

            )


        if existe_solicitud_duplicada(

            tipo="vacaciones",

            nombre=datos[
                "nombre"
            ],

            fecha_inicio=datos[
                "fecha_inicio"
            ],

            fecha_fin=datos[
                "fecha_fin"
            ]

        ):

            return (

                "La solicitud parece "
                "estar duplicada. "
                "No se realizará un "
                "nuevo registro."

            )


        solicitudes_ultimas.pop(
            thread_id,
            None
        )


        solicitudes_pendientes[
            thread_id
        ] = datos


        return (

            crear_resumen_solicitud_pendiente(

                datos

            )

        )


    # ========================================================
    # 4. SOLICITUD DE DEPENDIENTE
    # ========================================================

    if es_dependiente:

        nuevos_datos = (

            extraer_datos_dependiente(
                pregunta
            )

        )


        datos = {

            "tipo": "dependiente",

            "nombre": nuevos_datos[
                "nombre"
            ],

            "fecha_inicio": "",

            "fecha_fin": "",

            "dias": 0,

            "jefe_aprobador": "",

            "dependiente": nuevos_datos[
                "dependiente"
            ],

            "vinculo": nuevos_datos[
                "vinculo"
            ],

            "documentos_respaldo": (
                nuevos_datos[
                    "documentos_respaldo"
                ]
            ),

            "confirmacion": ""

        }


        faltantes = (

            validar_solicitud_dependiente(

                nombre=datos[
                    "nombre"
                ],

                dependiente=datos[
                    "dependiente"
                ],

                vinculo=datos[
                    "vinculo"
                ],

                documentos_respaldo=datos[
                    "documentos_respaldo"
                ]

            )

        )


        if faltantes:

            solicitudes_pendientes[
                thread_id
            ] = datos


            return (

                "Para continuar con "
                "la inscripción del "
                "dependiente necesito:\n\n"

                "- "

                + "\n- ".join(
                    faltantes
                )

            )


        if existe_solicitud_duplicada(

            tipo="dependiente",

            nombre=datos[
                "nombre"
            ],

            dependiente=datos[
                "dependiente"
            ]

        ):

            return (

                "La solicitud parece "
                "estar duplicada. "
                "No se realizará un "
                "nuevo registro."

            )


        solicitudes_ultimas.pop(
            thread_id,
            None
        )


        solicitudes_pendientes[
            thread_id
        ] = datos


        return (

            crear_resumen_solicitud_pendiente(

                datos

            )

        )


    # ========================================================
    # 5. RESPUESTA GENERAL
    # ========================================================

    return (

        "Puedo ayudarte a registrar:\n\n"

        "• Solicitudes de vacaciones\n"

        "• Inscripción de dependientes\n\n"

        "Indícame los datos de la solicitud."

    )