import pandas as pd
import re
import sys
import unicodedata
from config import RUTA_EXCEL, TRADUCCION_TIPOS, MAPA_UI

def limpiar_texto(texto):
    """Quita acentos y pasa a minúsculas para comparaciones exactas."""
    texto_sin_acentos = unicodedata.normalize('NFD', str(texto)).encode('ascii', 'ignore').decode('utf-8')
    return texto_sin_acentos.lower().strip()

def asignar_piscina_forms(es_pieza, es_volumen, vars_pieza, vars_volumen, dict_ubicacion, separar_ubicacion):
    """Calcula matemáticamente y distribuye dinámicamente los 10 Forms agrupando por base de datos."""
    forms_disponibles = list(range(1, 11))
    rutas = {}
    
    def calcular_paginas_estructuradas(variables):
        paginas = []
        if not variables: return paginas
        
        current_lookup = 'no_lookup'
        current_vars = []
        
        for v in variables:
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
                'loc1': forms_disponibles.pop(0),
                'loc2': forms_disponibles.pop(0) if (separar_ubicacion and len(dict_ubicacion) > 1) else None,
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
                'loc1': forms_disponibles.pop(0),
                'loc2': forms_disponibles.pop(0) if (separar_ubicacion and len(dict_ubicacion) > 1) else None,
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

