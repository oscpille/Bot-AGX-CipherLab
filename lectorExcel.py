import pandas as pd
import unicodedata

# --- FUNCIÓN PARA LIMPIAR TEXTOS ---
# Quita acentos y pasa a minúsculas (Ej: 'Día' -> 'dia')
def limpiar_texto(texto):
    texto_sin_acentos = unicodedata.normalize('NFD', str(texto)).encode('ascii', 'ignore').decode('utf-8')
    return texto_sin_acentos.lower().strip()

# --- RUTAS DE ARCHIVOS ---
ruta_excel = r"C:\Users\dell\OneDrive - Profesionales en Inventarios SA de CV\FORMATO DE SOLICITUD DE AGX.xlsx"
ruta_csv = r"C:\Users\dell\Documents\Bot AGX\UltimaFila.csv"

# =========================================================
# FASE 1: EXTRAER LA ÚLTIMA SOLICITUD DE EXCEL Y GUARDARLA
# =========================================================
try:
    print("Iniciando extracción de datos desde OneDrive...")
    # Leer SOLO las columnas de la F a la K del Excel
    df = pd.read_excel(ruta_excel, usecols="F:K", engine='openpyxl')
    
    # Extraer únicamente la última fila
    ultima_fila = df.iloc[-1:]
    
    # Guardar en formato CSV local
    ultima_fila.to_csv(ruta_csv, index=False, encoding='utf-8-sig')
    print(f"✅ Extracción completada. Archivo guardado en: {ruta_csv}\n")

except FileNotFoundError:
    print("❌ Error: No se encontró el Excel. Verifica la ruta y OneDrive.")
    exit() # Detiene el script si no hay archivo
except Exception as e:
    print(f"❌ Error al leer el Excel: {e}")
    exit()

# =========================================================
# FASE 2: LEER EL CSV Y LIMPIAR LAS INSTRUCCIONES
# =========================================================
try:
    # Leer el archivo CSV que acabamos de generar
    df_csv = pd.read_csv(ruta_csv, encoding='utf-8-sig')
    solicitud = df_csv.iloc[0]
    
    # Extraer variables principales
    cliente = solicitud['INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:']
    datos_crudos = str(solicitud['DATOS REQUERIDOS'])
    
    print(f"📦 Procesando Inventario para: {cliente}")
    print("-" * 50)
    
    configuracion_agx = {}
    lineas = datos_crudos.split('\n')
    
    for linea in lineas:
        linea = linea.strip()
        # Ignorar renglones vacíos o sin formato correcto
        if not linea or ':' not in linea:
            continue
            
        partes = linea.split(':')
        
        # Blindaje del nombre del dato
        nombre_original = partes[0].strip()
        nombre_logico = limpiar_texto(nombre_original)
        
        # Blindaje de las reglas (Apretar guiones)
        reglas_limpias = partes[1].replace(" - ", "-").replace("- ", "-").replace(" -", "-")
        
        # Separar longitud y tipo
        reglas = reglas_limpias.strip().split()
        
        if len(reglas) >= 2:
            longitud = reglas[0]
            tipo_dato = limpiar_texto(reglas[1]) 
            
            # Guardar en el diccionario estructurado
            configuracion_agx[nombre_logico] = {
                'nombre_pantalla': nombre_original,
                'longitud': longitud,
                'tipo': tipo_dato
            }

    # Imprimir el resultado final limpio
    print("✅ Datos extraídos, limpiados y entendidos por el Bot:\n")
    for dato_logico, config in configuracion_agx.items():
        print(f"➤ ID Bot: {dato_logico.ljust(10)} | Pantalla: {config['nombre_pantalla'].ljust(12)} | Min-Max: {config['longitud'].ljust(8)} | Tipo: {config['tipo']}")

except Exception as e:
    print(f"❌ Error al procesar el CSV: {e}")