# =========================================================
# CONFIGURACIONES Y DICCIONARIOS GLOBALES
# =========================================================

RUTA_EXCEL = r"C:\Users\dell\OneDrive - Profesionales en Inventarios SA de CV\SOLICITUD DE AGX.xlsx"

DICCIONARIO_PREFIJOS = {
    "area": "ar", "caja": "caj", "barras": "cba", "interno": "ps",
    "color": "col", "descripcion": "ds", "estado": "est", "caducidad": "fc",
    "lpn": "ic", "usuario": "pw", "operador": "pw", "lote": "lt",
    "marbete": "mb", "marca": "mca", "modelo": "mod", "serie": "nse",
    "pedimento": "ped", "sku": "sk", "talla": "tal", "ubicacion": "ubi",
    "unidad": "uni", "cantidad": "cn", "conteo": "cn", "contrasena": "ps"
}

TRADUCCION_TIPOS = {
    "num": "integer", "numerico": "integer", "entero": "integer", "decimal": "real",
    "alfanum": "alphameric", "alfanumerico": "alphameric", "texto": "text", "letras": "letter",
    "lookup": "lookup"
}

# Este mapa se llenará dinámicamente según el modelo requerido (8000 u 8200)
MAPA_UI = {}