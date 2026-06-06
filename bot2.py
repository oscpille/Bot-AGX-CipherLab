import pandas as pd
import unicodedata
import pyautogui
import time
import sys
import textwrap 
from mapeo_batch import MAPA_UI 

# =========================================================
# 1. FUNCIONES AUXILIARES Y DE INYECCIÓN
# =========================================================
def limpiar_texto(texto):
    """Quita acentos y pasa a minúsculas para comparaciones exactas."""
    texto_sin_acentos = unicodedata.normalize('NFD', str(texto)).encode('ascii', 'ignore').decode('utf-8')
    return texto_sin_acentos.lower().strip()

def inyectar_datos_en_tabla(diccionario_datos, es_ubicacion=False, es_flujo_volumen=False):
    """
    Inyecta datos respetando las Zonas Seguras de la plantilla AGX y omitiendo duplicados.
    """
    columnas = MAPA_UI["vista_form"]["tabla"]["columnas_x"]
    filas_y = MAPA_UI["vista_form"]["tabla"]["filas_y"]
    
    indice_fila_captura = 1 
    filas_usadas = [] 
    
    tiene_ambos_ubicaciones = any("marbete" in k for k in diccionario_datos) and any("ubicacion" in k for k in diccionario_datos)
    
    # --- DETERMINAR LÍMITES Y ZONAS SEGURAS ---
    if es_ubicacion:
        limite_indice = 7 # Limpia hasta Fila 7 (índice 6). Protege Fila 8.
    elif es_flujo_volumen:
        limite_indice = 6 # (Form 7) Limpia hasta Fila 6. PROTEGE FILA 7 (Cantidad) y 8.
    else:
        limite_indice = 5 # (Form 4) Limpia hasta Fila 5. PROTEGE FILA 6 (Pause), 7 (Fixed) y 8.
        
    # --- A. INYECTAR DATOS ---
    for nombre_logico, config in diccionario_datos.items():
        
        # --- LÓGICA ESPACIAL (Ubicaciones) ---
        if es_ubicacion:
            if "marbete" in nombre_logico:
                idx = 2 
            elif "ubicacion" in nombre_logico:
                idx = 4 if tiene_ambos_ubicaciones else 2 
            else:
                idx = 5 
        
        # --- LÓGICA DE CAPTURA NORMAL Y FILTROS ---
        else:
            if es_flujo_volumen:
                # Filtro 1: Omitir decimales en Volumen
                if config['tipo'] == 'real':
                    print(f"   [!] Omitiendo '{config['nombre_pantalla']}' (Decimal) porque estamos en Volumen.")
                    continue 
                
                # Filtro 2: Omitir Cantidad en Volumen (Ya está fija en la fila 7)
                if "cantidad" in nombre_logico:
                    print(f"   [!] Omitiendo '{config['nombre_pantalla']}' porque ya viene por defecto en el Form 7.")
                    continue
                
            idx = indice_fila_captura
            indice_fila_captura += 1
            
            # Detener inyección si superamos el espacio disponible
            if idx >= limite_indice: 
                print(f"   [!] Alerta: Se ignoraron campos extra porque se alcanzó el límite de esta pantalla.")
                break 
            
        y_actual = filas_y[idx]
        filas_usadas.append(idx)
        print(f"   -> Inyectando '{config['nombre_pantalla']}' en fila {idx + 1}")
        
        # 1. Seleccionar Data Type
        pyautogui.click(columnas["data_type"], y_actual)
        time.sleep(0.1)
        pyautogui.click(columnas["data_type"], y_actual)
        time.sleep(0.1)
        
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

        # 2. Escribir Prompt
        pyautogui.click(columnas["prompt"], y_actual)
        time.sleep(0.1)
        
        texto_pantalla = unicodedata.normalize('NFD', config['nombre_pantalla']).encode('ascii', 'ignore').decode('utf-8').strip()
        if texto_pantalla.endswith(':'):
            texto_pantalla = texto_pantalla[:-1]
        texto_final = f"{texto_pantalla}: "
        
        pyautogui.write(texto_final, interval=0.05)

        # 3. Separar y escribir Longitudes
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
        
    # --- B. LIMPIEZA CON NIL ---
    # La barredora ahora solo llega hasta el límite permitido, protegiendo lo de abajo
    for i in range(1, limite_indice):
        if i not in filas_usadas:
            y_actual = filas_y[i]
            pyautogui.click(columnas["data_type"], y_actual)
            time.sleep(0.1)
            pyautogui.click(columnas["data_type"], y_actual) 
            time.sleep(0.1)
            pyautogui.press('n') 
            pyautogui.press('enter')

# =========================================================
# 2. RUTAS, TRADUCCIÓN Y LECTURA DE EXCEL
# =========================================================
ruta_excel = r"C:\Users\dell\OneDrive - Profesionales en Inventarios SA de CV\FORMATO DE SOLICITUD DE AGX.xlsx"
ruta_csv = r"C:\Users\dell\Documents\Bot AGX\UltimaFila.csv"

