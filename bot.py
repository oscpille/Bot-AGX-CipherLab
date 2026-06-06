import pandas as pd
import unicodedata
import pyautogui
import time
import sys
from mapeo_batch import MAPA_UI 

# =========================================================
# 1. FUNCIONES AUXILIARES Y DE INYECCIÓN
# =========================================================
def limpiar_texto(texto):
    texto_sin_acentos = unicodedata.normalize('NFD', str(texto)).encode('ascii', 'ignore').decode('utf-8')
    return texto_sin_acentos.lower().strip()

def inyectar_datos_en_tabla(diccionario_datos, es_ubicacion=False):
    columnas = MAPA_UI["vista_form"]["tabla"]["columnas_x"]
    filas_y = MAPA_UI["vista_form"]["tabla"]["filas_y"]
    
    indice_fila_captura = 1 
    filas_usadas = [] 
    
    for nombre_logico, config in diccionario_datos.items():
        if es_ubicacion:
            if "marbete" in nombre_logico:
                idx = 2 
            elif "ubicacion" in nombre_logico:
                idx = 1 
            else:
                idx = 3 
        else:
            idx = indice_fila_captura
            indice_fila_captura += 1
            if idx >= 7: break 
            
        y_actual = filas_y[idx]
        filas_usadas.append(idx)
        print(f"   -> Inyectando '{config['nombre_pantalla']}' en fila {idx + 1}")
        
        pyautogui.click(columnas["data_type"], y_actual)
        time.sleep(0.2)
        pyautogui.click(columnas["data_type"], y_actual)
        time.sleep(0.2)
        
        tipo_interno = config['tipo']
        if tipo_interno in MAPA_UI["vista_form"]["tabla"]["logica_data_type"]["secuencias"]:
            info_tecla = MAPA_UI["vista_form"]["tabla"]["logica_data_type"]["secuencias"][tipo_interno]
            pyautogui.press('n') 
            time.sleep(0.1)
            for _ in range(info_tecla["pulsaciones"]):
                pyautogui.press(info_tecla["tecla"])
                time.sleep(0.1)
        pyautogui.press('enter')
        time.sleep(0.1)

        pyautogui.click(columnas["prompt"], y_actual)
        time.sleep(0.1)
        pyautogui.write(config['nombre_pantalla'], interval=0.05)

        if '-' in config['longitud']:
            min_val, max_val = config['longitud'].split('-')
        else:
            min_val = max_val = config['longitud'] 

        pyautogui.click(columnas["min_length"], y_actual)
        time.sleep(0.1)
        pyautogui.write(min_val.strip(), interval=0.05)

        pyautogui.click(columnas["max_length"], y_actual)
        time.sleep(0.1)
        pyautogui.write(max_val.strip(), interval=0.05)
        
    for i in range(1, 7):
        if i not in filas_usadas:
            y_actual = filas_y[i]
            pyautogui.click(columnas["data_type"], y_actual)
            time.sleep(0.1)
            pyautogui.click(columnas["data_type"], y_actual) 
            time.sleep(0.1)
            pyautogui.press('n') 
            pyautogui.press('enter')

# =========================================================
# 2. RUTAS, TRADUCCIÓN Y LECTURA DE EXCEL (FASE 1 Y 2)
# =========================================================
ruta_excel = r"C:\Users\dell\OneDrive - Profesionales en Inventarios SA de CV\FORMATO DE SOLICITUD DE AGX.xlsx"
ruta_csv = r"C:\Users\dell\Documents\Bot AGX\UltimaFila.csv"

# --- DICCIONARIO DE TRADUCCIÓN (EXCEL -> FORGE AG) ---
TRADUCCION_TIPOS = {
    "num": "integer",
    "entero": "integer",
    "decimal": "real",
    "alfamum": "alphameric",
    "alfanumerico": "alphameric",
    "texto": "text",
    "letras": "letter",
    "ddmmaa": "alphameric" # <- NUEVO: Convertimos las fechas a alfanumérico para soportar ceros a la izquierda
}

try:
    print("➤ Iniciando lectura desde OneDrive...")
    
    # --- BUCLE DE PACIENCIA (ANTI-RETRASO DE ONEDRIVE) ---
    max_reintentos = 3
    df_valido = False
    
    for intento in range(max_reintentos):
        df = pd.read_excel(ruta_excel, usecols="F:K", engine='openpyxl')
        df = df.dropna(how='all') 
        
        if not df.empty:
            df_valido = True
            break 
            
        print(f"   ⏳ OneDrive aún no actualiza. Esperando 5 segundos (Intento {intento + 1})...")
        time.sleep(5) 
        
    if not df_valido:
        raise ValueError("El Excel sigue vacío. Revisa OneDrive.")

    df.iloc[-1:].to_csv(ruta_csv, index=False, encoding='utf-8-sig')

    df_csv = pd.read_csv(ruta_csv, encoding='utf-8-sig')
    solicitud = df_csv.iloc[0]
    
    cliente = str(solicitud['INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:']).strip()
    
    # --- CORRECCIÓN ANTI-ACENTOS Y MAYÚSCULAS ---
    # Usamos tu función limpiar_texto para que "Volúmen" o "VOLÚMEN" siempre sean "volumen"
    flujo_crudo = limpiar_texto(solicitud['FLUJO OPERATIVO:'])
    
    es_pieza = "pieza" in flujo_crudo or "ambos" in flujo_crudo
    es_volumen = "volumen" in flujo_crudo or "ambos" in flujo_crudo
    
    print(f"📦 Cliente: {cliente}")
    print(f"🔄 Flujo: Pieza={es_pieza} | Volumen={es_volumen}\n")
    
    dict_ubicacion = {}
    dict_captura = {}
    
    for linea in str(solicitud['DATOS REQUERIDOS']).split('\n'):
        linea = linea.strip()
        if linea and ':' in linea:
            partes = linea.split(':')
            nombre_original = partes[0].strip()
            nombre_logico = limpiar_texto(nombre_original)
            
            reglas = partes[1].replace(" - ", "-").replace("- ", "-").replace(" -", "-").strip().split()
            if len(reglas) >= 2:
                tipo_excel = limpiar_texto(reglas[1])
                tipo_forge = TRADUCCION_TIPOS.get(tipo_excel, tipo_excel)
                
                datos = {
                    'nombre_pantalla': nombre_original,
                    'longitud': reglas[0],
                    'tipo': tipo_forge
                }
                
                if "marbete" in nombre_logico or "ubicacion" in nombre_logico:
                    dict_ubicacion[nombre_logico] = datos
                else:
                    dict_captura[nombre_logico] = datos

