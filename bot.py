import pandas as pd
import unicodedata
import pyautogui
import time
import sys
from mapeo_batch import MAPA_UI 

# =========================================================
# FUNCIONES AUXILIARES Y DE INYECCIÓN
# =========================================================
def limpiar_texto(texto):
    texto_sin_acentos = unicodedata.normalize('NFD', str(texto)).encode('ascii', 'ignore').decode('utf-8')
    return texto_sin_acentos.lower().strip()

def inyectar_datos_desde_fila_2(diccionario_datos):
    """
    Sobrescribe la tabla activa empezando desde la Fila 2.
    Al terminar de escribir, limpia los renglones sobrantes con 'Nil'.
    """
    columnas = MAPA_UI["vista_form"]["tabla"]["columnas_x"]
    filas_y = MAPA_UI["vista_form"]["tabla"]["filas_y"]
    
    indice_fila = 1 # Empezamos en la Fila 2 (índice 1)
    
    # 1. Escribir los datos del diccionario
    for nombre_logico, config in diccionario_datos.items():
        if indice_fila >= 7: 
            break
            
        y_actual = filas_y[indice_fila]
        print(f"   -> Inyectando '{config['nombre_pantalla']}' en fila {indice_fila + 1}")
        
        # A. Seleccionar Data Type
        pyautogui.click(columnas["data_type"], y_actual)
        time.sleep(0.2)
        tipo_interno = config['tipo']
        if tipo_interno in MAPA_UI["vista_form"]["tabla"]["logica_data_type"]["secuencias"]:
            info_tecla = MAPA_UI["vista_form"]["tabla"]["logica_data_type"]["secuencias"][tipo_interno]
            pyautogui.press('n') # Reset
            time.sleep(0.1)
            for _ in range(info_tecla["pulsaciones"]):
                pyautogui.press(info_tecla["tecla"])
                time.sleep(0.1)
        pyautogui.press('enter')
        time.sleep(0.1)

        # B. Escribir Prompt (1 Clic + Supr)
        pyautogui.click(columnas["prompt"], y_actual)
        time.sleep(0.1)
        pyautogui.press('delete')
        pyautogui.write(config['nombre_pantalla'], interval=0.05)

        # C. Separar y escribir Longitudes
        if '-' in config['longitud']:
            min_val, max_val = config['longitud'].split('-')
        else:
            min_val = max_val = config['longitud']

        pyautogui.click(columnas["min_length"], y_actual)
        time.sleep(0.1)
        pyautogui.press('delete')
        pyautogui.write(min_val.strip(), interval=0.05)

        pyautogui.click(columnas["max_length"], y_actual)
        time.sleep(0.1)
        pyautogui.press('delete')
        pyautogui.write(max_val.strip(), interval=0.05)

        pyautogui.press('enter')
        indice_fila += 1
        
    # 2. Limpiar la basura residual (Poner en Nil las filas que sobraron)
    while indice_fila < 7:
        y_actual = filas_y[indice_fila]
        pyautogui.click(columnas["data_type"], y_actual)
        time.sleep(0.1)
        pyautogui.press('n') 
        pyautogui.press('enter')
        indice_fila += 1

# =========================================================
# RUTAS DE ARCHIVOS
# =========================================================
ruta_excel = r"C:\Users\dell\OneDrive - Profesionales en Inventarios SA de CV\FORMATO DE SOLICITUD DE AGX.xlsx"
ruta_csv = r"C:\Users\dell\Documents\Bot AGX\UltimaFila.csv"

# =========================================================
# FASE 1 Y 2: EXTRACCIÓN Y LÓGICA ESTRICTA DE FLUJO
# =========================================================
try:
    print("➤ Iniciando lectura desde OneDrive...")
    df = pd.read_excel(ruta_excel, usecols="F:K", engine='openpyxl')
    df.iloc[-1:].to_csv(ruta_csv, index=False, encoding='utf-8-sig')

    df_csv = pd.read_csv(ruta_csv, encoding='utf-8-sig')
    solicitud = df_csv.iloc[0]
    
    # 1. Nombre del cliente
    col_cliente = [c for c in df_csv.columns if 'INGRESA EL NOMBRE' in str(c).upper()][0]
    cliente = str(solicitud[col_cliente]).strip()
    
    # 2. Lógica excluyente de Flujo Operativo
    col_flujo = [c for c in df_csv.columns if 'FLUJO' in str(c).upper()][0]
    flujo_crudo = str(solicitud[col_flujo]).strip().upper()
    
    es_pieza = False
    es_volumen = False
    
    if "AMBOS" in flujo_crudo:
        es_pieza = True
        es_volumen = True
    elif "PIEZA" in flujo_crudo: # Verifica Pieza de forma aislada
        es_pieza = True
    elif "VOLUMEN" in flujo_crudo: # Verifica Volumen de forma aislada
        es_volumen = True
    else:
        print(f"⚠️ Flujo '{flujo_crudo}' desconocido. Se asume PIEZA por seguridad.")
        es_pieza = True
        
    print(f"📦 Cliente: {cliente}")
    print(f"🔄 Análisis de Flujo: '{flujo_crudo}' -> Pieza={es_pieza} | Volumen={es_volumen}\n")
    
    # DICCIONARIOS SEPARADOS
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
                datos = {
                    'nombre_pantalla': nombre_original,
                    'longitud': reglas[0],
                    'tipo': limpiar_texto(reglas[1])
                }
                if "marbete" in nombre_logico or "ubicacion" in nombre_logico:
                    dict_ubicacion[nombre_logico] = datos
                else:
                    dict_captura[nombre_logico] = datos

