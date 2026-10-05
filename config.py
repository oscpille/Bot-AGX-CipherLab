# =========================================================
# CONFIGURACIONES Y DICCIONARIOS GLOBALES
# =========================================================

# RUTA_EXCEL = r"C:\Users\dell\OneDrive - Profesionales en Inventarios SA de CV\SOLICITUD DE AGX.xlsx"
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Configuración Supabase
try:
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    if url and key:
        db: Client = create_client(url, key)
        print("✅ PC conectada a Supabase exitosamente.")
    else:
        db = None
        print("⚠️ Advertencia: No se encontraron las credenciales SUPABASE_URL o SUPABASE_KEY en el archivo .env")
except Exception as e:
    db = None
    print(f"⚠️ Error conectando a Supabase: {e}")

DICCIONARIO_NOMBRES_CORTOS = {
    "fecha de caducidad": "Caducidad",
    "fecha caducidad": "Caducidad",
    "fecha de vencimiento": "Caducidad",
    "vencimiento": "Caducidad",
    "numero de serie": "Serie",
    "numero serial": "Serie",
    "serial number": "Serie",
    "registro aduanero": "Pedimento",
    "mercancia importada": "Pedimento",
    "importacion": "Pedimento",
    "numero de matricula": "LPN",
    "matricula": "LPN",
    "codigo de barras": "C.Barras",
    "codigo de barra": "C.Barras",
    "codigo interno": "C.Interno",
    "codigo cliente": "C.Cliente",
    "descripcion de articulo": "Descrip.",
    "descripcion": "Descrip.",
    "id terminal": "Terminal",
    "ns del scaner": "Scanner",
    "numero de caja": "Caja",
    "unidades de medida": "U.Medida",
    "unidad de medida": "U.Medida",
    "codigo de producto": "C.Producto",
    "departamento": "Depto.",
    "depto": "Depto."
}

TRADUCCION_TIPOS = {
    "num": "integer", "numerico": "integer", "entero": "integer", "decimal": "real",
    "alfanum": "alphameric", "alfanumerico": "alphameric", "texto": "text", "letras": "letter",
    "lookup": "lookup", "prompt": "prompt"
}

# Este mapa se llenará dinámicamente según el modelo requerido (8000 u 8200)
MAPA_UI = {}