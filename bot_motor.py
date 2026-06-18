import pyautogui
import time
import re
import textwrap
import pyperclip
import unicodedata
import os
from datetime import datetime
from config import DICCIONARIO_PREFIJOS, MAPA_UI
from extractor_datos import limpiar_texto

def quitar_acentos(texto):
    """Filtro para PyAutoGUI y Portapapeles: Quita acentos respetando mayúsculas."""
    return unicodedata.normalize('NFD', str(texto)).encode('ascii', 'ignore').decode('utf-8')

def calcular_prefijo(nombre_pantalla):
    """Analiza el texto de la pantalla, busca el prefijo ideal y le agrega '#'."""
    nombre_limpio = limpiar_texto(nombre_pantalla)
    
    for clave, prefijo in DICCIONARIO_PREFIJOS.items():
        if clave in nombre_limpio:
            return prefijo + "#"
            
    letras = re.sub(r'[^a-z]', '', nombre_limpio)
    if len(letras) >= 3:
        return letras[:3] + "#"
    elif len(letras) > 0:
        return letras + "#"
    return ""

def inyectar_texto_en_grid(texto_a_ingresar):
    """Convierte un string a valores ASCII y da clics matemáticos en el Grid."""
    grid = MAPA_UI["vista_more"]["grid_ascii"]
    
    pyautogui.click(grid["btn_clear"])
    time.sleep(0.04)
    
    for caracter in str(texto_a_ingresar):
        ascii_val = ord(caracter)
        col_idx = ascii_val // 16 
        row_idx = ascii_val % 16
        
        coord_x = grid["origen_x"] + (col_idx * grid["delta_x"])
        coord_y = grid["origen_y"] + (row_idx * grid["delta_y"])
        
        pyautogui.click(coord_x, coord_y)
        time.sleep(0.03)
        
    pyautogui.click(grid["btn_ok"])
    time.sleep(0.09)

def configurar_boton_more(row_idx, data_type, prefix_text="", input_mark_char=""):
    """Detecta el formato de la fila y configura prefijos (Grid ASCII) y marcas de entrada (Teclado directo)."""
    formatos = MAPA_UI["vista_form"]["tabla"]["formatos_more"]
    
    if data_type in formatos["bloqueado"] or data_type == "nil":
        return
        
    if data_type in formatos["formato_1"] and not prefix_text and not input_mark_char:
        return
        
    y_actual = MAPA_UI["vista_form"]["tabla"]["filas_y"][row_idx]
    pyautogui.click(MAPA_UI["vista_more"]["columna_more_x"], y_actual)
    time.sleep(0.26) 
    
    if data_type in formatos["formato_1"]:
        if prefix_text:
            pyautogui.click(MAPA_UI["vista_more"]["formato_1"]["check_prefix"])
            time.sleep(0.04)
            pyautogui.click(MAPA_UI["vista_more"]["formato_1"]["campo_prefix"])
            time.sleep(0.24) 
            inyectar_texto_en_grid(prefix_text)
            
        if input_mark_char:
            pyautogui.click(MAPA_UI["vista_more"]["formato_1"]["check_input_mark"])
            time.sleep(0.04)
            pyautogui.click(MAPA_UI["vista_more"]["formato_1"]["campo_input_mark"])
            time.sleep(0.04) 
            
            pyautogui.write(input_mark_char, interval=0.02)
            time.sleep(0.04)
            
    elif data_type in formatos["formato_2"]:
        pyautogui.click(MAPA_UI["vista_more"]["formato_2"]["check_save_field"])
        time.sleep(0.04)
        if prefix_text:
            pyautogui.click(MAPA_UI["vista_more"]["formato_2"]["check_prefix"])
            time.sleep(0.04)
            pyautogui.click(MAPA_UI["vista_more"]["formato_2"]["campo_prefix"])
            time.sleep(0.24)
            inyectar_texto_en_grid(prefix_text)
            
    elif data_type in formatos["formato_3"]:
        pyautogui.click(MAPA_UI["vista_more"]["formato_3"]["check_show_time"])
        time.sleep(0.04)
        
    pyautogui.press('enter') 
    time.sleep(0.04)

