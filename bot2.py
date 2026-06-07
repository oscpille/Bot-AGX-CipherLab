import pandas as pd
import unicodedata
import pyautogui
import time
import sys
import textwrap 
import re 
from mapeo_batch import MAPA_UI 

# =========================================================
# 1. FUNCIONES AUXILIARES Y DE INYECCIÓN
# =========================================================
def limpiar_texto(texto):
    """Quita acentos y pasa a minúsculas para comparaciones exactas."""
    texto_sin_acentos = unicodedata.normalize('NFD', str(texto)).encode('ascii', 'ignore').decode('utf-8')
    return texto_sin_acentos.lower().strip()

def configurar_1st_lookup(form_coords):
    """
    Entra a Form 2 o Form 5, activa el 1st Lookup y asigna Field 1 y Field 2.
    """
    pyautogui.click(form_coords)
    time.sleep(0.75)
    
    # 1. Encender el Radio Button de 1st Lookup
    pyautogui.click(MAPA_UI["vista_form"]["sub_menus"]["lookup"]["1st_lookup"])
    time.sleep(0.2)
    
    col_field = MAPA_UI["vista_form"]["tabla"]["columnas_x"]["variables_field"]
    filas_y = MAPA_UI["vista_form"]["tabla"]["filas_y"]
    
    # 2. Configurar Fila 2 (Contraseña) -> Field 1
    pyautogui.click(col_field, filas_y[1])
    time.sleep(0.1)
    pyautogui.click(col_field, filas_y[1]) 
    time.sleep(0.1)
    pyautogui.press('n') 
    time.sleep(0.1)
    pyautogui.press('f') 
    time.sleep(0.1)
    pyautogui.press('enter')
    time.sleep(0.1)
    
    # 3. Configurar Fila 3 (Operador) -> Field 2
    pyautogui.click(col_field, filas_y[2])
    time.sleep(0.1)
    pyautogui.click(col_field, filas_y[2]) 
    time.sleep(0.1)
    pyautogui.press('n') 
    time.sleep(0.1)
    pyautogui.press('f') 
    time.sleep(0.1)
    pyautogui.press('f') 
    time.sleep(0.1)
    pyautogui.press('enter')
    time.sleep(0.1)

def inyectar_datos_en_tabla(diccionario_datos, es_ubicacion=False, es_flujo_volumen=False):
    """
    Inyecta datos respetando las Zonas Seguras de la plantilla AGX,
    omitiendo duplicados y asignando Field 1 al SKU.
    """
    columnas = MAPA_UI["vista_form"]["tabla"]["columnas_x"]
    filas_y = MAPA_UI["vista_form"]["tabla"]["filas_y"]
    
    indice_fila_captura = 1 
    filas_usadas = [] 
    
    tiene_ambos_ubicaciones = any("marbete" in k for k in diccionario_datos) and any("ubicacion" in k for k in diccionario_datos)
    
    # --- DETERMINAR LÍMITES Y ZONAS SEGURAS ---
    if es_ubicacion:
        limite_indice = 7 
    elif es_flujo_volumen:
        limite_indice = 6 
    else:
        limite_indice = 5 
        
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
                if config['tipo'] == 'real':
                    print(f"   [!] Omitiendo '{config['nombre_pantalla']}' (Decimal) porque estamos en Volumen.")
                    continue 
                if "cantidad" in nombre_logico:
                    print(f"   [!] Omitiendo '{config['nombre_pantalla']}' porque ya viene por defecto en el Form 7.")
                    continue
                
            idx = indice_fila_captura
            indice_fila_captura += 1
            
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
        
        # 4. ASIGNACIÓN DE FIELD 1 PARA EL SKU
        if "sku" in nombre_logico:
            print(f"      [+] Vinculando SKU con Field 1...")
            pyautogui.click(columnas["variables_field"], y_actual)
            time.sleep(0.1)
            pyautogui.click(columnas["variables_field"], y_actual)
            time.sleep(0.1)
            pyautogui.press('n') 
            time.sleep(0.1)
            pyautogui.press('f') 
            time.sleep(0.1)
            pyautogui.press('enter')
            time.sleep(0.1)
        
    # --- B. LIMPIEZA CON NIL ---
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
# 2. RUTAS, TRADUCCIÓN Y LECTURA DE EXCEL (REGEX)
# =========================================================
ruta_excel = r"C:\Users\dell\OneDrive - Profesionales en Inventarios SA de CV\FORMATO DE SOLICITUD DE AGX.xlsx"
ruta_csv = r"C:\Users\dell\Documents\Bot AGX\UltimaFila.csv"

