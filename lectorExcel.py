import pandas as pd
import unicodedata # <--- NUEVA LIBRERÍA (Ya viene en Python, no hay que instalar nada)

# --- FUNCIÓN PARA LIMPIAR TEXTOS (Quita acentos y mayúsculas) ---
def limpiar_texto(texto):
    # Transforma 'Día' -> 'dia', 'Categoría' -> 'categoria'
    texto_sin_acentos = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    return texto_sin_acentos.lower().strip()

# 1. Leer el archivo CSV que acabamos de generar
ruta_csv = r"C:\Users\dell\Documents\Bot AGX\UltimaFila.csv"

try:
    df_csv = pd.read_csv(ruta_csv, encoding='utf-8-sig')
    solicitud = df_csv.iloc[0]
    
    cliente = solicitud['INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:']
    datos_crudos = str(solicitud['DATOS REQUERIDOS'])
    
    print(f"📦 Procesando Inventario para: {cliente}")
    print("-" * 40)
    
    configuracion_agx = {}
    lineas = datos_crudos.split('\n')
    
    for linea in lineas:
        linea = linea.strip()
        if not linea or ':' not in linea:
            continue
            
        partes = linea.split(':')
        
        # --- BLINDAJE DEL NOMBRE DEL DATO ---
        nombre_original = partes[0].strip() # Ej: "Día" (Para usarlo en la pantalla del lector)
        nombre_logico = limpiar_texto(nombre_original) # Ej: "dia" (Para que el bot sepa qué es)
        
        # --- BLINDAJE DE LAS REGLAS (El problema del guion) ---
        # Apretamos los guiones: "1 - 3" o "1- 3" o "1 -3" se convierten en "1-3"
        reglas_limpias = partes[1].replace(" - ", "-").replace("- ", "-").replace(" -", "-")
        
        # Ahora sí, separamos por espacios de forma segura
        reglas = reglas_limpias.strip().split()
        
        if len(reglas) >= 2:
            longitud = reglas[0]
            # También limpiamos el tipo de dato por si escriben "NUM" en mayúsculas
            tipo_dato = limpiar_texto(reglas[1]) 
            
            # Guardamos todo en el diccionario usando el nombre_logico como llave principal
            configuracion_agx[nombre_logico] = {
                'nombre_pantalla': nombre_original,
                'longitud': longitud,
                'tipo': tipo_dato
            }

    print("✅ Datos extraídos, limpiados y entendidos por el Bot:\n")
    for dato_logico, config in configuracion_agx.items():
        print(f"➤ ID Bot: {dato_logico.ljust(10)} | Pantalla: {config['nombre_pantalla'].ljust(12)} | Min-Max: {config['longitud'].ljust(8)} | Tipo: {config['tipo']}")

except Exception as e:
    print(f"❌ Error al procesar el CSV: {e}")