def escribir_celda(row_idx, data_type, prompt_text, min_len="", max_len="", num_fields=0, prefijo_forzado=None, input_mark_char=""):
    """Escribe velozmente un renglón, usa portapapeles y configura el botón More. Ignora filas vacías (nil)."""
    if data_type.lower() == "nil":
        return

    columnas = MAPA_UI["vista_form"]["tabla"]["columnas_x"]
    y_actual = MAPA_UI["vista_form"]["tabla"]["filas_y"][row_idx]
    
    pyautogui.click(columnas["data_type"], y_actual); time.sleep(0.03)
    pyautogui.click(columnas["data_type"], y_actual); time.sleep(0.03)
    pyautogui.press('n'); time.sleep(0.03)
    
    if data_type in MAPA_UI["vista_form"]["tabla"]["logica_data_type"]["secuencias"]:
        seq = MAPA_UI["vista_form"]["tabla"]["logica_data_type"]["secuencias"][data_type]
        for _ in range(seq["pulsaciones"]):
            pyautogui.press(seq["tecla"])
            time.sleep(0.03)
    pyautogui.press('enter'); time.sleep(0.03)
    
    if prompt_text:
        pyautogui.click(columnas["prompt"], y_actual); time.sleep(0.03)
        pyperclip.copy(quitar_acentos(prompt_text)); time.sleep(0.03)
        pyautogui.hotkey('ctrl', 'v'); time.sleep(0.03)
        
    if data_type.lower() != "lookup":
        if min_len:
            pyautogui.click(columnas["min_length"], y_actual); time.sleep(0.03)
            pyautogui.write(min_len, interval=0.02)
        if max_len:
            pyautogui.click(columnas["max_length"], y_actual); time.sleep(0.03)
            pyautogui.write(max_len, interval=0.02)
        
    if num_fields > 0:
        pyautogui.click(columnas["variables_field"], y_actual); time.sleep(0.03)
        pyautogui.click(columnas["variables_field"], y_actual); time.sleep(0.04)
        
        pyautogui.press('n'); time.sleep(0.09) 
        
        es_8200 = "scroll_tabla" in MAPA_UI.get("vista_form", {})
        
        for iteracion in range(num_fields):
            pyautogui.press('f')
            time.sleep(0.09)
            
            if es_8200 and iteracion == 0:
                pyautogui.press('enter')
                time.sleep(0.09)
                
        pyautogui.press('enter'); time.sleep(0.03) 

    prefijo_calculado = prefijo_forzado if prefijo_forzado is not None else (calcular_prefijo(prompt_text) if prompt_text else "")
    configurar_boton_more(row_idx, data_type, prefijo_calculado, input_mark_char)

def configurar_1st_lookup(form_coords, tipo_conteo, next_form_id):
    """Entra a la pantalla de Login, configura Properties y dibuja el Formato Visual."""
    pyautogui.click(form_coords)
    time.sleep(0.40)
    
    configurar_propiedades_form("menu 2", next_form_id, "pass_down")
    
    pyautogui.click(MAPA_UI["vista_form"]["sub_menus"]["lookup"]["1st_lookup"])
    time.sleep(0.14)
    
    if "scroll_tabla" in MAPA_UI["vista_form"]:
        pyautogui.moveTo(MAPA_UI["vista_form"]["scroll_tabla"]["origen"])
        pyautogui.dragTo(MAPA_UI["vista_form"]["scroll_tabla"]["destino"], duration=0.28, button='left')
        time.sleep(0.14)
        
    escribir_celda(0, "prompt", ">> L O G I N <<")
    escribir_celda(1, "nil", "")
    
    escribir_celda(2, "integer", "Contrasena: ", "5", "5", 1, prefijo_forzado="pw#", input_mark_char="*")
    escribir_celda(3, "lookup", "Operador: ", "0", "80", 2, prefijo_forzado="us#") 
    
    escribir_celda(4, "nil", "")
    escribir_celda(5, "prompt", "TIPO DE CONTEO:")
    escribir_celda(6, "fixed_data", tipo_conteo, prefijo_forzado="rk#")
    escribir_celda(7, "fixed_data", "1", prefijo_forzado="nc#")

