import hashlib
import re
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document

from config.settings import CHROMA_DIR


# ============================================================
# DIVIDIR DOCUMENTO EN CHUNKS
# ============================================================

def dividir_documento_en_chunks(
    texto: str,
    nombre_documento: str
) -> list[Document]:

    texto = texto.replace(
        "\r\n",
        "\n"
    )

    texto = texto.replace(
        "\r",
        "\n"
    )

    parrafos = re.split(
        r"\n\s*\n",
        texto
    )

    documentos = []

    numero_chunk = 1

    for parrafo in parrafos:

        contenido = parrafo.strip()

        if not contenido:
            continue

        documento = Document(
            page_content=contenido,
            metadata={
                "documento": nombre_documento,
                "chunk": numero_chunk
            }
        )

        documentos.append(
            documento
        )

        numero_chunk += 1

    return documentos


# ============================================================
# GENERAR HASH DEL DOCUMENTO
# ============================================================

def obtener_hash_documento(
    texto: str
) -> str:

    return hashlib.md5(
        texto.encode(
            "utf-8"
        )
    ).hexdigest()


# ============================================================
# CREAR DIRECTORIO CHROMA
# ============================================================

def preparar_directorio_chroma() -> None:

    CHROMA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


# ============================================================
# ELIMINAR COLECCIÓN CHROMA
# ============================================================

def eliminar_coleccion_chroma(
    nombre_coleccion: str
) -> None:

    """
    Elimina únicamente la colección problemática de Chroma.

    No elimina físicamente toda la carpeta CHROMA_DIR.
    Esto evita conflictos con chroma.sqlite3 en Windows.
    """

    try:

        print(
            f"[RAG] Eliminando colección: "
            f"{nombre_coleccion}"
        )

        vectorstore = Chroma(
            collection_name=nombre_coleccion,
            embedding_function=None,
            persist_directory=str(CHROMA_DIR)
        )

        vectorstore.delete_collection()

        print(
            "[RAG] Colección eliminada correctamente."
        )

    except Exception as error:

        print(
            "[RAG] No se pudo eliminar "
            "la colección existente."
        )

        print(
            f"[RAG] Detalle: {error}"
        )


# ============================================================
# INTENTAR CARGAR VECTOR STORE
# ============================================================

def intentar_cargar_vector_store(
    nombre_coleccion: str,
    embeddings,
    hash_actual: str
):

    """
    Intenta cargar una colección existente.

    Devuelve:

        - vectorstore si es válido
        - None si debe reconstruirse
    """

    try:

        print(
            "[RAG] Intentando cargar índice existente: "
            f"{nombre_coleccion}"
        )

        vectorstore = Chroma(
            collection_name=nombre_coleccion,
            embedding_function=embeddings,
            persist_directory=str(CHROMA_DIR)
        )

        cantidad = (
            vectorstore._collection.count()
        )

        # ----------------------------------------------------
        # COLECCIÓN VACÍA
        # ----------------------------------------------------

        if cantidad <= 0:

            print(
                "[RAG] La colección existe "
                "pero está vacía."
            )

            return None

        # ----------------------------------------------------
        # OBTENER METADATOS
        # ----------------------------------------------------

        datos_existentes = (
            vectorstore.get(
                include=[
                    "metadatas"
                ]
            )
        )

        metadatas = (
            datos_existentes.get(
                "metadatas",
                []
            )
        )

        hash_guardado = None

        for metadata in metadatas:

            if not metadata:
                continue

            if (
                "hash_documento"
                in metadata
            ):

                hash_guardado = (
                    metadata[
                        "hash_documento"
                    ]
                )

                break

        # ----------------------------------------------------
        # COMPARAR HASH
        # ----------------------------------------------------

        if (
            hash_guardado
            ==
            hash_actual
        ):

            print(
                "[RAG] Índice existente válido: "
                f"{nombre_coleccion}"
            )

            return vectorstore

        print(
            "[RAG] El documento original cambió."
        )

        print(
            "[RAG] Se debe reconstruir el índice."
        )

        return None

    except Exception as error:

        print(
            "[RAG] El índice existente no es "
            "compatible o está dañado."
        )

        print(
            f"[RAG] Detalle: {error}"
        )

        return None


# ============================================================
# CREAR O CARGAR VECTOR STORE
# ============================================================

def crear_o_cargar_vector_store(
    ruta_documento: Path,
    nombre_coleccion: str,
    nombre_documento: str,
    embeddings
):

    # --------------------------------------------------------
    # VALIDAR DOCUMENTO
    # --------------------------------------------------------

    if not ruta_documento.exists():

        raise FileNotFoundError(
            f"No se encontró el documento: "
            f"{ruta_documento}"
        )

    print(
        "[RAG] Verificando índice: "
        f"{nombre_coleccion}"
    )

    # --------------------------------------------------------
    # LEER DOCUMENTO
    # --------------------------------------------------------

    texto = ruta_documento.read_text(
        encoding="utf-8"
    )

    if not texto.strip():

        raise ValueError(
            f"El documento está vacío: "
            f"{ruta_documento}"
        )

    # --------------------------------------------------------
    # HASH DEL DOCUMENTO
    # --------------------------------------------------------

    hash_actual = (
        obtener_hash_documento(
            texto
        )
    )

    # --------------------------------------------------------
    # GENERAR CHUNKS
    # --------------------------------------------------------

    documentos = (
        dividir_documento_en_chunks(
            texto,
            nombre_documento
        )
    )

    if not documentos:

        raise ValueError(
            "No se pudieron generar chunks "
            f"para el documento: {ruta_documento}"
        )

    # ========================================================
    # PREPARAR DIRECTORIO
    # ========================================================

    preparar_directorio_chroma()

    # ========================================================
    # INTENTAR CARGAR ÍNDICE EXISTENTE
    # ========================================================

    vectorstore = (
        intentar_cargar_vector_store(
            nombre_coleccion=nombre_coleccion,
            embeddings=embeddings,
            hash_actual=hash_actual
        )
    )

    if vectorstore is not None:

        return vectorstore

    # ========================================================
    # SI LA COLECCIÓN NO ES UTILIZABLE
    # ELIMINAR SOLAMENTE LA COLECCIÓN
    # ========================================================

    eliminar_coleccion_chroma(
        nombre_coleccion
    )

    # ========================================================
    # AGREGAR HASH A LOS METADATOS
    # ========================================================

    for documento in documentos:

        documento.metadata[
            "hash_documento"
        ] = hash_actual

    # ========================================================
    # CREAR NUEVO ÍNDICE
    # ========================================================

    print(
        "[RAG] Creando índice: "
        f"{nombre_coleccion}"
    )

    try:

        vectorstore = (
            Chroma.from_documents(
                documents=documentos,
                embedding=embeddings,
                collection_name=nombre_coleccion,
                persist_directory=str(CHROMA_DIR)
            )
        )

    except Exception as error:

        print(
            "[RAG] Error creando el índice Chroma."
        )

        print(
            f"[RAG] Detalle: {error}"
        )

        raise error

    print(
        "[RAG] Índice creado correctamente: "
        f"{nombre_coleccion}"
    )

    return vectorstore