TRADUCCION_TIPOS = {
    "num": "integer",
    "numerico": "integer",
    "entero": "integer",
    "decimal": "real",
    "alfanum": "alphameric",
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
    
    cliente = str(solicitud['INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:']).strip().upper()
    flujo_crudo = limpiar_texto(solicitud['FLUJO OPERATIVO:'])
    
    es_pieza = "pieza" in flujo_crudo or "ambos" in flujo_crudo
    es_volumen = "volumen" in flujo_crudo or "ambos" in flujo_crudo
    
    print(f"📦 Cliente: {cliente}")
    print(f"🔄 Flujo: Pieza={es_pieza} | Volumen={es_volumen}\n")
    
    dict_ubicacion = {}
    dict_captura = {}
    
    datos_req_limpios = str(solicitud['DATOS REQUERIDOS'])
    print("➤ Procesando y limpiando variables del usuario...")
    
    for linea in datos_req_limpios.split('\n'):
        linea = linea.strip()
        if not linea: continue

        linea_limpia = linea.lower().replace(',', '').replace('.', '').replace(';', '')

        match_nombre = re.match(r'^([^0-9:]+)', linea)
        if not match_nombre:
            continue
            
        nombre_original = match_nombre.group(1).strip()
        nombre_original = re.sub(r'(?i)\s+(con|de|mínimo|minimo|en)$', '', nombre_original).strip()
        nombre_logico = limpiar_texto(nombre_original)

        min_max_final = ""
        rango_match = re.search(r'(\d+)\s*(?:-|a|al|maximo|máximo)\s*(\d+)', linea_limpia)
        
        if rango_match:
            min_max_final = f"{rango_match.group(1)}-{rango_match.group(2)}"
        else:
            num_match = re.search(r'\b(\d+)\b', linea_limpia)
            if num_match:
                min_max_final = f"{num_match.group(1)}-{num_match.group(1)}"
            elif "ddmm" in linea_limpia: 
                long_calc = 8 if "aaaa" in linea_limpia else 6
                min_max_final = f"{long_calc}-{long_calc}"

        if not min_max_final:
            print(f"   [!] Ignorada por falta de longitud medible: '{linea}'")
            continue

        tipo_bruto = "alfanumerico" 
        tipos_clave = ["numérico", "numerico", "num", "entero", "decimal", "texto", "letras", "ddmmaa", "ddmmaaaa"]
        for t in tipos_clave:
            if t in linea_limpia:
                tipo_bruto = t
                break

        tipo_forge = TRADUCCION_TIPOS.get(limpiar_texto(tipo_bruto), "alphameric")

        datos = {
            'nombre_pantalla': nombre_original,
            'longitud': min_max_final,
            'tipo': tipo_forge
        }
        
        if "marbete" in nombre_logico or "ubicacion" in nombre_logico:
            dict_ubicacion[nombre_logico] = datos
        else:
            dict_captura[nombre_logico] = datos

    # --- CÁLCULO DEL MÚLTIPLO DE 5 PARA 2ND LOOKUP ---
    multiplo_sku = 20 
    for clave, datos in dict_captura.items():
        if "sku" in clave:
            max_len = int(datos['longitud'].split('-')[1])
            multiplo_sku = ((max_len + 4) // 5) * 5 
            print(f"🔍 SKU detectado con Max Length: {max_len}. Múltiplo asignado al 2nd Lookup: {multiplo_sku}")
            break

except Exception as e:
    print(f"❌ Error al procesar datos: {e}")
    sys.exit()

# =========================================================
# 3. EL CEREBRO DEL BOT (FASE 3 - EJECUCIÓN CRONOLÓGICA)
# =========================================================
print("🤖 Iniciando Bot en 5 segundos...")
print("⚠️ Activa Forge AG y suelta el ratón.")
time.sleep(5) 

try:
    # --- A. ABRIR Y CONFIGURAR MENÚS ---
    print("\n➤ [PASO 1] Desplegando directorio Menu...")
    pyautogui.click(MAPA_UI["directorio_izquierdo"]["menu"])
    time.sleep(0.5) 

    print("➤ Modificando Menu 1 (Cabecera del Cliente)...")
    pyautogui.click(MAPA_UI["vista_menu"]["menu_1"])
    time.sleep(0.75) 
    
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
    
    # Cortar el nombre e inyectarlo renglón por renglón
    lineas_cliente = textwrap.wrap(cliente, width=16, break_long_words=True)
    
    for i in range(3): 
        if i < len(lineas_cliente):
            # 1. Escribir el texto (Sin borrar y sin dar Enter)
            pyautogui.click(coords_items[i])
            time.sleep(0.1)
            pyautogui.write(lineas_cliente[i], interval=0.05)
            
            # 2. Configurar la columna Next (INTACTA)
            pyautogui.click(dicc_nexts[i]["coords"]) 
            time.sleep(0.1)
            pyautogui.click(dicc_nexts[i]["coords"]) 
            time.sleep(0.25)
            
            pyautogui.click(dicc_nexts[i]["menu_2"])
            time.sleep(0.1)

    print("➤ Configurando Menu 2 (Tipos de Conteo)...")
    pyautogui.click(MAPA_UI["vista_menu"]["menu_2"])
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

    # --- B. COLAPSAR MENÚS Y ABRIR LOOKUPS ---
    print("\n➤ [PASO 2] Colapsando Menu para liberar espacio...")
    pyautogui.click(MAPA_UI["directorio_izquierdo"]["menu"])
    time.sleep(0.5)

    print("➤ Desplegando directorio Lookup...")
    pyautogui.click(MAPA_UI["directorio_izquierdo"]["lookup"])
    time.sleep(0.5)

    print("➤ Configurando Lookup Files (1st y 2nd)...")
    
    # 1st Lookup File
    pyautogui.click(MAPA_UI["vista_lookup"]["archivos"]["1st_lookup"])
    time.sleep(0.75)
    
    pyautogui.click(MAPA_UI["vista_lookup"]["configuracion"]["max_length_1"]["coords"])
    time.sleep(0.1)
    pyautogui.write('10', interval=0.05)
    
    pyautogui.click(MAPA_UI["vista_lookup"]["configuracion"]["max_length_2"]["coords"])
    time.sleep(0.1)
    pyautogui.write('10', interval=0.05)
    
    # 2nd Lookup File
    pyautogui.click(MAPA_UI["vista_lookup"]["archivos"]["2nd_lookup"])
    time.sleep(0.75)
    
    pyautogui.click(MAPA_UI["vista_lookup"]["configuracion"]["max_length_1"]["coords"])
    time.sleep(0.1)
    pyautogui.write(str(multiplo_sku), interval=0.05)

    # --- C. ABRIR FORMS E INYECTAR DATOS ---
    print("\n➤ [PASO 3] Desplegando directorio Form...")
    pyautogui.click(MAPA_UI["directorio_izquierdo"]["form"])
    time.sleep(0.5)

    if es_pieza:
        print("\n➤ [PIEZA] Configurando Operador y Contraseña en Form 2...")
        configurar_1st_lookup(MAPA_UI["vista_form"]["seleccion_forms"]["form_2"])

        print("➤ [PIEZA] Inyectando Ubicaciones en Form 3...")
        pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"]["form_3"])
        time.sleep(0.75) 
        inyectar_datos_en_tabla(dict_ubicacion, es_ubicacion=True, es_flujo_volumen=False)
        
        print("➤ [PIEZA] Inyectando Variables en Form 4...")
        pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"]["form_4"])
        time.sleep(0.75) 
        
        pyautogui.click(MAPA_UI["vista_form"]["sub_menus"]["lookup"]["2nd_lookup"])
        time.sleep(0.2)
        
        inyectar_datos_en_tabla(dict_captura, es_ubicacion=False, es_flujo_volumen=False)

    if es_volumen:
        print("\n➤ [VOLUMEN] Configurando Operador y Contraseña en Form 5...")
        configurar_1st_lookup(MAPA_UI["vista_form"]["seleccion_forms"]["form_5"])

        print("➤ [VOLUMEN] Inyectando Ubicaciones en Form 6...")
        pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"]["form_6"])
        time.sleep(0.75) 
        inyectar_datos_en_tabla(dict_ubicacion, es_ubicacion=True, es_flujo_volumen=True)
        
        print("➤ [VOLUMEN] Inyectando Variables en Form 7...")
        pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"]["form_7"])
        time.sleep(0.5) 
        
        pyautogui.click(MAPA_UI["vista_form"]["sub_menus"]["lookup"]["2nd_lookup"])
        time.sleep(0.2)
        
        inyectar_datos_en_tabla(dict_captura, es_ubicacion=False, es_flujo_volumen=True)

    print("\n✅ ¡ARCHIVO AGX GENERADO Y LIMPIO CON FLUJO TURBO CONTRACTIL!")

except Exception as e:
    print(f"\n❌ El bot se detuvo por un error: {e}")