TRADUCCION_TIPOS = {
    "num": "integer",
    "entero": "integer",
    "decimal": "real",
    "alfamum": "alphameric",
    "alfanumerico": "alphameric",
    "texto": "text",
    "letras": "letter",
    "ddmmaa": "integer",
    "ddmmaaaa": "integer"
}

try:
    print("➤ Iniciando lectura desde OneDrive...")
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
    
    # FORZAR MAYÚSCULAS en el nombre del cliente
    cliente = str(solicitud['INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:']).strip().upper()
    flujo_crudo = limpiar_texto(solicitud['FLUJO OPERATIVO:'])
    
    es_pieza = "pieza" in flujo_crudo or "ambos" in flujo_crudo
    es_volumen = "volumen" in flujo_crudo or "ambos" in flujo_crudo
    
    print(f"📦 Cliente: {cliente}")
    print(f"🔄 Flujo: Pieza={es_pieza} | Volumen={es_volumen}\n")
    
    dict_ubicacion = {}
    dict_captura = {}
    
    # Reemplaza posibles ';' por ':' para blindar el código
    datos_req_limpios = str(solicitud['DATOS REQUERIDOS']).replace(';', ':')
    
    for linea in datos_req_limpios.split('\n'):
        linea = linea.strip()
        if linea and ':' in linea:
            partes = linea.split(':')
            nombre_original = partes[0].strip()
            nombre_logico = limpiar_texto(nombre_original)
            
            es_caducidad = "caducidad" in nombre_logico
            reglas = partes[1].strip().split()
            
            min_max_final = ""
            tipo_bruto = ""
            
            if len(reglas) >= 2:
                # Escenario normal: 'Kilo: 3-7 decimal'
                min_max_final = reglas[0]
                tipo_bruto = reglas[1]
            elif len(reglas) == 1 and es_caducidad:
                # Escenario inteligente: 'Caducidad: DDMMAAAA'
                tipo_formato_fecha = reglas[0]
                longitud_calculada = len(tipo_formato_fecha.strip())
                min_max_final = f"{longitud_calculada}-{longitud_calculada}"
                tipo_bruto = tipo_formato_fecha
            else:
                print(f"   [!] Omitiendo línea mal formateada: '{linea}'")
                continue

            tipo_forge = TRADUCCION_TIPOS.get(limpiar_texto(tipo_bruto), limpiar_texto(tipo_bruto))
            
            datos = {
                'nombre_pantalla': nombre_original,
                'longitud': min_max_final,
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
# 3. EL CEREBRO DEL BOT (FASE 3 - NUEVA ARQUITECTURA DE MENÚS)
# =========================================================
print("🤖 Iniciando Bot en 5 segundos...")
print("⚠️ Activa Forge AG y suelta el ratón.")
time.sleep(5) 

try:
    print("➤ [PASO 0] Desplegando árbol de directorios...")
    pyautogui.click(MAPA_UI["directorio_izquierdo"]["menu"])
    time.sleep(0.25) 
    pyautogui.click(MAPA_UI["directorio_izquierdo"]["lookup"])
    time.sleep(0.25) 
    pyautogui.click(MAPA_UI["directorio_izquierdo"]["form"]["coords"])
    time.sleep(0.5)  
    
    pyautogui.scroll(1500)
    time.sleep(0.25) 

    # --- B. MODIFICAR MENU 1 (NOMBRE DEL CLIENTE EN FILAS 5, 6, 7) ---
    print("\n➤ Modificando Menu 1 (Cabecera del Cliente)...")
    pyautogui.click(MAPA_UI["vista_menu"]["menu_1"])
    time.sleep(0.75) 
    
    # Extraemos el diccionario completo de las Nexts para tener 'coords' y 'menu_2'
    coords_items = [
        MAPA_UI["vista_menu"]["items"]["item_5"]["coords"],
        MAPA_UI["vista_menu"]["items"]["item_6"]["coords"],
        MAPA_UI["vista_menu"]["items"]["item_7"]["coords"]
    ]
    dicc_nexts = [
        MAPA_UI["vista_menu"]["next_dropdowns"]["next_5"],
        MAPA_UI["vista_menu"]["next_dropdowns"]["next_6"],
        MAPA_UI["vista_menu"]["next_dropdowns"]["next_7"]
    ]
    
    # 1. Limpiar visualmente cualquier texto anterior en las filas 5, 6 y 7
    for coord in coords_items: 
        pyautogui.click(coord)
        time.sleep(0.1)
        pyautogui.press('delete')
        
    # 2. Cortar el nombre e inyectarlo renglón por renglón
    lineas_cliente = textwrap.wrap(cliente, width=16, break_long_words=True)
    
    for i in range(3): 
        if i < len(lineas_cliente):
            # Escribir el fragmento de texto
            pyautogui.click(coords_items[i])
            time.sleep(0.1)
            pyautogui.write(lineas_cliente[i], interval=0.05)
            
            # Cambiar la columna "Next" a Menu 2 usando CLICS FÍSICOS
            pyautogui.click(dicc_nexts[i]["coords"]) 
            time.sleep(0.1)
            pyautogui.click(dicc_nexts[i]["coords"]) # Doble clic para desplegar
            time.sleep(0.25)
            
            # Clic directo en la opción "Menu 2" del menú desplegable
            pyautogui.click(dicc_nexts[i]["menu_2"])
            time.sleep(0.1)

    # --- C. MODIFICAR MENU 2 (ENRUTADOR PIEZA O VOLUMEN) ---
    print("\n➤ Configurando Menu 2 (Tipos de Conteo)...")
    pyautogui.click(MAPA_UI["vista_menu"]["menu_2"]) # Extraído del diccionario
    time.sleep(0.75) 

    coords_item1 = MAPA_UI["vista_menu"]["items"]["item_1"]["coords"]
    coords_item2 = MAPA_UI["vista_menu"]["items"]["item_2"]["coords"]
    
    if es_volumen and not es_pieza:
        pyautogui.click(coords_item1)
        time.sleep(0.1)
        pyautogui.write("1. VOLUMEN", interval=0.05)
        
        pyautogui.click(MAPA_UI["vista_menu"]["next_dropdowns"]["next_1"]["coords"]) 
        time.sleep(0.1)
        pyautogui.click(MAPA_UI["vista_menu"]["next_dropdowns"]["next_1"]["coords"]) 
        time.sleep(0.25)           
        pyautogui.click(MAPA_UI["vista_menu"]["next_dropdowns"]["next_1"]["form_5"])
        time.sleep(0.1)
        
        pyautogui.click(coords_item2)
        time.sleep(0.1)
        pyautogui.press('delete')
        pyautogui.press('enter')

    elif es_pieza and not es_volumen:
        pyautogui.click(coords_item1)
        time.sleep(0.1)
        pyautogui.write("1. PIEZA X PIEZA", interval=0.05)
        
        pyautogui.click(MAPA_UI["vista_menu"]["next_dropdowns"]["next_1"]["coords"]) 
        time.sleep(0.1)
        pyautogui.click(MAPA_UI["vista_menu"]["next_dropdowns"]["next_1"]["coords"]) 
        time.sleep(0.25)           
        pyautogui.click(MAPA_UI["vista_menu"]["next_dropdowns"]["next_1"]["form_2"])
        time.sleep(0.1)
        
        pyautogui.click(coords_item2)
        time.sleep(0.1)
        pyautogui.press('delete')
        pyautogui.press('enter')

    elif es_pieza and not es_volumen:
        pyautogui.click(coords_item1)
        time.sleep(0.1)
        pyautogui.write("1. PIEZA X PIEZA", interval=0.05)
        
        # Doble clic para asegurar que el dropdown abra
        pyautogui.click(1000, 230) 
        time.sleep(0.1)
        pyautogui.click(1000, 230) 
        time.sleep(0.25)           
        pyautogui.click(MAPA_UI["vista_menu"]["next_dropdowns"]["next_1"]["form_2"])
        time.sleep(0.1)
        
        pyautogui.click(coords_item2)
        time.sleep(0.1)
        pyautogui.press('delete')
        pyautogui.press('enter')

    # --- D. INYECCIÓN EN FORMS ---
    pyautogui.scroll(1500) 
    time.sleep(0.5) 

    if es_pieza:
        print("\n➤ [PIEZA] Inyectando Ubicaciones en Form 3...")
        pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"]["form_3"])
        time.sleep(0.75) 
        inyectar_datos_en_tabla(dict_ubicacion, es_ubicacion=True, es_flujo_volumen=False)
        
        print("➤ [PIEZA] Inyectando Variables en Form 4...")
        pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"]["form_4"])
        time.sleep(0.75) 
        inyectar_datos_en_tabla(dict_captura, es_ubicacion=False, es_flujo_volumen=False)

    if es_volumen:
        print("\n➤ [VOLUMEN] Inyectando Ubicaciones en Form 6...")
        pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"]["form_6"])
        time.sleep(0.75) 
        inyectar_datos_en_tabla(dict_ubicacion, es_ubicacion=True, es_flujo_volumen=True)
        
        print("➤ [VOLUMEN] Inyectando Variables en Form 7...")
        x_f7, y_f7 = MAPA_UI["vista_form"]["seleccion_forms"]["form_7"]["coords"]
        pyautogui.click(x_f7, y_f7)
        time.sleep(0.5) 
        
        # EL SCROLL FALTANTE PARA MANTENER LA INTERFAZ EN SU LUGAR
        pyautogui.scroll(1500) 
        time.sleep(0.25)
        
        inyectar_datos_en_tabla(dict_captura, es_ubicacion=False, es_flujo_volumen=True)

    print("\n✅ ¡ARCHIVO AGX GENERADO Y LIMPIO!")

except Exception as e:
    print(f"\n❌ El bot se detuvo por un error: {e}")