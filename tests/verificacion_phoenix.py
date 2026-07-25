"""Prueba estática de la integración Phoenix sin iniciar Gemini ni el servidor."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

archivos = [
    ROOT / "observability" / "__init__.py",
    ROOT / "observability" / "phoenix_config.py",
    ROOT / "docs" / "observabilidad_phoenix.md",
]

faltantes = [str(p.relative_to(ROOT)) for p in archivos if not p.exists()]
if faltantes:
    raise SystemExit("Faltan archivos Phoenix: " + ", ".join(faltantes))

main = (ROOT / "main.py").read_text(encoding="utf-8")
requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
env_example = (ROOT / ".env.example").read_text(encoding="utf-8")

comprobaciones = {
    "inicialización temprana": "inicializar_phoenix()" in main,
    "contexto en chat": 'canal="chat_texto"' in main,
    "contexto en imagen": 'canal="chat_imagen"' in main,
    "endpoint de estado": '/observabilidad/estado' in main,
    "servidor Phoenix": "arize-phoenix" in requirements,
    "OTEL Phoenix": "arize-phoenix-otel" in requirements,
    "instrumentador LangChain": "openinference-instrumentation-langchain" in requirements,
    "variable PHOENIX_ENABLED": "PHOENIX_ENABLED=" in env_example,
}

fallos = [nombre for nombre, cumple in comprobaciones.items() if not cumple]
if fallos:
    raise SystemExit("Falló la integración Phoenix: " + ", ".join(fallos))

print("OK: integración estática de Phoenix completa.")
