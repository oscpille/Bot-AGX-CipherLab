import pandas as pd
import unicodedata
import pyautogui
import time
import sys
import textwrap 
import re 
import math
from mapeo_batch import MAPA_UI 

# =========================================================
# 1. FUNCIONES AUXILIARES Y DE INFRAESTRUCTURA RELACIONAL
# =========================================================
def limpiar_texto(texto):
    """Quita acentos y pasa a minúsculas para comparaciones exactas."""
    texto_sin_acentos = unicodedata.normalize('NFD', str(texto)).encode('ascii', 'ignore').decode('utf-8')
    return texto_sin_acentos.lower().strip()

def escribir_celda(row_idx, data_type, prompt_text, min_len="", max_len="", field_select=""):
    """Escribe de manera limpia y veloz un renglón de la tabla sin parpadeos."""
    columnas = MAPA_UI["vista_form"]["tabla"]["columnas_x"]
    y_actual = MAPA_UI["vista_form"]["tabla"]["filas_y"][row_idx]
    
    # 1. Tipo de dato
    pyautogui.click(columnas["data_type"], y_actual)
    time.sleep(0.05)
    pyautogui.click(columnas["data_type"], y_actual)
    time.sleep(0.05)
    pyautogui.press('n') # Reset a Nil
    time.sleep(0.05)
    
    if data_type in MAPA_UI["vista_form"]["tabla"]["logica_data_type"]["secuencias"]:
        seq = MAPA_UI["vista_form"]["tabla"]["logica_data_type"]["secuencias"][data_type]
        for _ in range(seq["pulsaciones"]):
            pyautogui.press(seq["tecla"])
            time.sleep(0.03)
    pyautogui.press('enter')
    time.sleep(0.05)
    
    # 2. Escribir Prompt (Si aplica)
    if prompt_text:
        pyautogui.click(columnas["prompt"], y_actual)
        time.sleep(0.05)
        pyautogui.write(prompt_text, interval=0.02)
        
    # 3. Longitudes (Si aplica)
    if min_len:
        pyautogui.click(columnas["min_length"], y_actual)
        time.sleep(0.05)
        pyautogui.write(min_len, interval=0.02)
    if max_len:
        pyautogui.click(columnas["max_length"], y_actual)
        time.sleep(0.05)
        pyautogui.write(max_len, interval=0.02)
        
    # 4. Asignación de Llaves Referenciales de Campos (Field)
    if field_select:
        pyautogui.click(columnas["variables_field"], y_actual)
        time.sleep(0.05)
        pyautogui.click(columnas["variables_field"], y_actual)
        time.sleep(0.05)
        pyautogui.press('n') # Resetea a Nil
        time.sleep(0.05)
        for _ in range(field_select.lower().count('f')):
            pyautogui.press('f')
            time.sleep(0.03)
        pyautogui.press('enter')
        time.sleep(0.05)

def configurar_1st_lookup(form_coords):
    """Entra a la pantalla de Login (Form 2 o 5), activa el 1st Lookup y sus Fields."""
    pyautogui.click(form_coords)
    time.sleep(0.75)
    
    pyautogui.click(MAPA_UI["vista_form"]["sub_menus"]["lookup"]["1st_lookup"])
    time.sleep(0.2)
    
    # Renglón 2 (Contrasena:) -> Field 1
    escribir_celda(1, "integer", "Contrasena: ", "5", "5", "field_1")
    # Renglón 3 (Operador:) -> Field 2
    escribir_celda(2, "lookup", "Operador: ", "", "", "field_2")
    
    # Limpieza absoluta de las celdas restantes de la pantalla de login
    for i in range(3, 8):
        escribir_celda(i, "nil", "")

