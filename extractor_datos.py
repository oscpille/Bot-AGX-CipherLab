import pandas as pd
import re
import sys
import unicodedata
from config import TRADUCCION_TIPOS, MAPA_UI, DICCIONARIO_NOMBRES_CORTOS

def limpiar_texto(texto):
    """Quita acentos y pasa a minúsculas para comparaciones exactas."""
    texto_sin_acentos = unicodedata.normalize('NFD', str(texto)).encode('ascii', 'ignore').decode('utf-8')
    return texto_sin_acentos.lower().strip()

def asignar_piscina_forms(es_pieza, es_volumen, vars_pieza, vars_volumen):
    """Calcula matemáticamente y distribuye dinámicamente los 10 Forms agrupando por base de datos."""
    forms_disponibles = list(range(1, 11))
    rutas = {}
    
    def calcular_paginas_estructuradas(variables):
        paginas = []
        if not variables: return paginas
        
        current_lookup = 'no_lookup'
        current_vars = []
        
        for v in variables:
            if v.get('is_page_break'):
                # Forzar salto de página explícito
                if current_vars:
                    paginas.append({'lookup_file': current_lookup, 'vars': current_vars})
                    current_vars = []
                    current_lookup = 'no_lookup'
                continue

            l_file = v.get('lookup_file', 'no_lookup')
            
            # Si hay un conflicto de base de datos (ambas distintas de 'no_lookup' y diferentes entre sí)
            if l_file != 'no_lookup' and current_lookup != 'no_lookup' and l_file != current_lookup:
                paginas.append({'lookup_file': current_lookup, 'vars': current_vars})
                current_lookup = l_file
                current_vars = []
                
            # Si llegamos al límite de capacidad de la página (6)
            if len(current_vars) == 6:
                paginas.append({'lookup_file': current_lookup, 'vars': current_vars})
                # El nuevo grupo hereda el lookup de la variable si lo tiene, si no, arranca neutral
                current_lookup = l_file if l_file != 'no_lookup' else 'no_lookup'
                current_vars = []
                
            # Si la página era neutral y llega una variable con lookup, la página adopta ese lookup
            if current_lookup == 'no_lookup' and l_file != 'no_lookup':
                current_lookup = l_file
                
            current_vars.append(v)
            
        if current_vars:
            paginas.append({'lookup_file': current_lookup, 'vars': current_vars})
            
        # La última página de todas solo soporta 5 variables (porque lleva el [ENTER] O [ESC] y el [1] oculto)
        if paginas and len(paginas[-1]['vars']) == 6:
            overflow_var = paginas[-1]['vars'].pop()
            # La nueva página hereda el lookup de la página anterior, lo cual es correcto
            paginas.append({'lookup_file': paginas[-1]['lookup_file'], 'vars': [overflow_var]})
            
        return paginas
    
    try:
        paginas_p = calcular_paginas_estructuradas(vars_pieza)
        paginas_v = calcular_paginas_estructuradas(vars_volumen)
        
        if es_pieza:
            rutas['pieza'] = {
                'login': forms_disponibles.pop(0),
                'datos': []
            }
            for p in paginas_p:
                rutas['pieza']['datos'].append({
                    'f_num': forms_disponibles.pop(0),
                    'lookup_file': p['lookup_file'],
                    'vars': list(p['vars'])
                })
                
        if es_volumen:
            rutas['volumen'] = {
                'login': forms_disponibles.pop(0),
                'datos': []
            }
            for p in paginas_v:
                rutas['volumen']['datos'].append({
                    'f_num': forms_disponibles.pop(0),
                    'lookup_file': p['lookup_file'],
                    'vars': list(p['vars'])
                })
                
    except IndexError:
        print("\n❌ ERROR CRÍTICO: ¡La solicitud desborda la capacidad de 10 Forms de Forge AG!")
        sys.exit()
        
    return rutas

