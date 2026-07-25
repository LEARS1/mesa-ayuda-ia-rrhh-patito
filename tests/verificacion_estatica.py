"""Verificación estática mínima sin realizar llamadas a Gemini."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

OBLIGATORIOS = [
    ROOT / "main.py",
    ROOT / "README.md",
    ROOT / ".env.example",
    ROOT / "requirements.txt",
    ROOT / "data" / "01_Beneficios_Compensaciones.txt",
    ROOT / "data" / "02_Reglamento_Interno.txt",
    ROOT / "data" / "03_Reclutamiento_Onboarding.txt",
    ROOT / "docs" / "arquitectura.md",
    ROOT / "docs" / "ejemplos_pruebas.md",
    ROOT / "docs" / "observabilidad_phoenix.md",
    ROOT / "observability" / "phoenix_config.py",
    ROOT / "tests" / "imagenes" / "formulario_dependiente_prueba.png",
]

faltantes = [str(ruta.relative_to(ROOT)) for ruta in OBLIGATORIOS if not ruta.exists()]
if faltantes:
    raise SystemExit("Faltan archivos obligatorios: " + ", ".join(faltantes))

print("OK: estructura y entregables mínimos presentes.")