def configurar_propiedades_form(esc_id, next_id, record_tipo):
    """Enruta la navegación usando atajos F y M para máxima velocidad."""
    props = MAPA_UI["vista_form"]["properties"]
    
    def aplicar_atajo(valor):
        if isinstance(valor, int):
            for _ in range(valor):
                pyautogui.press('f')
                time.sleep(0.03)
        elif isinstance(valor, str) and "menu" in valor.lower():
            num = int(re.search(r'\d+', valor).group())
            for _ in range(num):
                pyautogui.press('m')
                time.sleep(0.03)
        pyautogui.press('enter')
        time.sleep(0.04)

    pyautogui.click(props["esc"]["coords"]); time.sleep(0.04)
    aplicar_atajo(esc_id)
    
    pyautogui.click(props["next"]["coords"]); time.sleep(0.04)
    aplicar_atajo(next_id)
    
    pyautogui.click(props["record"]["coords"]); time.sleep(0.04)
    pyautogui.press('p'); time.sleep(0.04)
    
    if record_tipo == 'save':
        for _ in range(4):
            pyautogui.press('s')
            time.sleep(0.03)
    pyautogui.press('enter')
    time.sleep(0.04)

def inyectar_localizaciones_formato(route_dict, loc_items_list, tipo_conteo_texto):
    """Dibuja dinámicamente las pantallas de localización (1 sola o separadas)."""
    if route_dict.get('loc2') and len(loc_items_list) == 2:
        pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"][f"form_{route_dict['loc1']}"]); time.sleep(0.26)
        configurar_propiedades_form(route_dict['login'], route_dict['loc2'], "pass_down")
        
        if loc_items_list[0].get('es_catalogo'):
            pyautogui.click(MAPA_UI["vista_form"]["sub_menus"]["lookup"]["2nd_lookup"]); time.sleep(0.04)
            
        if "scroll_tabla" in MAPA_UI["vista_form"]:
            pyautogui.moveTo(MAPA_UI["vista_form"]["scroll_tabla"]["origen"])
            pyautogui.dragTo(MAPA_UI["vista_form"]["scroll_tabla"]["destino"], duration=0.28, button='left'); time.sleep(0.14)
            
        escribir_celda(0, "prompt", "LOCALIZACION 1/2")
        escribir_celda(1, "nil", "")
        item1 = loc_items_list[0]
        nf1 = 1 if item1.get('es_catalogo') else 0
        escribir_celda(2, item1['tipo'], f"{item1['nombre_pantalla']}: ", item1['longitud'].split('-')[0], item1['longitud'].split('-')[1], nf1, input_mark_char="_")
        escribir_celda(3, "nil", "")
        escribir_celda(4, "nil", "")
        escribir_celda(5, "nil", "")
        escribir_celda(6, "prompt", "TIPO DE CONTEO:")
        escribir_celda(7, "prompt", tipo_conteo_texto)
        
        pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"][f"form_{route_dict['loc2']}"]); time.sleep(0.26)
        configurar_propiedades_form(route_dict['loc1'], route_dict['datos'][0], "pass_down")
        
        if loc_items_list[1].get('es_catalogo'):
            pyautogui.click(MAPA_UI["vista_form"]["sub_menus"]["lookup"]["2nd_lookup"]); time.sleep(0.04)
            
        if "scroll_tabla" in MAPA_UI["vista_form"]:
            pyautogui.moveTo(MAPA_UI["vista_form"]["scroll_tabla"]["origen"])
            pyautogui.dragTo(MAPA_UI["vista_form"]["scroll_tabla"]["destino"], duration=0.28, button='left'); time.sleep(0.14)
            
        escribir_celda(0, "prompt", "LOCALIZACION 2/2")
        escribir_celda(1, "nil", "")
        item2 = loc_items_list[1]
        nf2 = 1 if item2.get('es_catalogo') else 0
        escribir_celda(2, item2['tipo'], f"{item2['nombre_pantalla']}: ", item2['longitud'].split('-')[0], item2['longitud'].split('-')[1], nf2, input_mark_char="_")
        escribir_celda(3, "nil", "")
        escribir_celda(4, "nil", "")
        escribir_celda(5, "nil", "")
        escribir_celda(6, "prompt", "TIPO DE CONTEO:")
        escribir_celda(7, "prompt", tipo_conteo_texto)
        return route_dict['loc2']
        
    else:
        pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"][f"form_{route_dict['loc1']}"]); time.sleep(0.26)
        configurar_propiedades_form(route_dict['login'], route_dict['datos'][0], "pass_down")
        
        if any(item.get('es_catalogo') for item in loc_items_list):
            pyautogui.click(MAPA_UI["vista_form"]["sub_menus"]["lookup"]["2nd_lookup"]); time.sleep(0.04)
            
        if "scroll_tabla" in MAPA_UI["vista_form"]:
            pyautogui.moveTo(MAPA_UI["vista_form"]["scroll_tabla"]["origen"])
            pyautogui.dragTo(MAPA_UI["vista_form"]["scroll_tabla"]["destino"], duration=0.28, button='left'); time.sleep(0.14)
            
        escribir_celda(0, "prompt", "LOCALIZACION 1/1")
        escribir_celda(1, "nil", "")
        
        if len(loc_items_list) == 1:
            item = loc_items_list[0]
            nf = 1 if item.get('es_catalogo') else 0
            escribir_celda(2, item['tipo'], f"{item['nombre_pantalla']}: ", item['longitud'].split('-')[0], item['longitud'].split('-')[1], nf, input_mark_char="_")
            escribir_celda(3, "nil", "")
            escribir_celda(4, "nil", "")
            escribir_celda(5, "nil", "")
        elif len(loc_items_list) == 2:
            item1 = loc_items_list[0]
            item2 = loc_items_list[1]
            nf1 = 1 if item1.get('es_catalogo') else 0
            nf2 = 1 if item2.get('es_catalogo') else 0
            escribir_celda(2, item1['tipo'], f"{item1['nombre_pantalla']}: ", item1['longitud'].split('-')[0], item1['longitud'].split('-')[1], nf1, input_mark_char="_")
            escribir_celda(3, "nil", "")
            escribir_celda(4, item2['tipo'], f"{item2['nombre_pantalla']}: ", item2['longitud'].split('-')[0], item2['longitud'].split('-')[1], nf2, input_mark_char="_")
            escribir_celda(5, "nil", "")
            
        escribir_celda(6, "prompt", "TIPO DE CONTEO:")
        escribir_celda(7, "prompt", tipo_conteo_texto)
        return route_dict['loc1']