except Exception as e:
    print(f"❌ Error al procesar datos: {e}")
    sys.exit()

# =========================================================
# FASE 3: EL BOT ENRUTADOR E INYECTOR
# =========================================================
print("🤖 Iniciando Bot en 5 segundos...")
print("⚠️ Activa Forge AG y suelta el ratón.")
time.sleep(5) 

try:
    # --- 0. PREPARAR EL TERRENO (DESPLEGAR ÁRBOL) ---
    print("➤ [PASO 0] Desplegando árbol de directorios...")
    
    # Un clic en Menu
    pyautogui.click(MAPA_UI["directorio_izquierdo"]["menu"])
    time.sleep(0.5)
    
    # Un clic en Lookup
    pyautogui.click(MAPA_UI["directorio_izquierdo"]["lookup"])
    time.sleep(0.5)
    
    # Un clic en Form
    pyautogui.click(MAPA_UI["directorio_izquierdo"]["form"]["coords"])
    time.sleep(1) # Pausa para que renderice toda la lista

    # Scroll hacia arriba para asegurar que la barra vuelva al inicio
    pyautogui.scroll(1500)
    time.sleep(0.5)
    print("   Árbol desplegado correctamente.")

    # --- 1. MODIFICAR FORM 1 ---
    print("\n➤ Modificando Form 1 (Cabecera)...")
    pyautogui.click(360, 295) # Click directo en Form 1 (ya visible)
    time.sleep(1.5) 
    pyautogui.click(650, 550) 
    time.sleep(0.2)
    pyautogui.press('delete')
    pyautogui.write(cliente, interval=0.05)
    pyautogui.press('enter')

    # --- 2. MODIFICAR MENU 1 ---
    print("\n➤ Configurando Menu 1...")
    pyautogui.click(MAPA_UI["vista_menu"]["menu_1"])
    time.sleep(1.5)

    coords_item1 = MAPA_UI["vista_menu"]["items"]["item_1"]["coords"]
    coords_item2 = MAPA_UI["vista_menu"]["items"]["item_2"]["coords"]
    
    if es_volumen and not es_pieza:
        # Poner Volumen arriba
        pyautogui.click(coords_item1)
        time.sleep(0.2)
        pyautogui.press('delete')
        pyautogui.write("1. VOLUMEN", interval=0.05)
        pyautogui.click(1000, 230)
        time.sleep(0.5)
        pyautogui.click(MAPA_UI["vista_menu"]["next_dropdowns"]["next_1"]["form_5"])
        # Borrar el Item 2
        pyautogui.click(coords_item2)
        time.sleep(0.2)
        pyautogui.press('delete')
        pyautogui.press('enter')

    elif es_pieza and not es_volumen:
        # Poner Pieza arriba
        pyautogui.click(coords_item1)
        time.sleep(0.2)
        pyautogui.press('delete')
        pyautogui.write("1. PIEZA X PIEZA", interval=0.05)
        pyautogui.click(1000, 230)
        time.sleep(0.5)
        pyautogui.click(MAPA_UI["vista_menu"]["next_dropdowns"]["next_1"]["form_2"])
        # Borrar el Item 2
        pyautogui.click(coords_item2)
        time.sleep(0.2)
        pyautogui.press('delete')
        pyautogui.press('enter')

    # --- 3. INYECCIÓN EN FORMS DE CAPTURA ---
    pyautogui.scroll(1500) 
    time.sleep(1)

    # --- RUTA PIEZA X PIEZA ---
    if es_pieza:
        print("\n➤ [PIEZA] Inyectando Ubicaciones en Form 3...")
        pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"]["form_3"])
        time.sleep(1.5)
        inyectar_datos_desde_fila_2(dict_ubicacion)
        
        print("➤ [PIEZA] Inyectando Variables en Form 4...")
        pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"]["form_4"])
        time.sleep(1.5)
        inyectar_datos_desde_fila_2(dict_captura)

    # --- RUTA VOLUMEN ---
    if es_volumen:
        print("\n➤ [VOLUMEN] Inyectando Ubicaciones en Form 6...")
        pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"]["form_6"])
        time.sleep(1.5)
        inyectar_datos_desde_fila_2(dict_ubicacion)
        
        print("➤ [VOLUMEN] Inyectando Variables en Form 7...")
        pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"]["form_7"]["coords"])
        time.sleep(1.5)
        inyectar_datos_desde_fila_2(dict_captura)

    print("\n✅ ¡ARCHIVO AGX GENERADO Y LIMPIO!")

except Exception as e:
    print(f"\n❌ El bot se detuvo por un error: {e}")