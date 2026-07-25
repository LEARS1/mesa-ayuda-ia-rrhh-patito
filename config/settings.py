import os

from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# CARGAR VARIABLES DE ENTORNO
# ============================================================

load_dotenv()


# ============================================================
# DIRECTORIOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

CHROMA_DIR = BASE_DIR / "chroma_db"

UPLOADS_DIR = BASE_DIR / "uploads"

REGISTRO_PATH = (
    BASE_DIR / "registro_solicitudes_rrhh.txt"
)


DATA_DIR.mkdir(
    exist_ok=True
)

CHROMA_DIR.mkdir(
    exist_ok=True
)

UPLOADS_DIR.mkdir(
    exist_ok=True
)


# ============================================================
# API KEY
# ============================================================

GOOGLE_API_KEY = os.getenv(
    "GOOGLE_API_KEY"
)


if not GOOGLE_API_KEY:

    raise RuntimeError(
        "No se encontró GOOGLE_API_KEY. "
        "Configure la clave en el archivo .env"
    )


# ============================================================
# MODELO GENERAL
# ============================================================

MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)


MODEL_NAME = MODEL_NAME.strip()


if MODEL_NAME.startswith(
    "GEMINI_MODEL="
):

    MODEL_NAME = MODEL_NAME.replace(
        "GEMINI_MODEL=",
        ""
    )


if MODEL_NAME.startswith(
    "models/"
):

    MODEL_NAME = MODEL_NAME.replace(
        "models/",
        ""
    )


# ============================================================
# MODELO MULTIMODAL
# ============================================================

VISION_MODEL_NAME = os.getenv(
    "GEMINI_VISION_MODEL",
    "gemini-3.5-flash-lite"
)


VISION_MODEL_NAME = (
    VISION_MODEL_NAME.strip()
)


if VISION_MODEL_NAME.startswith(
    "GEMINI_VISION_MODEL="
):

    VISION_MODEL_NAME = (
        VISION_MODEL_NAME.replace(
            "GEMINI_VISION_MODEL=",
            ""
        )
    )


if VISION_MODEL_NAME.startswith(
    "models/"
):

    VISION_MODEL_NAME = (
        VISION_MODEL_NAME.replace(
            "models/",
            ""
        )
    )


# ============================================================
# MODELO DE EMBEDDINGS
# ============================================================

EMBEDDING_MODEL = os.getenv(
    "GEMINI_EMBEDDING_MODEL",
    "gemini-embedding-2"
)


EMBEDDING_MODEL = (
    EMBEDDING_MODEL.strip()
)


if EMBEDDING_MODEL.startswith(
    "models/"
):

    EMBEDDING_MODEL = (
        EMBEDDING_MODEL.replace(
            "models/",
            ""
        )
    )


# ============================================================
# CONFIGURACIÓN
# ============================================================

print(
    f"[CONFIG] Modelo general: "
    f"{MODEL_NAME}"
)


print(
    f"[CONFIG] Modelo visión: "
    f"{VISION_MODEL_NAME}"
)


print(
    f"[CONFIG] Embeddings: "
    f"{EMBEDDING_MODEL}"
)