def procesar_fila_excel():
    """Ejecuta toda la lógica de lectura, analizador léxico y pre-vuelo."""
    try:
        print("➤ Iniciando lectura ultrarrápida desde OneDrive (Calamine)...")
        df = pd.read_excel(RUTA_EXCEL, engine='calamine').dropna(how='all')
        
        df_pendientes = df[df['ESTATUS:'].astype(str).str.strip().str.upper() == 'PENDIENTE']
        
        if df_pendientes.empty:
            print("\n✅ Bandeja limpia: No hay solicitudes PENDIENTES por procesar. Cerrando...")
            sys.exit()
            
        solicitud = df_pendientes.iloc[0]
        indice_excel = solicitud.name + 2 
        print(f"➤ Atendiendo solicitud en la fila {indice_excel} de la cola de trabajo.")
        
        modelo_solicitado = str(solicitud['¿QUÉ MODELO DE AGX NECESITAS?']).strip()
        
        if "8200" in modelo_solicitado:
            print("➤ Configuración Detectada: MODELO 8200")
            import mapeo_8200
            MAPA_UI.update(mapeo_8200.MAPA_UI)
        else:
            print("➤ Configuración Detectada: MODELO 8000")
            import mapeo_8000
            MAPA_UI.update(mapeo_8000.MAPA_UI)
            
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
            
            nombre_original = re.sub(r'(?i)\s+(con|de|mínimo|minimo|en|a|al|hasta)$', '', match_nombre.group(1).strip()).strip()
            nombre_original = re.sub(r'[;,.\-:]+$', '', nombre_original).strip()
            
            if "fecha de caducidad" in nombre_original.lower():
                nombre_original = "Caducidad"
            elif "numero de caja" in limpiar_texto(nombre_original):
                nombre_original = "Caja"
            elif "ean" in limpiar_texto(nombre_original):
                nombre_original = "EAN" 
                
            nombre_logico = limpiar_texto(nombre_original)
            
            longitud_base = "1-10" if "cantidad" in nombre_logico else "3-15"
            min_max_final = longitud_base
            
            rango_match = re.search(r'(\d+)\s*(?:-|a|al|maximo|máximo)\s*(\d+)', linea_limpia)
            if rango_match:
                min_max_final = f"{rango_match.group(1)}-{rango_match.group(2)}"
            else:
                num_match = re.search(r'\b(\d+)\b', linea_limpia)
                if num_match: min_max_final = f"{num_match.group(1)}-{num_match.group(1)}"
                
            tipo_bruto = "texto" 
            
            for t in ["alfanumerico", "alfanum", "numérico", "numerico", "num", "entero", "decimal", "texto", "letras", "lookup"]:
                if t in linea_limpia: 
                    tipo_bruto = "texto" if t in ["alfanumerico", "alfanum"] else t
                    break
                    
            if "sku" in nombre_logico or "ubicacion" in nombre_logico:
                tipo_bruto = "texto" 
            elif "marbete" in nombre_logico:
                if "texto" not in linea_limpia and "letras" not in linea_limpia:
                    tipo_bruto = "entero"
            elif "cant" in nombre_logico:
                if "decim" in linea_limpia: 
                    tipo_bruto = "decimal"
                else:
                    tipo_bruto = "entero"
                    
            linea_limpia_sin_acentos = limpiar_texto(linea)
            match_cat = re.search(r'\b(catalogo|lookup|bd|base de datos)\b(.*)', linea_limpia_sin_acentos)
            if match_cat:
                es_catalogo = True
                id_catalogo = match_cat.group(2).strip()
            else:
                es_catalogo = False
                id_catalogo = ""
            
            if "marbete" not in nombre_logico and not es_catalogo:
                tipo_bruto = "texto"
            
            datos = {
                'nombre_pantalla': nombre_original, 
                'longitud': min_max_final, 
                'tipo': TRADUCCION_TIPOS.get(limpiar_texto(tipo_bruto), "alphameric"),
                'es_catalogo': es_catalogo,
                'id_catalogo': id_catalogo
            }
            
            if "marbete" in nombre_logico or "ubicacion" in nombre_logico:
                dict_ubicacion[nombre_logico] = datos
            else:
                dict_captura[nombre_logico] = datos

        prioridad_str = str(solicitud.get('¿QUÉ NIVEL DE PRIORIDAD DAREMOS?', '')).lower()
        es_primero_ubicacion = "primero registrar ubicacion" in limpiar_texto(prioridad_str) or "primero registrar ubicación" in prioridad_str
        regla_separar = "siguiente" in prioridad_str

        loc_items = []
        v_marbete = next((v for k, v in dict_ubicacion.items() if 'marbete' in k), None)
        v_ubicacion = next((v for k, v in dict_ubicacion.items() if 'ubicacion' in k), None)

        if v_marbete and v_ubicacion:
            loc_items = [v_ubicacion, v_marbete] if es_primero_ubicacion else [v_marbete, v_ubicacion]
        elif v_marbete:
            loc_items = [v_marbete]
        elif v_ubicacion:
            loc_items = [v_ubicacion]

        info_cantidad = {'tipo': 'integer', 'nombre_pantalla': 'Cantidad', 'longitud': '1-10'} 
        claves_a_borrar = []
        
        for k, v in dict_captura.items():
            if "cantidad" in k: 
                info_cantidad = v  
                info_cantidad['nombre_pantalla'] = 'Cantidad' 
                claves_a_borrar.append(k)
                
        for k in claves_a_borrar:
            del dict_captura[k]

        todas_las_vars = list(dict_ubicacion.values()) + list(dict_captura.values())
        listado_vars = list(dict_captura.values())
        
        agrupacion_catalogos = {}
        for v in todas_las_vars:
            if v.get('es_catalogo'):
                id_cat = v.get('id_catalogo', '').strip()
                if id_cat not in agrupacion_catalogos:
                    agrupacion_catalogos[id_cat] = []
                agrupacion_catalogos[id_cat].append(((int(v['longitud'].split('-')[1]) + 4) // 5) * 5)
                
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
        from config import DICCIONARIO_PREFIJOS
        def es_prefijo_con(nombre):
            nm = limpiar_texto(nombre)
            for c, p in DICCIONARIO_PREFIJOS.items():
                if re.search(rf'\b{c}\b', nm):
                    return p == "con"
            return False
            
        vars_volumen = [v for v in listado_vars if not es_prefijo_con(v['nombre_pantalla'])]

        plan_vuelo = asignar_piscina_forms(es_pieza, es_volumen, listado_vars, vars_volumen, dict_ubicacion, regla_separar)

        # =========================================================
        # CHECKLIST DE PRE-VUELO (CONFIRMACIÓN DE DATOS)
        # =========================================================
        solicitante = str(solicitud.get('NOMBRE DE QUIEN SOLICITA EL AGX', 'No especificado')).strip()
        tipo_agx = str(solicitud.get('¿DE QUÉ TIPO SERÁ?', 'No especificado')).strip()
        modelo_final = '8200' if '8200' in modelo_solicitado else '8000'
        
        tipo_agx_mostrar = "Abierto y Cerrado" if "ambos" in limpiar_texto(tipo_agx) else tipo_agx

        # Extracción y Limpieza del Teléfono para WhatsApp (Busca la llave dinámicamente para evitar problemas con espacios \xa0)
        telefono_crudo = ""
        for key in solicitud.keys():
            if "TELÉFONO" in str(key):
                telefono_crudo = str(solicitud.get(key, ''))
                break
                
        telefono_limpio = re.sub(r'\D', '', telefono_crudo) # Dejar solo números
        if len(telefono_limpio) == 10:
            telefono_final = f"(+52) {telefono_limpio[:2]}-{telefono_limpio[2:6]}-{telefono_limpio[6:]}"
        elif telefono_limpio.startswith('52') and len(telefono_limpio) == 12:
            num = telefono_limpio[2:]
            telefono_final = f"(+52) {num[:2]}-{num[2:6]}-{num[6:]}"
        elif telefono_limpio.startswith('+'):
            telefono_final = telefono_limpio
        else:
            telefono_final = telefono_limpio # Dejar como esté si es internacional o ya formateado

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
        print(f"➤ Pedido por     : {solicitante}")
        if telefono_final:
            print(f"➤ Enviar archivos al: {telefono_final}")
        print(f"➤ Inventario para: {cliente}")
        print(f"➤ Tipo de Conteo : {txt_conteo}")
        
        if len(loc_items) == 2:
            if not regla_separar:
                txt_loc = "c. Registrar ambos en la misma pantalla."
            elif es_primero_ubicacion:
                txt_loc = "b. Primero registrar Ubicación y en la pantalla siguiente Marbetes."
            else:
                txt_loc = "a. Primero registrar Marbete y en la pantalla siguiente Ubicación."
            print(f"➤ Prioridad elegida: {txt_loc}")
        elif len(loc_items) == 1:
            print(f"➤ Localizaciones : Solo {loc_items[0]['nombre_pantalla']}")
            
        print("➤ Datos interpretados por el bot:")
        
        todas_las_variables = loc_items + list(dict_captura.values())
        if es_volumen:
            todas_las_variables.append(info_cantidad)
            
        for var in todas_las_variables:
            if var is not None:
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
            'telefono': telefono_final,
            'plan_vuelo': plan_vuelo,
            'loc_items': loc_items,
            'info_cantidad': info_cantidad,
            'multiplos_por_lookup': multiplos_por_lookup,
            'dict_captura': dict_captura
        }

    except Exception as e:
        print(f"❌ Error en la curación de datos: {e}")
        sys.exit()