def abrir_programa_y_plantilla(modelo):
    """Abre el acceso directo del modelo y carga la plantilla .AGX desde File -> Open."""
    base_path = r"C:\Users\dell\Documents\Bot AGX\AGX Bot"
    
    if modelo == "8200":
        lnk_path = os.path.join(base_path, "8200 ForgeAG.exe.lnk")
        plantilla_path = os.path.join(base_path, "8200 AGX PLANTILLA.AGX")
    else:
        lnk_path = os.path.join(base_path, "8000 ForgeAG.exe.lnk")
        plantilla_path = os.path.join(base_path, "8000 AGX PLANTILLA.AGX")

    print(f"➤ Abriendo software ForgeAG ({modelo})...")
    os.startfile(lnk_path)
    time.sleep(1.5) 

    print(f"➤ Cargando plantilla: {os.path.basename(plantilla_path)}")
    pyautogui.click(MAPA_UI["barra_superior"]["file"])
    time.sleep(0.24)
    pyautogui.click(MAPA_UI["barra_superior"]["open"])
    time.sleep(0.50) 
    
    pyautogui.write(plantilla_path)
    time.sleep(0.26)
    pyautogui.press('enter')
    time.sleep(1.00) 

def guardar_trabajo_final(modelo, cliente, tipo_agx):
    """Guarda el archivo AGX con el formato [Cliente] [Tipo] [Modelo] [Fecha] v[Version].AGX"""
    base_path = r"C:\Users\dell\Documents\Bot AGX\AGX Bot"
    folder_name = f"Modelo {modelo}"
    save_dir = os.path.join(base_path, folder_name)
    
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    # Determinar si es Abierto o Cerrado para el nombre
    tipo_limpio = limpiar_texto(tipo_agx)
    tipo_nombre = "Abierto" if "abierto" in tipo_limpio or "forzado" in tipo_limpio else "Cerrado"
    
    fecha_hoy = datetime.now().strftime("%d-%m-%Y")
    version = 1
    cliente_limpio = re.sub(r'[\\/*?:"<>|]', "", cliente).strip()
    
    while True:
        nombre_archivo = f"{cliente_limpio} {tipo_nombre} {modelo} {fecha_hoy} v{version}.AGX"
        full_save_path = os.path.join(save_dir, nombre_archivo)
        if not os.path.exists(full_save_path):
            break
        version += 1

    print(f"➤ Guardando trabajo final como: {nombre_archivo} en {folder_name}...")
    
    pyautogui.click(MAPA_UI["barra_superior"]["file"])
    time.sleep(0.24)
    pyautogui.click(MAPA_UI["barra_superior"]["save_as"])
    time.sleep(0.50) 
    
    pyautogui.write(full_save_path)
    time.sleep(0.26)
    pyautogui.press('enter')
    time.sleep(0.50)
    return full_save_path