def procesar_solicitud(solicitud):
    """Ejecuta toda la lógica de analizador léxico y pre-vuelo recibiendo el JSON directo."""
    try:
        from config import MAPA_UI
        import datetime
        
        id_solicitud = solicitud.get('id_solicitud', 'desconocido')
        chat_id = solicitud.get('chat_id', '')
        mention_id = solicitud.get('mention_id', None)
        
        try:
            fecha_str = datetime.datetime.fromtimestamp(int(id_solicitud) / 1000.0).strftime('%d/%m/%Y|%H:%M:%S')
        except ValueError:
            fecha_str = "Fecha Desconocida"
            
        print(f"➤ Analizando datos de la solicitud recibida el {fecha_str}...")
        modelo_solicitado = str(solicitud.get('¿QUÉ MODELO DE AGX NECESITAS?', '')).strip()
        modelo_exacto = "8000"
        
        if "8200" in modelo_solicitado:
            print("➤ Configuración Detectada: MODELO 8200")
            modelo_exacto = "8200"
            import mapeo_8200
            MAPA_UI.update(mapeo_8200.MAPA_UI)
        elif "8000v2" in modelo_solicitado.lower():
            print("➤ Configuración Detectada: MODELO 8000v2")
            modelo_exacto = "8000v2"
            import mapeo_8200
            MAPA_UI.update(mapeo_8200.MAPA_UI)
        else:
            print("➤ Configuración Detectada: MODELO 8000")
            modelo_exacto = "8000"
            import mapeo_8000
            MAPA_UI.update(mapeo_8000.MAPA_UI)
            
        cliente = str(solicitud['INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:']).strip().upper()
        flujo_crudo = limpiar_texto(solicitud['FLUJO OPERATIVO:'])
        es_pieza = "pieza" in flujo_crudo or "ambos" in flujo_crudo
        es_volumen = "volumen" in flujo_crudo or "ambos" in flujo_crudo
        
        todas_las_vars_dict = {}
        print("➤ Ejecutando Analizador Léxico (Regex)...")
        
        page_break_count = 0
        for linea in str(solicitud['DATOS REQUERIDOS']).split('\n'):
            linea = linea.strip()
            if not linea: 
                todas_las_vars_dict[f'__page_break_{page_break_count}__'] = {'is_page_break': True}
                page_break_count += 1
                continue
            prefijo_extraido = None
            import re
            match_prefijo = re.match(r"^<([^>]+)>\s*", linea)
            if match_prefijo:
                prefijo_extraido = match_prefijo.group(1).strip()
                linea = linea[match_prefijo.end():]

            
            linea_limpia = linea.lower().replace(',', '').replace('.', '').replace(';', '')
            nombre_original = re.sub(r'(\d+)\s*(?:-|a|al|maximo|máximo)\s*(\d+)', '', linea).strip()
            nombre_original = re.sub(r'(?i)\s+(con|de|mínimo|minimo|en|a|al|hasta)$', '', nombre_original).strip()
            nombre_original = re.sub(r'(?i)(?:\s+(?:catalogo|catálogo|lookup|prompt|mensaje|bucle|loop|teclado|keypad|lector|reader|\d+))+$', '', nombre_original).strip()
            nombre_original = re.sub(r'[;,.\-:]+$', '', nombre_original).strip()
            
            nombre_original_lower = limpiar_texto(nombre_original)
            for largo, corto in DICCIONARIO_NOMBRES_CORTOS.items():
                if largo in nombre_original_lower:
                    nombre_original = corto
                    break
            
            if "ean" in nombre_original_lower:
                nombre_original = "EAN"
                
            if nombre_original_lower in ['catalogo', 'lookup', 'prompt', 'mensaje', 'bucle', 'loop', 'teclado', 'keypad', 'lector', 'reader']:
                nombre_original = ""
                
            nombre_logico = limpiar_texto(nombre_original)
            
            longitud_base = "1-10" if "cantidad" in nombre_logico else "3-15"
            min_max_final = longitud_base
            tiene_longitud = False
            
            rango_match = re.search(r'(\d+)\s*(?:-|a|al|maximo|máximo)\s*(\d+)', linea_limpia)
            if rango_match:
                min_max_final = f"{rango_match.group(1)}-{rango_match.group(2)}"
                tiene_longitud = True
            else:
                num_match = re.search(r'\b(\d+)\b', linea_limpia)
                if num_match: 
                    min_max_final = f"{num_match.group(1)}-{num_match.group(1)}"
                    tiene_longitud = True
                
            linea_limpia_sin_acentos = limpiar_texto(linea)
            
            linea_sin_long = re.sub(r'(\d+)\s*(?:-|a|al|maximo|máximo)\s*(\d+)', '', linea_limpia_sin_acentos)
            # Removemos la línea que borraba todos los números aislados porque destruía los IDs de catálogo (ej. 'catalogo 2')
            match_cat = re.search(r'\b(catalogo|lookup)\b\s*(\S*)', linea_sin_long)
            
            if match_cat:
                es_catalogo = True
                id_catalogo = match_cat.group(2).strip()
                id_catalogo = re.sub(r'\b(bucle|loop|teclado|keypad|lector|reader|prompt|mensaje)\b', '', id_catalogo).strip()
            else:
                es_catalogo = False
                id_catalogo = ""
                
            es_prompt = bool(re.search(r'\b(prompt|mensaje)\b', linea_limpia_sin_acentos))
            es_lookup_type = bool(re.search(r'\b(lookup)\b', linea_limpia_sin_acentos))
            
            if es_prompt:
                tipo_bruto = "prompt"
                min_max_final = "-"
                es_catalogo = False
            elif es_lookup_type:
                tipo_bruto = "lookup"
                es_catalogo = True
            elif not tiene_longitud:
                tipo_bruto = "entero" if "marbete" in nombre_logico else "texto"
            else:
                tipo_bruto = "entero" if "marbete" in nombre_logico else "texto"
                    
            es_bucle = bool(re.search(r'\b(bucle|loop)\b', linea_limpia_sin_acentos))
            
            input_type = "both"
            if bool(re.search(r'\b(teclado|keypad)\b', linea_limpia_sin_acentos)):
                input_type = "keypad"
            elif bool(re.search(r'\b(lector|reader)\b', linea_limpia_sin_acentos)):
                input_type = "reader"
            
            datos = {
                'nombre_pantalla': nombre_original, 
                'longitud': min_max_final, 
                'tipo': TRADUCCION_TIPOS.get(limpiar_texto(tipo_bruto), "text"),
                'es_catalogo': es_catalogo,
                'id_catalogo': id_catalogo,
                'es_bucle': es_bucle,
            'input_type': input_type,
            'prefijo_extraido': prefijo_extraido
            }
            
            todas_las_vars_dict[nombre_logico] = datos

        info_cantidad = {'tipo': 'text', 'nombre_pantalla': 'Cantidad', 'longitud': '1-10', 'prefijo_extraido': 'cn#'}
        claves_a_borrar = []
        
        for k, v in todas_las_vars_dict.items():
            if "cantidad" in k: 
                info_cantidad = v  
            info_cantidad['nombre_pantalla'] = 'Cantidad'
            info_cantidad['prefijo_extraido'] = 'cn#'
                claves_a_borrar.append(k)
                
        for k in claves_a_borrar:
            del todas_las_vars_dict[k]

        todas_las_vars = list(todas_las_vars_dict.values())
        listado_vars = todas_las_vars
        
        agrupacion_catalogos = {}
        ultimo_id_cat = ""
        for v in todas_las_vars:
            if v.get('is_page_break'): continue
            if v.get('es_catalogo'):
                id_cat = v.get('id_catalogo', '').strip()
                if not id_cat and ultimo_id_cat:
                    id_cat = ultimo_id_cat
                    v['id_catalogo'] = id_cat
                ultimo_id_cat = id_cat
                
                if id_cat not in agrupacion_catalogos:
                    agrupacion_catalogos[id_cat] = []
                max_str = v['longitud'].split('-')[1]
                if max_str:
                    agrupacion_catalogos[id_cat].append((int(max_str) // 5) * 5 + 5)
                else:
                    agrupacion_catalogos[id_cat].append(25)
                
        nombres_unicos_catalogos = list(agrupacion_catalogos.keys())[:2]
        multiplos_por_lookup = {}
        if len(nombres_unicos_catalogos) > 0:
            multiplos_por_lookup["2nd_lookup"] = agrupacion_catalogos[nombres_unicos_catalogos[0]]
        if len(nombres_unicos_catalogos) > 1:
            multiplos_por_lookup["3rd_lookup"] = agrupacion_catalogos[nombres_unicos_catalogos[1]]
            
        for v in todas_las_vars:
            if v.get('es_catalogo'):
                id_cat = v.get('id_catalogo', '').strip()
                if len(nombres_unicos_catalogos) > 0 and id_cat == nombres_unicos_catalogos[0]:
                    v['lookup_file'] = '2nd_lookup'
                elif len(nombres_unicos_catalogos) > 1 and id_cat == nombres_unicos_catalogos[1]:
                    v['lookup_file'] = '3rd_lookup'
                else:
                    v['lookup_file'] = '3rd_lookup'
                    
        # Filter volumen
        def es_prefijo_con(nombre):
            nm = limpiar_texto(nombre)
            return "cantidad" in nm or "volumen" in nm or "conteo" in nm
            
        vars_volumen = [v for v in listado_vars if v.get('is_page_break') or not es_prefijo_con(v.get('nombre_pantalla', ''))]

        plan_vuelo = asignar_piscina_forms(es_pieza, es_volumen, listado_vars, vars_volumen)

        # =========================================================
        # CHECKLIST DE PRE-VUELO (CONFIRMACIÓN DE DATOS)
        # =========================================================
        tipo_agx = str(solicitud.get('¿DE QUÉ TIPO SERÁ?', 'No especificado')).strip()
        modelo_final = '8200' if '8200' in modelo_solicitado else '8000'
        
        tipo_agx_mostrar = "Abierto y Cerrado" if "ambos" in limpiar_texto(tipo_agx) else tipo_agx

        if es_pieza and es_volumen:
            txt_conteo = "Ambos (Pieza x Pieza y Volumen)"
        elif es_pieza:
            txt_conteo = "Pieza x Pieza"
        elif es_volumen:
            txt_conteo = "Volumen"
        else:
            txt_conteo = "No definido"

        print("\n" + "="*55)
        print("📋 RESUMEN DE LA SOLICITUD A INYECTAR")
        print("="*55)
        print(f"➤ Modelo de AGX  : {modelo_final}")
        print(f"➤ Tipo de AGX    : {tipo_agx_mostrar}") 
        print(f"➤ Inventario para: {cliente}")
        print(f"➤ Tipo de Conteo : {txt_conteo}")
        
        print("➤ Formato original recibido (Raw Text):")
        for linea_cruda in str(solicitud.get('POR ÚLTIMO, INGRESA QUÉ DATOS SON LOS QUE DESEAS EN TU AGX Y CUÁL ES SU LÍMITE DE CARACTERES:', '')).split('\n'):
            print(f"   {linea_cruda}")
        print("➤ Datos interpretados por el bot:")
        
        todas_las_variables = list(listado_vars)
        if es_volumen:
            todas_las_variables.append(info_cantidad)
            
        for var in todas_las_variables:
            if var is not None:
                if var.get('is_page_break'):
                    print("   [--- SALTO DE PANTALLA ---]")
                else:
                    if var.get('lookup_file') and var.get('lookup_file') != 'no_lookup':
                        l_file_str = "2nd Lookup File" if var['lookup_file'] == '2nd_lookup' else "3rd Lookup File"
                        indicativo_lookup = f" <- {l_file_str}"
                    else:
                        indicativo_lookup = ""
                    print(f"   • {var['nombre_pantalla']}: {var['longitud']}{indicativo_lookup}")
        
        print("="*55)

        return {
            'es_pieza': es_pieza,
            'es_volumen': es_volumen,
            'cliente': cliente,
            'tipo_agx': tipo_agx,
            'plan_vuelo': plan_vuelo,
            'info_cantidad': info_cantidad,
            'multiplos_por_lookup': multiplos_por_lookup,
            'dict_captura': {v.get('nombre_pantalla', f'var_{i}'): v for i, v in enumerate(listado_vars) if not v.get('is_page_break')},
            'id_solicitud': id_solicitud,
            'chat_id': chat_id,
            'mention_id': mention_id,
            'modelo_exacto': modelo_exacto
        }

    except Exception as e:
        print(f"❌ Error en la curación de datos: {e}")
        sys.exit()
