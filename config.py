# =========================================================
# CONFIGURACIONES Y DICCIONARIOS GLOBALES
# =========================================================

# RUTA_EXCEL = r"C:\Users\dell\OneDrive - Profesionales en Inventarios SA de CV\SOLICITUD DE AGX.xlsx"
TERMUX_API_URL = "http://192.168.120.46:3000" # Cámbialo por la IP real del celular en tu WiFi, ej: "http://192.168.1.75:3000"

DICCIONARIO_PREFIJOS = {
    # fca
    "fecha de caducidad": "fca", "fecha caducidad": "fca", "fecha de vencimiento": "fca",
    "caduccion": "fca", "vencimiento": "fca", "caducidad": "fca",
    # nse
    "numero de serie": "nse", "numero serial": "nse", "serial number": "nse", 
    "series": "nse", "serie": "nse", "serial": "nse", "sn": "nse",
    # ped
    "registro aduanero": "ped", "mercancia importada": "ped", "importacion": "ped",
    "aduana": "ped", "pedimento": "ped",
    # lpn
    "numero de matricula": "lpn", "matricula": "lpn", "lpn": "lpn",
    # cba
    "codigo de barras": "cba", "codigo de barra": "cba", "barras": "cba", "ean": "cba", "upc": "cba",
    # cin
    "codigo interno": "cin", "codigo cliente": "cin", "clave": "cin", "interno": "cin",
    # des
    "descripcion de articulo": "des", "descripcion": "des",
    # ter
    "id terminal": "ter", "ns del scaner": "ter", "scanner": "ter", "escaner": "ter", "terminal": "ter",
    # mca, mod, lot, mar, tal, caj, are, col
    "marcas": "mca", "marca": "mca",
    "modelos": "mod", "modelo": "mod",
    "lotes": "lot", "lote": "lot",
    "marbetes": "mar", "marbete": "mar",
    "tallas": "tal", "talla": "tal",
    "cajas": "caj", "caja": "caj",
    "areas": "are", "area": "are",
    "colores": "col", "color": "col",
    # ubi, sku, est
    "ubicacion": "ubi",
    "sku": "sku", "sk": "sku", "sap": "sku",
    "estado": "est", "condicion": "est", "estatus": "est",
    # uni
    "unidades de medida": "uni", "unidad de medida": "uni", "unidades": "uni", "unidad": "uni", "medida": "uni",
    # con (Conteos y unidades específicas)
    "centimetro": "con", "cm": "con", "milimetro": "con", "mm": "con",
    "milla": "con", "mi": "con", "yarda": "con", "yd": "con", "pie": "con", "ft": "con", 
    "pulgada": "con", "in": "con", "metro": "con", "metros": "con", "mts": "con",
    "kilometro": "con", "km": "con", "decimetro": "con", "dm": "con", 
    "tonelada": "con", "kilogramo": "con", "kilos": "con", "kg": "con", 
    "gramo": "con", "gramos": "con", "gr": "con", "miligramo": "con", "miligramos": "con", "mg": "con", 
    "libra": "con", "lb": "con", "onza": "con", "oz": "con", "grano": "con",
    "litros": "con", "galones": "con", "kl": "con", "ml": "con",
    "cantidad": "con", "conteo": "con"
}

TRADUCCION_TIPOS = {
    "num": "integer", "numerico": "integer", "entero": "integer", "decimal": "real",
    "alfanum": "alphameric", "alfanumerico": "alphameric", "texto": "text", "letras": "letter",
    "lookup": "lookup"
}

# Este mapa se llenará dinámicamente según el modelo requerido (8000 u 8200)
MAPA_UI = {}