def enviar_por_whatsapp(file_path, telefono, es_segundo_envio=False):
    """Copia nativamente el archivo físico al portapapeles mediante PowerShell y lo envía por WhatsApp Desktop."""
    if not telefono or len(telefono) < 8:
        print("⚠️ No se proporcionó un número de teléfono válido para el envío por WhatsApp.")
        return

    print(f"➤ Preparando archivo para WhatsApp: {os.path.basename(file_path)}")
    import subprocess
    
    # Comando nativo de PowerShell para meter un objeto ARCHIVO FÍSICO en el portapapeles de Windows (idéntico a Ctrl+C en el explorador)
    ps_cmd = f"Set-Clipboard -Path '{file_path}'"
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.15)
    
    print(f"➤ Abriendo chat de WhatsApp para el número: {telefono}...")
    # Protocolo nativo de Windows URI que enfoca o abre WhatsApp Desktop en un chat específico
    os.startfile(f"whatsapp://send?phone={telefono}")
    
    # Tiempo de carga: el primer envío necesita más tiempo por si la app está cerrada; el segundo es casi instantáneo
    tiempo_espera = 1.50 if es_segundo_envio else 3.50
    time.sleep(tiempo_espera)
    
    print("➤ Pegando y enviando archivo...")
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.25)
    pyautogui.press('enter')
    time.sleep(0.50)

