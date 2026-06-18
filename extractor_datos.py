import pandas as pd
import re
import sys
import unicodedata
from config import RUTA_EXCEL, TRADUCCION_TIPOS, MAPA_UI

def limpiar_texto(texto):
    """Quita acentos y pasa a minúsculas para comparaciones exactas."""
    texto_sin_acentos = unicodedata.normalize('NFD', str(texto)).encode('ascii', 'ignore').decode('utf-8')
    return texto_sin_acentos.lower().strip()

def asignar_piscina_forms(es_pieza, es_volumen, dict_captura, dict_ubicacion, separar_ubicacion):
    """Calcula matemáticamente y distribuye dinámicamente los 10 Forms."""
    forms_disponibles = list(range(1, 11))
    rutas = {}
    total_vars = len(dict_captura)
    
    def calcular_paginas_contractiles(t_vars):
        """Calcula páginas: intermedias soportan 6, la última soporta 5."""
        if t_vars == 0: return 1
        paginas = 0
        v_left = t_vars
        while True:
            paginas += 1
            if v_left <= 5: break
            v_left -= 6
        return paginas
    
    try:
        paginas_necesarias = calcular_paginas_contractiles(total_vars)
        
        if es_pieza:
            rutas['pieza'] = {
                'login': forms_disponibles.pop(0),
                'loc1': forms_disponibles.pop(0),
                'loc2': forms_disponibles.pop(0) if (separar_ubicacion and len(dict_ubicacion) > 1) else None
            }
            rutas['pieza']['datos'] = [forms_disponibles.pop(0) for _ in range(paginas_necesarias)]
            
        if es_volumen:
            rutas['volumen'] = {
                'login': forms_disponibles.pop(0),
                'loc1': forms_disponibles.pop(0),
                'loc2': forms_disponibles.pop(0) if (separar_ubicacion and len(dict_ubicacion) > 1) else None
            }
            rutas['volumen']['datos'] = [forms_disponibles.pop(0) for _ in range(paginas_necesarias)]
            
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
                    
            es_catalogo = "catalogo" in limpiar_texto(linea) or "lookup" in linea_limpia 
            
            datos = {
                'nombre_pantalla': nombre_original, 
                'longitud': min_max_final, 
                'tipo': TRADUCCION_TIPOS.get(limpiar_texto(tipo_bruto), "alphameric"),
                'es_catalogo': es_catalogo
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

        multiplo_catalogo = 20
        catalogo_asignado = False
        
        todas_las_vars = list(dict_ubicacion.values()) + list(dict_captura.values())
        
        for v in todas_las_vars:
            if v.get('es_catalogo'):
                multiplo_catalogo = ((int(v['longitud'].split('-')[1]) + 4) // 5) * 5
                catalogo_asignado = True
                break
                
        if not catalogo_asignado:
            for v in todas_las_vars:
                if "sku" in limpiar_texto(v['nombre_pantalla']):
                    v['es_catalogo'] = True
                    multiplo_catalogo = ((int(v['longitud'].split('-')[1]) + 4) // 5) * 5
                    break

        plan_vuelo = asignar_piscina_forms(es_pieza, es_volumen, dict_captura, dict_ubicacion, regla_separar)

        # =========================================================
        # CHECKLIST DE PRE-VUELO (CONFIRMACIÓN DE DATOS)
        # =========================================================
        solicitante = str(solicitud.get('NOMBRE DE QUIEN SOLICITA EL AGX', 'No especificado')).strip()
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
        print(f"➤ Pedido por     : {solicitante}")
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
        if 'Cantidad' in info_cantidad['nombre_pantalla']:
            todas_las_variables.append(info_cantidad)
            
        for var in todas_las_variables:
            if var is not None:
                indicativo_lookup = " <- 2nd Lookup File" if var.get('es_catalogo') else ""
                tipo_dato = str(var.get('tipo', 'alphameric')).upper() 
                print(f"   • {var['nombre_pantalla']} (Tipo: {tipo_dato} | Longitud: {var['longitud']}){indicativo_lookup}")
        
        print("="*55)

        return {
            'es_pieza': es_pieza,
            'es_volumen': es_volumen,
            'cliente': cliente,
            'tipo_agx': tipo_agx,
            'plan_vuelo': plan_vuelo,
            'loc_items': loc_items,
            'info_cantidad': info_cantidad,
            'multiplo_catalogo': multiplo_catalogo,
            'dict_captura': dict_captura
        }

    except Exception as e:
        print(f"❌ Error en la curación de datos: {e}")
        sys.exit()