def configurar_propiedades_form(esc_id, next_id, record_tipo):
    """Enruta la navegación entre pantallas usando atajos de teclado (F y M)."""
    props = MAPA_UI["vista_form"]["properties"]
    
    def aplicar_atajo(valor):
        """Pulsa F o M la cantidad exacta de veces según el número destino."""
        if isinstance(valor, int):
            for _ in range(valor):
                pyautogui.press('f')
                time.sleep(0.03)
        elif isinstance(valor, str) and "menu" in valor.lower():
            # Extrae el número del texto (ej. de "menu 2" saca el 2)
            num = int(re.search(r'\d+', valor).group())
            for _ in range(num):
                pyautogui.press('m')
                time.sleep(0.03)
        
        # ¡EL SALVAVIDAS! Forzamos el Enter para cerrar el menú desplegable
        pyautogui.press('enter')
        time.sleep(0.1)

    # 1. Enrutar ESC
    pyautogui.click(props["esc"]["coords"])
    time.sleep(0.1)
    aplicar_atajo(esc_id)
    
    # 2. Enrutar NEXT
    pyautogui.click(props["next"]["coords"])
    time.sleep(0.1)
    aplicar_atajo(next_id)
    
    # 3. Enrutar RECORD (Tu truco P -> S x4)
    pyautogui.click(props["record"]["coords"])
    time.sleep(0.1)
    
    pyautogui.press('p') # Fuerza a Pass down
    time.sleep(0.1)
    
    if record_tipo == 'save':
        for _ in range(4):
            pyautogui.press('s')
            time.sleep(0.03)
            
    # ¡EL SALVAVIDAS X2!
    pyautogui.press('enter')
    time.sleep(0.1)

def asignar_piscina_forms(es_pieza, es_volumen, dict_captura, dict_ubicacion, separar_ubicacion):
    """Calcula matemáticamente y distribuye dinámicamente los 10 Forms de la piscina."""
    forms_disponibles = list(range(1, 11))
    rutas = {}
    total_vars = len(dict_captura)
    
    try:
        if es_pieza:
            rutas['pieza'] = {
                'login': forms_disponibles.pop(0),
                'loc1': forms_disponibles.pop(0),
                'loc2': forms_disponibles.pop(0) if (separar_ubicacion and len(dict_ubicacion) > 1) else None
            }
            paginas = math.ceil(total_vars / 5) if total_vars > 0 else 1
            rutas['pieza']['datos'] = [forms_disponibles.pop(0) for _ in range(paginas)]
            
        if es_volumen:
            rutas['volumen'] = {
                'login': forms_disponibles.pop(0),
                'loc1': forms_disponibles.pop(0),
                'loc2': forms_disponibles.pop(0) if (separar_ubicacion and len(dict_ubicacion) > 1) else None
            }
            # Lógica contractil para Volumen: Páginas intermedias de 6, última página de hasta 5 variables
            v_left = total_vars
            paginas_v = 0
            while v_left > 0:
                paginas_v += 1
                v_left = 0 if v_left <= 5 else v_left - 6
            if paginas_v == 0: paginas_v = 1
            rutas['volumen']['datos'] = [forms_disponibles.pop(0) for _ in range(paginas_v)]
            
    except IndexError:
        print("\n❌ ERROR CRÍTICO: ¡La solicitud desborda la capacidad de 10 Forms de Forge AG!")
        sys.exit()
        
    return rutas

# =========================================================
# 2. PROCESAMIENTO E INTERPRETACIÓN DE DATOS (FASE 2)
# =========================================================
ruta_excel = r"C:\Users\dell\OneDrive - Profesionales en Inventarios SA de CV\FORMATO DE SOLICITUD DE AGX.xlsx"
ruta_csv = r"C:\Users\dell\Documents\Bot AGX\UltimaFila.csv"

TRADUCCION_TIPOS = {
    "num": "integer", "numerico": "integer", "entero": "integer", "decimal": "real",
    "alfanum": "alphameric", "alfanumerico": "alphameric", "texto": "text", "letras": "letter"
}