except Exception as e:
    print(f"❌ Error al procesar datos: {e}")
    sys.exit()

# =========================================================
# 3. EL CEREBRO DEL BOT (FASE 3) - MODO TURBO
# =========================================================
print("🤖 Iniciando Bot en 5 segundos...")
print("⚠️ Activa Forge AG y suelta el ratón.")
time.sleep(5) 

try:
    # --- A. PREPARAR EL TERRENO ---
    print("➤ [PASO 0] Desplegando árbol de directorios...")
    pyautogui.click(MAPA_UI["directorio_izquierdo"]["menu"])
    time.sleep(0.25) # Antes 0.5
    pyautogui.click(MAPA_UI["directorio_izquierdo"]["lookup"])
    time.sleep(0.25) # Antes 0.5
    pyautogui.click(MAPA_UI["directorio_izquierdo"]["form"]["coords"])
    time.sleep(0.5)  # Antes 1
    
    pyautogui.scroll(1500)
    time.sleep(0.25) # Antes 0.5

    # --- B. MODIFICAR FORM 1 ---
    print("\n➤ Modificando Form 1 (Cabecera)...")
    x_f1, y_f1 = MAPA_UI["vista_form"]["seleccion_forms"]["form_1"]
    pyautogui.click(x_f1, y_f1) 
    time.sleep(0.75) # Antes 1.5
    
    pyautogui.click(650, 550) 
    time.sleep(0.1)  # Antes 0.2
    pyautogui.press('delete')
    pyautogui.write(cliente, interval=0.05) 
    pyautogui.press('enter')

    # --- C. MODIFICAR MENU 1 ---
    print("\n➤ Configurando Menu 1...")
    pyautogui.click(MAPA_UI["vista_menu"]["menu_1"])
    time.sleep(0.75) # Antes 1.5

    coords_item1 = MAPA_UI["vista_menu"]["items"]["item_1"]["coords"]
    coords_item2 = MAPA_UI["vista_menu"]["items"]["item_2"]["coords"]
    
    if es_volumen and not es_pieza:
        pyautogui.click(coords_item1)
        time.sleep(0.1)
        pyautogui.write("1. VOLUMEN", interval=0.05)
        
        pyautogui.click(1000, 230)
        time.sleep(0.25) # Antes 0.5
        pyautogui.click(MAPA_UI["vista_menu"]["next_dropdowns"]["next_1"]["form_5"])
        
        pyautogui.click(coords_item2)
        time.sleep(0.1)
        pyautogui.press('delete')
        pyautogui.press('enter')

    elif es_pieza and not es_volumen:
        pyautogui.click(coords_item1)
        time.sleep(0.1)
        pyautogui.write("1. PIEZA X PIEZA", interval=0.05)
        
        pyautogui.click(1000, 230)
        time.sleep(0.25) # Antes 0.5
        pyautogui.click(MAPA_UI["vista_menu"]["next_dropdowns"]["next_1"]["form_2"])
        
        pyautogui.click(coords_item2)
        time.sleep(0.1)
        pyautogui.press('delete')
        pyautogui.press('enter')

    # --- D. INYECCIÓN EN FORMS ---
    pyautogui.scroll(1500) 
    time.sleep(0.5) # Antes 1

    if es_pieza:
        print("\n➤ [PIEZA] Inyectando Ubicaciones en Form 3...")
        pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"]["form_3"])
        time.sleep(0.75) # Antes 1.5
        inyectar_datos_en_tabla(dict_ubicacion, es_ubicacion=True)
        
        print("➤ [PIEZA] Inyectando Variables en Form 4...")
        pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"]["form_4"])
        time.sleep(0.75) # Antes 1.5
        inyectar_datos_en_tabla(dict_captura, es_ubicacion=False)

    if es_volumen:
        print("\n➤ [VOLUMEN] Inyectando Ubicaciones en Form 6...")
        pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"]["form_6"])
        time.sleep(0.75) # Antes 1.5
        inyectar_datos_en_tabla(dict_ubicacion, es_ubicacion=True)
        
        print("➤ [VOLUMEN] Inyectando Variables en Form 7...")
        x_f7, y_f7 = MAPA_UI["vista_form"]["seleccion_forms"]["form_7"]["coords"]
        pyautogui.click(x_f7, y_f7)
        time.sleep(0.75) # Antes 1.5
        inyectar_datos_en_tabla(dict_captura, es_ubicacion=False)

    print("\n✅ ¡ARCHIVO AGX GENERADO Y LIMPIO!")

except Exception as e:
    print(f"\n❌ El bot se detuvo por un error: {e}")