def ejecutar_bot(datos):
    """Ejecuta el bot RPA utilizando los datos interpretados de Excel."""
    es_pieza = datos['es_pieza']
    es_volumen = datos['es_volumen']
    cliente = datos['cliente']
    tipo_agx = datos['tipo_agx']
    telefono = datos.get('telefono', '')
    plan_vuelo = datos['plan_vuelo']
    loc_items = datos['loc_items']
    info_cantidad = datos['info_cantidad']
    multiplo_catalogo = datos['multiplo_catalogo']
    dict_captura = datos['dict_captura']
    listado_vars = list(dict_captura.values())
    
    es_8200 = "scroll_tabla" in MAPA_UI["vista_form"]
    modelo_str = "8200" if es_8200 else "8000"

    print(f"\n🤖 Iniciando Bot AGX ({modelo_str}). ¡Suelta el mouse y el teclado!...")
    abrir_programa_y_plantilla(modelo_str)

    try:
        if es_8200:
            print("\n➤ Entorno 8200: Desplegando Menu, Lookup y Form simultáneamente...")
            pyautogui.click(MAPA_UI["directorio_izquierdo"]["menu"]); time.sleep(0.24)
            pyautogui.click(MAPA_UI["directorio_izquierdo"]["lookup"]); time.sleep(0.24)
            pyautogui.click(MAPA_UI["directorio_izquierdo"]["form"]); time.sleep(0.24)
        else:
            print("\n➤ Entorno 8000: Desplegando solo Menu...")
            pyautogui.click(MAPA_UI["directorio_izquierdo"]["menu"]); time.sleep(0.26)

        pyautogui.click(MAPA_UI["vista_menu"]["menu_1"]); time.sleep(0.40)
        
        lineas_cliente = textwrap.wrap(cliente, width=16, break_long_words=True)
        coords_items = [MAPA_UI["vista_menu"]["items"]["item_5"]["coords"], MAPA_UI["vista_menu"]["items"]["item_6"]["coords"], MAPA_UI["vista_menu"]["items"]["item_7"]["coords"]]
        dicc_nexts = [MAPA_UI["vista_menu"]["next_dropdowns"]["next_5"], MAPA_UI["vista_menu"]["next_dropdowns"]["next_6"], MAPA_UI["vista_menu"]["next_dropdowns"]["next_7"]]
        
        for i in range(min(len(lineas_cliente), 3)):
            pyautogui.click(coords_items[i]); time.sleep(0.03)
            pyautogui.write(lineas_cliente[i], interval=0.03)
            pyautogui.click(dicc_nexts[i]["coords"]); time.sleep(0.14)
            pyautogui.press('m'); time.sleep(0.03)
            pyautogui.press('m'); time.sleep(0.03)
            pyautogui.press('enter'); time.sleep(0.03)

        print("➤ Configurando Menu 2 (Tipos de Conteo)...")
        pyautogui.click(MAPA_UI["vista_menu"]["menu_2"])
        time.sleep(0.40) 

        coords_item1 = MAPA_UI["vista_menu"]["items"]["item_1"]["coords"]
        coords_item2 = MAPA_UI["vista_menu"]["items"]["item_2"]["coords"]
        next_1 = MAPA_UI["vista_menu"]["next_dropdowns"]["next_1"]["coords"]
        next_2 = MAPA_UI["vista_menu"]["next_dropdowns"]["next_2"]["coords"]

        def seleccionar_form_dropdown(coordenada_next, num_form):
            pyautogui.click(coordenada_next)
            time.sleep(0.04)
            for _ in range(num_form):
                pyautogui.press('f')
                time.sleep(0.03)
            pyautogui.press('enter')
            time.sleep(0.04)

        if es_pieza and es_volumen:
            pyautogui.click(coords_item1); time.sleep(0.03)
            pyautogui.write("1. PIEZA X PIEZA", interval=0.02)
            seleccionar_form_dropdown(next_1, plan_vuelo['pieza']['login'])
            pyautogui.click(coords_item2); time.sleep(0.03)
            pyautogui.write("2. VOLUMEN", interval=0.02)
            seleccionar_form_dropdown(next_2, plan_vuelo['volumen']['login'])
        elif es_pieza:
            pyautogui.click(coords_item1); time.sleep(0.03)
            pyautogui.write("1. PIEZA X PIEZA", interval=0.02)
            seleccionar_form_dropdown(next_1, plan_vuelo['pieza']['login'])
            pyautogui.click(coords_item2); time.sleep(0.03)
            pyautogui.press('delete'); pyautogui.press('enter')
        elif es_volumen:
            pyautogui.click(coords_item1); time.sleep(0.03)
            pyautogui.write("1. VOLUMEN", interval=0.02)
            seleccionar_form_dropdown(next_1, plan_vuelo['volumen']['login'])
            pyautogui.click(coords_item2); time.sleep(0.03)
            pyautogui.press('delete'); pyautogui.press('enter')

        if not es_8200:
            pyautogui.click(MAPA_UI["directorio_izquierdo"]["menu"]); time.sleep(0.26)
            pyautogui.click(MAPA_UI["directorio_izquierdo"]["lookup"]); time.sleep(0.26)
        
        pyautogui.click(MAPA_UI["vista_lookup"]["archivos"]["1st_lookup"]); time.sleep(0.26)
        pyautogui.click(MAPA_UI["vista_lookup"]["configuracion"]["max_length_1"]["coords"]); pyautogui.write('10', interval=0.02)
        pyautogui.click(MAPA_UI["vista_lookup"]["configuracion"]["max_length_2"]["coords"]); pyautogui.write('10', interval=0.02)
        
        pyautogui.click(MAPA_UI["vista_lookup"]["archivos"]["2nd_lookup"]); time.sleep(0.26)
        pyautogui.click(MAPA_UI["vista_lookup"]["configuracion"]["max_length_1"]["coords"]); pyautogui.write(str(multiplo_catalogo), interval=0.02)

        # LÓGICA DE AGX ABIERTO/CERRADO/AMBOS
        tipo_agx_limpio = limpiar_texto(tipo_agx)
        if "ambos" in tipo_agx_limpio:
            modo_ejecucion = "ambos"
        elif "abierto" in tipo_agx_limpio or "forzado" in tipo_agx_limpio:
            modo_ejecucion = "abierto"
        else:
            modo_ejecucion = "cerrado"

        if modo_ejecucion in ["abierto", "ambos"]:
            print(f"➤ Configurando 2nd Lookup: Abierto (Show warning & insert) {'[Modo Dual Activo]' if modo_ejecucion == 'ambos' else ''}")
            pyautogui.click(MAPA_UI["vista_lookup"]["action_no_match"]["show_warning_insert"]); time.sleep(0.04)
        else:
            print("➤ Configurando 2nd Lookup: Cerrado (Show warning)")
            pyautogui.click(MAPA_UI["vista_lookup"]["action_no_match"]["show_warning"]); time.sleep(0.04)

        if not es_8200:
            pyautogui.click(MAPA_UI["directorio_izquierdo"]["form"]); time.sleep(0.26)
            
        if es_pieza:
            p_route = plan_vuelo['pieza']
            print(f"\n➤ Construyendo Interfaz Gráfica de Piezas (Inicia Form {p_route['login']})...")
            configurar_1st_lookup(MAPA_UI["vista_form"]["seleccion_forms"][f"form_{p_route['login']}"], "PZ X PZ", p_route['loc1'])
            esc_retorno_datos = inyectar_localizaciones_formato(p_route, loc_items, "Pieza x Pieza")
            total_pags_p = len(p_route['datos'])
            p_idx_global = 0
            for idx, f_num in enumerate(p_route['datos']):
                pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"][f"form_{f_num}"]); time.sleep(0.26)
                es_ultima = (idx == total_pags_p - 1)
                capacidad = 5 if es_ultima else 6
                rebanada = listado_vars[p_idx_global : p_idx_global + capacidad]
                p_esc = esc_retorno_datos if idx == 0 else p_route['datos'][idx - 1]
                p_next = p_route['datos'][0] if es_ultima else p_route['datos'][idx + 1] 
                p_record = "save" if es_ultima else "pass_down"
                configurar_propiedades_form(p_esc, p_next, p_record)
                if any(v.get('es_catalogo') for v in rebanada):
                    pyautogui.click(MAPA_UI["vista_form"]["sub_menus"]["lookup"]["2nd_lookup"]); time.sleep(0.04)
                if es_ultima:
                    pyautogui.click(MAPA_UI["vista_form"]["sub_menus"]["date_time_stamp"]["append_end"]); time.sleep(0.04)
                if "scroll_tabla" in MAPA_UI["vista_form"]:
                    pyautogui.moveTo(MAPA_UI["vista_form"]["scroll_tabla"]["origen"])
                    pyautogui.dragTo(MAPA_UI["vista_form"]["scroll_tabla"]["destino"], duration=0.28, button='left'); time.sleep(0.14)
                escribir_celda(0, "prompt", f"DATOS PZxPZ {idx+1}/{total_pags_p}")
                p_idx_global += len(rebanada) 
                for r_idx, v_info in enumerate(rebanada):
                    num_field = 1 if v_info.get('es_catalogo') else 0
                    escribir_celda(r_idx + 1, v_info['tipo'], f"{v_info['nombre_pantalla']}: ", v_info['longitud'].split('-')[0], v_info['longitud'].split('-')[1], num_field, input_mark_char="_")
                if es_ultima:
                    for v_blank in range(len(rebanada) + 1, 6): escribir_celda(v_blank, "nil", "")
                    escribir_celda(6, "pause", "[ENTER] O [ESC]")
                    escribir_celda(7, "fixed_data", "1", prefijo_forzado="cn#")
                else:
                    for v_blank in range(len(rebanada) + 1, 7): escribir_celda(v_blank, "nil", "")
                    escribir_celda(7, "pause", "[SIGUIENTE] ->")

        if es_volumen:
            v_route = plan_vuelo['volumen']
            print(f"\n➤ Construyendo Interfaz Gráfica de Volumen (Inicia Form {v_route['login']})...")
            configurar_1st_lookup(MAPA_UI["vista_form"]["seleccion_forms"][f"form_{v_route['login']}"], "VOL", v_route['loc1'])
            esc_retorno_datos_v = inyectar_localizaciones_formato(v_route, loc_items, "Conteo x Volumen")
            total_pags_v = len(v_route['datos'])
            v_idx_global = 0
            for idx, f_num in enumerate(v_route['datos']):
                pyautogui.click(MAPA_UI["vista_form"]["seleccion_forms"][f"form_{f_num}"]); time.sleep(0.26)
                es_ultima = (idx == total_pags_v - 1)
                capacidad = 5 if es_ultima else 6
                rebanada = listado_vars[v_idx_global : v_idx_global + capacidad]
                v_esc = esc_retorno_datos_v if idx == 0 else v_route['datos'][idx - 1]
                v_next = v_route['datos'][0] if es_ultima else v_route['datos'][idx + 1] 
                v_record = "save" if es_ultima else "pass_down"
                configurar_propiedades_form(v_esc, v_next, v_record)
                if any(v.get('es_catalogo') for v in rebanada):
                    pyautogui.click(MAPA_UI["vista_form"]["sub_menus"]["lookup"]["2nd_lookup"]); time.sleep(0.04)
                if es_ultima:
                    pyautogui.click(MAPA_UI["vista_form"]["sub_menus"]["date_time_stamp"]["append_end"]); time.sleep(0.04)
                if "scroll_tabla" in MAPA_UI["vista_form"]:
                    pyautogui.moveTo(MAPA_UI["vista_form"]["scroll_tabla"]["origen"])
                    pyautogui.dragTo(MAPA_UI["vista_form"]["scroll_tabla"]["destino"], duration=0.28, button='left'); time.sleep(0.14)
                escribir_celda(0, "prompt", f"CONTEO X VOL {idx+1}/{total_pags_v}")
                v_idx_global += len(rebanada) 
                for r_idx, v_info in enumerate(rebanada):
                    num_field = 1 if v_info.get('es_catalogo') else 0
                    escribir_celda(r_idx + 1, v_info['tipo'], f"{v_info['nombre_pantalla']}: ", v_info['longitud'].split('-')[0], v_info['longitud'].split('-')[1], num_field, input_mark_char="_")
                if es_ultima:
                    for v_blank in range(len(rebanada) + 1, 6): escribir_celda(v_blank, "nil", "")
                    c_min, c_max = info_cantidad['longitud'].split('-')
                    escribir_celda(6, info_cantidad['tipo'], f"{info_cantidad['nombre_pantalla']}: ", c_min, c_max, input_mark_char="_")
                    escribir_celda(7, "pause", "[ENTER] O [ESC]")
                else:
                    for v_blank in range(len(rebanada) + 1, 7): escribir_celda(v_blank, "nil", "")
                    escribir_celda(7, "pause", "[SIGUIENTE] ->")

        # [AL FINAL DE TODA LA INYECCIÓN]
        print("\n➤ Finalizando inyección de datos...")
        
        if modo_ejecucion == "ambos":
            path_abierto = guardar_trabajo_final(modelo_str, cliente, "Abierto")
            enviar_por_whatsapp(path_abierto, telefono)
            
            print("\n➤ [Modo Ambos] Regresando a configuración de Lookup para generar versión Cerrada...")
            pyautogui.click(MAPA_UI["vista_lookup"]["archivos"]["2nd_lookup"]); time.sleep(0.26)
            
            print("➤ Configurando 2nd Lookup: Cerrado (Show warning)")
            pyautogui.click(MAPA_UI["vista_lookup"]["action_no_match"]["show_warning"]); time.sleep(0.04)
            
            path_cerrado = guardar_trabajo_final(modelo_str, cliente, "Cerrado")
            enviar_por_whatsapp(path_cerrado, telefono, es_segundo_envio=True)
        elif modo_ejecucion == "abierto":
            path_gen = guardar_trabajo_final(modelo_str, cliente, "Abierto")
            enviar_por_whatsapp(path_gen, telefono)
        else:
            path_gen = guardar_trabajo_final(modelo_str, cliente, "Cerrado")
            enviar_por_whatsapp(path_gen, telefono)

        print("\n✅ ¡SISTEMA AGX PROCEDURAL GENERADO, GUARDADO Y ENVIADO PERFECTAMENTE!")

    except Exception as e:
        print(f"\n❌ El bot dinámico falló en ejecución: {e}")