try:
    print("➤ Iniciando lectura desde OneDrive...")
    df = pd.read_excel(ruta_excel, usecols="F:K", engine='openpyxl').dropna(how='all')
    df.iloc[-1:].to_csv(ruta_csv, index=False, encoding='utf-8-sig')
    solicitud = pd.read_csv(ruta_csv, encoding='utf-8-sig').iloc[0]
    
    cliente = str(solicitud['INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:']).strip().upper()
    flujo_crudo = limpiar_texto(solicitud['FLUJO OPERATIVO:'])
    es_pieza = "pieza" in flujo_crudo or "ambos" in flujo_crudo
    es_volumen = "volumen" in flujo_crudo or "ambos" in flujo_crudo
    
    dict_ubicacion, dict_captura = {}, {}
    print("➤ Ejecutando Analizador Léxico (Regex)...")
    
    for linea in str(solicitud['DATOS REQUERIDOS']).split('\n'):
        linea = linea.strip()
        if not linea: continue
        linea_limpia = linea.lower().replace(',', '').replace('.', '').replace(';', '')
        match_nombre = re.match(r'^([^0-9:]+)', linea)
        if not match_nombre: continue
        
        nombre_original = re.sub(r'(?i)\s+(con|de|mínimo|minimo|en)$', '', match_nombre.group(1).strip()).strip()
        nombre_logico = limpiar_texto(nombre_original)
        
        min_max_final = "3-15" # Fallback estándar
        rango_match = re.search(r'(\d+)\s*(?:-|a|al|maximo|máximo)\s*(\d+)', linea_limpia)
        if rango_match:
            min_max_final = f"{rango_match.group(1)}-{rango_match.group(2)}"
        else:
            num_match = re.search(r'\b(\d+)\b', linea_limpia)
            if num_match: min_max_final = f"{num_match.group(1)}-{num_match.group(1)}"
            
        tipo_bruto = "alfanumerico"
        for t in ["numérico", "numerico", "num", "entero", "decimal", "texto", "letras"]:
            if t in linea_limpia: tipo_bruto = t; break
        
        datos = {'nombre_pantalla': nombre_original, 'longitud': min_max_final, 'tipo': TRADUCCION_TIPOS.get(limpiar_texto(tipo_bruto), "alphameric")}
        
        if "marbete" in nombre_logico or "ubicacion" in nombre_logico:
            dict_ubicacion[nombre_logico] = datos
        else:
            dict_captura[nombre_logico] = datos

    multiplo_sku = 20
    for k, v in dict_captura.items():
        if "sku" in k:
            multiplo_sku = ((int(v['longitud'].split('-')[1]) + 4) // 5) * 5; break

    regla_separar = "siguiente" in str(solicitud['¿QUÉ NIVEL DE PRIORIDAD DAREMOS?']).lower()
    plan_vuelo = asignar_piscina_forms(es_pieza, es_volumen, dict_captura, dict_ubicacion, regla_separar)

except Exception as e:
    print(f"❌ Error en la curación de datos: {e}"); sys.exit()

# =========================================================
# 3. EL CEREBRO DE EJECUCIÓN PROCEDURAL (FASE 3)
# =========================================================
print("🤖 Iniciando Bot en 5 segundos..."); time.sleep(5)

try:
    # --- STEP 1: CONFIGURAR LOS MENÚS EN CASCADA ---
    print("\n➤ Desplegando directorio Menu...")
    pyautogui.click(MAPA_UI["directorio_izquierdo"]["menu"]); time.sleep(0.5)
    pyautogui.click(MAPA_UI["vista_menu"]["menu_1"]); time.sleep(0.75)
    
    lineas_cliente = textwrap.wrap(cliente, width=16, break_long_words=True)
    coords_items = [MAPA_UI["vista_menu"]["items"]["item_5"]["coords"], MAPA_UI["vista_menu"]["items"]["item_6"]["coords"], MAPA_UI["vista_menu"]["items"]["item_7"]["coords"]]
    dicc_nexts = [MAPA_UI["vista_menu"]["next_dropdowns"]["next_5"], MAPA_UI["vista_menu"]["next_dropdowns"]["next_6"], MAPA_UI["vista_menu"]["next_dropdowns"]["next_7"]]
    
    for i in range(min(len(lineas_cliente), 3)):
        pyautogui.click(coords_items[i]); time.sleep(0.05)
        pyautogui.write(lineas_cliente[i], interval=0.03)
        pyautogui.click(dicc_nexts[i]["coords"]); time.sleep(0.05)
        pyautogui.click(dicc_nexts[i]["coords"]); time.sleep(0.15)
        pyautogui.click(dicc_nexts[i]["menu_2"]); time.sleep(0.05)

    # --- CONFIGURAR MENU 2 CON TRUCO ALFABÉTICO ('F') ---
    print("➤ Configurando Menu 2 (Tipos de Conteo)...")
    pyautogui.click(MAPA_UI["vista_menu"]["menu_2"])
    time.sleep(0.75) 

    coords_item1 = MAPA_UI["vista_menu"]["items"]["item_1"]["coords"]
    coords_item2 = MAPA_UI["vista_menu"]["items"]["item_2"]["coords"]
    next_1 = MAPA_UI["vista_menu"]["next_dropdowns"]["next_1"]["coords"]
    next_2 = MAPA_UI["vista_menu"]["next_dropdowns"]["next_2"]["coords"]

    def seleccionar_form_dropdown(coordenada_next, num_form):
        """Un clic en Next y teclea 'F' las veces necesarias."""
        pyautogui.click(coordenada_next)
        time.sleep(0.1)
        for _ in range(num_form):
            pyautogui.press('f')
            time.sleep(0.03)
            
        # ¡EL SALVAVIDAS! Cerramos el menú para no devorar clics futuros
        pyautogui.press('enter')
        time.sleep(0.1)

    if es_pieza and es_volumen:
        # Item 1 -> Pieza
        pyautogui.click(coords_item1)
        time.sleep(0.05)
        pyautogui.write("1. PIEZA X PIEZA", interval=0.02)
        seleccionar_form_dropdown(next_1, plan_vuelo['pieza']['login'])
        
        # Item 2 -> Volumen
        pyautogui.click(coords_item2)
        time.sleep(0.05)
        pyautogui.write("2. VOLUMEN", interval=0.02)
        seleccionar_form_dropdown(next_2, plan_vuelo['volumen']['login'])

    elif es_pieza:
        pyautogui.click(coords_item1)
        time.sleep(0.05)
        pyautogui.write("1. PIEZA X PIEZA", interval=0.02)
        seleccionar_form_dropdown(next_1, plan_vuelo['pieza']['login'])
        
        pyautogui.click(coords_item2)
        time.sleep(0.05)
        pyautogui.press('delete')
        pyautogui.press('enter')

    elif es_volumen:
        pyautogui.click(coords_item1)
        time.sleep(0.05)
        pyautogui.write("1. VOLUMEN", interval=0.02)
        seleccionar_form_dropdown(next_1, plan_vuelo['volumen']['login'])
        
        pyautogui.click(coords_item2)
        time.sleep(0.05)
        pyautogui.press('delete')
        pyautogui.press('enter')

    # --- STEP 2: COLAPSAR Y PASAR A LOOKUPS ---
    pyautogui.click(MAPA_UI["directorio_izquierdo"]["menu"]); time.sleep(0.4)
    pyautogui.click(MAPA_UI["directorio_izquierdo"]["lookup"]); time.sleep(0.4)
    
    # Configurar DBFs de manera directa (Sin parpadeos)
    pyautogui.click(MAPA_UI["vista_lookup"]["archivos"]["1st_lookup"]); time.sleep(0.5)
    pyautogui.click(MAPA_UI["vista_lookup"]["configuracion"]["max_length_1"]["coords"]); pyautogui.write('10')
    pyautogui.click(MAPA_UI["vista_lookup"]["configuracion"]["max_length_2"]["coords"]); pyautogui.write('10')
    
    pyautogui.click(MAPA_UI["vista_lookup"]["archivos"]["2nd_lookup"]); time.sleep(0.5)
    pyautogui.click(MAPA_UI["vista_lookup"]["configuracion"]["max_length_1"]["coords"]); pyautogui.write(str(multiplo_sku))

    # --- STEP 3: DESPLEGAR COMPACTO DE FORMS ---
    pyautogui.click(MAPA_UI["directorio_izquierdo"]["form"]); time.sleep(0.4)
    listado_vars = list(dict_captura.values())

    # =========================================================
    # INYECCIÓN CONTINUA DE LA RAMA A: PIEZA X PIEZA
    # =========================================================
    if es_pieza:
        p_route = plan_vuelo['pieza']
        print(f"\n➤ Construyendo Flujo Procedural de Piezas (Inicia Form {p_route['login']})...")
        
        # 1. Login Pieza
        configurar_1st_lookup(MAPA_UI["vista_form"]["seleccion_forms"][f"form_{p_route['login']}"])
        configurar_propiedades_form("menu 2", p_route['loc1'], "pass_down")
        
        # 2. Localizaciones (Evaluación de Separación Dinámica)
        if p_route['loc2']:
            pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"][f"form_{p_route['loc1']}"]); time.sleep(0.5)
            escribir_celda(2, "prompt", "Marbete: ")
            escribir_celda(7, "prompt", "CONTEO X PIEZA")
            configurar_propiedades_form(p_route['login'], p_route['loc2'], "pass_down")
            
            pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"][f"form_{p_route['loc2']}"]); time.sleep(0.5)
            escribir_celda(4, "prompt", "Ubicacion: ")
            escribir_celda(7, "prompt", "CONTEO X PIEZA")
            configurar_propiedades_form(p_route['loc1'], p_route['datos'][0], "pass_down")
            esc_retorno_datos = p_route['loc2']
        else:
            pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"][f"form_{p_route['loc1']}"]); time.sleep(0.5)
            escribir_celda(2, "prompt", "Marbete: ")
            escribir_celda(4, "prompt", "Ubicacion: ")
            escribir_celda(7, "prompt", "CONTEO X PIEZA")
            configurar_propiedades_form(p_route['login'], p_route['datos'][0], "pass_down")
            esc_retorno_datos = p_route['loc1']

        # 3. Datos Pieza Paginados (Bloques de 5 variables)
        total_pags_p = len(p_route['datos'])
        for idx, f_num in enumerate(p_route['datos']):
            pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"][f"form_{f_num}"]); time.sleep(0.5)
            pyautogui.click(MAPA_UI["vista_form"]["sub_menus"]["lookup"]["2nd_lookup"]); time.sleep(0.1)
            
            # Cabecera indicadora de página
            escribir_celda(0, "prompt", f"CONTEO X PZ {idx+1}/{total_pags_p}")
            
            # Extraer rebanada de 5 variables
            rebanada = listado_vars[idx*5 : (idx+1)*5]
            for r_idx, v_info in enumerate(rebanada):
                escribir_celda(r_idx + 1, v_info['tipo'], v_info['nombre_pantalla'], v_info['longitud'].split('-')[0], v_info['longitud'].split('-')[1], "field_1" if "sku" in limpiar_texto(v_info['nombre_pantalla']) else "")
                
            # Limpiar renglones intermedios sobrantes antes del pie de página
            for v_blank in range(len(rebanada) + 1, 6):
                escribir_celda(v_blank, "nil", "")
                
            # Configuración del Pie de Página de Navegación y Enrutamiento del Scan Loop
            es_ultima = (idx == total_pags_p - 1)
            escribir_celda(6, "pause", "[ENTER] O [ESC]" if es_ultima else "SIGUIENTE ")
            escribir_celda(7, "fixed_data", "1")
            
            p_esc = esc_retorno_datos if idx == 0 else p_route['datos'][idx - 1]
            p_next = p_route['datos'][0] if es_ultima else p_route['datos'][idx + 1] # ¡AQUÍ SE CURA EL BUCLE CONTINUO!
            p_record = "save" if es_ultima else "pass_down"
            configurar_propiedades_form(p_esc, p_next, p_record)

    # =========================================================
    # INYECCIÓN CONTINUA DE LA RAMA B: VOLUMEN
    # =========================================================
    if es_volumen:
        v_route = plan_vuelo['volumen']
        print(f"\n➤ Construyendo Flujo Procedural de Volumen (Inicia Form {v_route['login']})...")
        
        # 1. Login Volumen
        configurar_1st_lookup(MAPA_UI["vista_form"]["seleccion_forms"][f"form_{v_route['login']}"])
        configurar_propiedades_form("menu 2", v_route['loc1'], "pass_down")
        
        # 2. Localizaciones Volumen
        if v_route['loc2']:
            pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"][f"form_{v_route['loc1']}"]); time.sleep(0.5)
            escribir_celda(2, "prompt", "Marbete: ")
            escribir_celda(7, "prompt", "CONTEO VOLUMEN")
            configurar_propiedades_form(v_route['login'], v_route['loc2'], "pass_down")
            
            pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"][f"form_{v_route['loc2']}"]); time.sleep(0.5)
            escribir_celda(4, "prompt", "Ubicacion: ")
            escribir_celda(7, "prompt", "CONTEO VOLUMEN")
            configurar_propiedades_form(v_route['loc1'], v_route['datos'][0], "pass_down")
            esc_retorno_datos_v = v_route['loc2']
        else:
            pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"][f"form_{v_route['loc1']}"]); time.sleep(0.5)
            escribir_celda(2, "prompt", "Marbete: ")
            escribir_celda(4, "prompt", "Ubicacion: ")
            escribir_celda(7, "prompt", "CONTEO VOLUMEN")
            configurar_propiedades_form(v_route['login'], v_route['datos'][0], "pass_down")
            esc_retorno_datos_v = v_route['loc1']

        # 3. Datos Volumen Paginados (Lógica Contractil Automatizada)
        total_pags_v = len(v_route['datos'])
        v_idx_global = 0
        
        for idx, f_num in enumerate(v_route['datos']):
            pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"][f"form_{f_num}"]); time.sleep(0.5)
            pyautogui.click(MAPA_UI["vista_form"]["sub_menus"]["lookup"]["2nd_lookup"]); time.sleep(0.1)
            
            es_ultima = (idx == total_pags_v - 1)
            escribir_celda(0, "prompt", f"CONTEO X VOL {idx+1}/{total_pags_v}")
            
            # Slicing dinámico dependiendo de la zona de la página
            capacidad = 5 if es_ultima else 6
            rebanada = listado_vars[v_idx_global : v_idx_global + capacidad]
            v_idx_global += len(rebanada)
            
            for r_idx, v_info in enumerate(rebanada):
                escribir_celda(r_idx + 1, v_info['tipo'], v_info['nombre_pantalla'], v_info['longitud'].split('-')[0], v_info['longitud'].split('-')[1], "field_1" if "sku" in limpiar_texto(v_info['nombre_pantalla']) else "")
                
            # Limpieza y estructuración del pie flotante de volumen
            if es_ultima:
                for v_blank in range(len(rebanada) + 1, 6):
                    escribir_celda(v_blank, "nil", "")
                escribir_celda(6, "integer", "Cantidad: ")
                escribir_celda(7, "prompt", "CONTEO VOLUMEN")
            else:
                for v_blank in range(len(rebanada) + 1, 7):
                    escribir_celda(v_blank, "nil", "")
                escribir_celda(7, "pause", "SIGUIENTE ")
                
            v_esc = esc_retorno_datos_v if idx == 0 else v_route['datos'][idx - 1]
            v_next = v_route['datos'][0] if es_ultima else v_route['datos'][idx + 1] # ¡BUCLE CONTINUO CERRADO CON ÉXITO!
            v_record = "save" if es_ultima else "pass_down"
            configurar_propiedades_form(v_esc, v_next, v_record)

    print("\n✅ ¡SISTEMA AGX PROCEDURAL GENERADO PERFECTAMENTE EN LOS 10 FORMS!")

except Exception as e:
    print(f"\n❌ El bot dinámico falló en ejecución: {e}")