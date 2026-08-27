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
DICCIONARIO_PREFIJOS = {
    # fc
    "fecha de caducidad": "fc", "fecha caducidad": "fc", "fecha de vencimiento": "fc",
    "caduccion": "fc", "vencimiento": "fc", "caducidad": "fc", "expiracion": "fc", "cad": "fc",
    # nse
    "numero de serie": "nse", "numero serial": "nse", "serial number": "nse", 
    "series": "nse", "serie": "nse", "serial": "nse", "sn": "nse",
    # ped
    "registro aduanero": "ped", "mercancia importada": "ped", "importacion": "ped",
    "aduana": "ped", "pedimento": "ped",
    # ic
    "numero de matricula": "ic", "matricula": "ic", "lpn": "ic",
    # cba
    "codigo de barras": "cba", "codigo de barra": "cba", "barras": "cba", "ean": "cba", "upc": "cba",
    # ps
    "codigo interno": "ps", "codigo cliente": "ps", "clave": "ps", "interno": "ps",
    # ds
    "descripcion de articulo": "ds", "descripcion": "ds", "descrip": "ds",
    # ter
    "id terminal": "ter", "ns del scaner": "ter", "scanner": "ter", "escaner": "ter", "terminal": "ter",
    # mca, mod, lt, mb, tal, caj, ar, col
    "marcas": "mca", "marca": "mca",
    "modelos": "mod", "modelo": "mod",
    "lotes": "lt", "lote": "lt", "batch": "lt",
    "marbetes": "mb", "marbete": "mb",
    "tallas": "tal", "talla": "tal",
    "cajas": "caj", "caja": "caj",
    "areas": "ar", "area": "ar",
    "colores": "col", "color": "col",
    # ubi, sk, est
    "ubicacion": "ubi",
    "sku": "sk", "sk": "sk", "sap": "sk", "articulo": "sk", "item": "sk", "producto": "sk", "codigo de producto": "sk", "cve": "sk",
    "estado": "est", "condicion": "est", "estatus": "est",
    # dep
    "departamento": "dep", "depto": "dep", "familia": "dep", "clase": "dep", "seccion": "dep",
    # uni
    "unidades de medida": "uni", "unidad de medida": "uni", "unidades": "uni", "unidad": "uni", "medida": "uni",
    # cn (Conteos y unidades específicas)
    "centimetro": "cn", "cm": "cn", "milimetro": "cn", "mm": "cn",
    "milla": "cn", "mi": "cn", "yarda": "cn", "yd": "cn", "pie": "cn", "ft": "cn", 
    "pulgada": "cn", "in": "cn", "metro": "cn", "metros": "cn", "mts": "cn",
    "kilometro": "cn", "km": "cn", "decimetro": "cn", "dm": "cn", 
    "tonelada": "cn", "kilogramo": "cn", "kilos": "cn", "kg": "cn", 
    "gramo": "cn", "gramos": "cn", "gr": "cn", "miligramo": "cn", "miligramos": "cn", "mg": "cn", 
    "libra": "cn", "lb": "cn", "onza": "cn", "oz": "cn", "grano": "cn",
    "litros": "cn", "galones": "cn", "kl": "cn", "ml": "cn",
    "cantidad": "cn", "conteo": "cn"
}

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