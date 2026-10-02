import sys
import os
import time
import base64
import requests
import threading
import tkinter as tk
import json
import logging
import warnings
# Suprimir warnings
warnings.filterwarnings("ignore", category=UserWarning, module="google.cloud")
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

from config import db
from extractor_datos import procesar_solicitud
from bot_motor import ejecutar_bot

def preguntar_al_usuario(root, cantidad):
    """
    Despliega una ventana emergente de Tkinter preguntando si se debe iniciar.
    Retorna True si se presionó Sí o si pasaron 10 segundos.
    Retorna False si se presionó Posponer.
    """
    resultado = [False]
    
    top = tk.Toplevel(root)
    top.title("AGX Bot - Modo Vigía")
    
    # Centrar la ventana y hacerla flotar sobre todo
    ancho = 420
    alto = 150
    pantalla_ancho = top.winfo_screenwidth()
    pantalla_alto = top.winfo_screenheight()
    x = int((pantalla_ancho/2) - (ancho/2))
    y = int((pantalla_alto/2) - (alto/2))
    top.geometry(f"{ancho}x{alto}+{x}+{y}")
    top.attributes('-topmost', True)
    
    # Evitar que la ventana colapse visualmente
    top.resizable(False, False)

    lbl = tk.Label(top, text=f"Hay {cantidad} AGX pendientes.\n¿Comenzar creación? (Iniciará automáticamente en 10s)", font=("Arial", 11, "bold"))
    lbl.pack(pady=20)

    tiempo_restante = 10
    
    def on_yes():
        resultado[0] = True
        top.destroy()
        root.quit()
        
    def on_no():
        resultado[0] = False
        top.destroy()
        root.quit()
        
    # Manejar el botón de cerrar la ventana (X)
    top.protocol("WM_DELETE_WINDOW", on_no)
        
    def update_timer():
        nonlocal tiempo_restante
        if not top.winfo_exists():
            return
        tiempo_restante -= 1
        if tiempo_restante <= 0:
            on_yes()
        else:
            try:
                lbl.config(text=f"Hay {cantidad} AGX pendientes.\n¿Comenzar creación? (Iniciará automáticamente en {tiempo_restante}s)")
                top.after(1000, update_timer)
            except tk.TclError:
                pass # Ignorar si la ventana ya fue cerrada manualmente

    btn_frame = tk.Frame(top)
    btn_frame.pack()
    
    btn_yes = tk.Button(btn_frame, text="Sí, Iniciar Ahora", command=on_yes, bg="#28a745", fg="white", font=("Arial", 10, "bold"), width=15)
    btn_yes.pack(side=tk.LEFT, padx=10)
    
    btn_no = tk.Button(btn_frame, text="Posponer (5 min)", command=on_no, bg="#dc3545", fg="white", font=("Arial", 10, "bold"), width=15)
    btn_no.pack(side=tk.RIGHT, padx=10)

    top.after(1000, update_timer)
    
    # Traer al frente y dar foco
    top.lift()
    top.focus_force()

    root.mainloop()
    return resultado[0]


def actualizar_latido():
    while True:
        if db:
            try:
                db.table('configuracion').upsert({
                    'id': 'estado_servidor',
                    'ultimo_latido': time.time()
                }).execute()
            except Exception:
                pass
        time.sleep(60)

def main():
    # Prevenir que Windows entre en modo suspensión (bajo consumo) mientras el bot esté abierto
    import ctypes
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)

    # ---------------------------------------------------------
    # LÓGICA DE SYSTEM TRAY (ICONOS OCULTOS)
    # ---------------------------------------------------------
    import pystray
    from PIL import Image, ImageDraw
    import sys
    
    kernel32 = ctypes.WinDLL('kernel32')
    user32 = ctypes.WinDLL('user32')
    hWnd = kernel32.GetConsoleWindow()
    
    # Ocultar la consola automáticamente al abrir y deshabilitar su botón "X"
    if hWnd:
        user32.ShowWindow(hWnd, 0) # SW_HIDE
        hMenu = user32.GetSystemMenu(hWnd, False)
        if hMenu:
            user32.EnableMenuItem(hMenu, 0xF060, 1) # SC_CLOSE (0xF060) | MF_GRAYED (1)

    def on_show(icon, item):
        if hWnd: user32.ShowWindow(hWnd, 5) # SW_SHOW

    def on_hide(icon, item):
        if hWnd: user32.ShowWindow(hWnd, 0) # SW_HIDE
        
    def on_quit(icon, item):
        icon.stop()
        os._exit(0)

    def create_image():
        image = Image.new('RGB', (64, 64), color=(0, 0, 0))
        dc = ImageDraw.Draw(image)
        dc.rectangle((16, 16, 48, 48), fill=(40, 167, 69))
        return image
        
    tray_icon = pystray.Icon("AGX Vigía", create_image(), "AGX Bot (Vigía)", menu=pystray.Menu(
        pystray.MenuItem("Mostrar Consola", on_show),
        pystray.MenuItem("Ocultar Consola", on_hide),
        pystray.MenuItem("Cerrar Bot", on_quit)
    ))
    tray_icon.run_detached()
    # ---------------------------------------------------------

    # Instanciar Tkinter de forma persistente y ocultarlo
    root_tk = tk.Tk()
    root_tk.withdraw()

    threading.Thread(target=actualizar_latido, daemon=True).start()
    print("=====================================================")
    print("      ORQUESTADOR DE BOT AGX INICIADO (MODO VIGÍA)   ")
    print("=====================================================")
    print("➤ El bot está monitoreando en segundo plano 24/7...")
    print("➤ Prevención de Suspensión de Windows ACTIVADA (El equipo no se dormirá).")
    print("➤ La consola está anclada a la barra de tareas (Iconos Ocultos).")
    
    while True:
        if not db:
            print("⚠️ Esperando a que se configure la conexión con Supabase...")
            time.sleep(30)
            continue
            
        try:
            # Primero consultamos TODOS los registros sin filtrar para ver qué hay realmente en la base de datos
            debug_resp = db.table('AGX').select('*').execute()
            print(f"🔎 DEBUG TOTAL FILAS EN LA TABLA: {len(debug_resp.data)}")
            if len(debug_resp.data) > 0:
                print(f"🔎 DEBUG PRIMERA FILA (Status): '{debug_resp.data[0].get('Status_AGX')}'")

            response = db.table('AGX').select('*').eq('Status_AGX', 'Solicitado').execute()
            todas_las_docs = response.data
            print(f"🔎 DEBUG FILAS 'Solicitado': {len(todas_las_docs)}")
            
            solicitudes_pendientes = []
            def mapear_doc(d):
                dp = {}
                dp['¿QUÉ MODELO DE AGX NECESITAS?'] = d.get('Modelo_AGX', '')
                dp['INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:'] = d.get('Nombre_AGX', '')
                dp['¿DE QUÉ TIPO SERÁ?'] = d.get('Tipo_AGX', '')
                dp['FLUJO OPERATIVO:'] = d.get('Flujo_AGX', '')
                
                datos_agx = d.get('Datos_AGX') or {}
                dp['¿QUÉ NIVEL DE PRIORIDAD DAREMOS?'] = datos_agx.get('Prioridad', '')
                
                vars_req = datos_agx.get('Variables_Requeridas', '')
                if isinstance(vars_req, list):
                    vars_req = '\n'.join(vars_req)
                elif isinstance(vars_req, dict):
                    vars_req = '\n'.join([f"{k} {v}" for k, v in vars_req.items()])
                dp['DATOS REQUERIDOS'] = vars_req
                
                dp['MARBETE Y UBICACIÓN'] = datos_agx.get('Marbete_Ubicacion', '')
                dp['id_solicitud'] = str(d.get('AGX_id', ''))
                dp['chat_id'] = d.get('Chat_id', '')
                dp['mention_id'] = d.get('Mention_id', None)
                dp['supabase_id'] = d.get('AGX_id')
                return dp

            grupos = {}
            for doc in todas_las_docs:
                key = (
                    doc.get('Modelo_AGX', ''), 
                    doc.get('Nombre_AGX', ''), 
                    doc.get('Flujo_AGX', ''), 
                    json.dumps(doc.get('Datos_AGX', {}), sort_keys=True), 
                    doc.get('Chat_id', '')
                )
                if key not in grupos:
                    grupos[key] = []
                grupos[key].append(doc)

            solicitudes_pendientes = []
            for key, docs_en_grupo in grupos.items():
                tipos = {d.get('Tipo_AGX') for d in docs_en_grupo}
                if 'Abierto' in tipos and 'Cerrado' in tipos:
                    doc_abierto = next(d for d in docs_en_grupo if d.get('Tipo_AGX') == 'Abierto')
                    doc_cerrado = next(d for d in docs_en_grupo if d.get('Tipo_AGX') == 'Cerrado')
                    
                    merged_doc = doc_abierto.copy()
                    merged_doc['Tipo_AGX'] = 'Ambos'
                    dp = mapear_doc(merged_doc)
                    dp['AGX_ids_merged'] = {
                        'Abierto': doc_abierto.get('AGX_id'),
                        'Cerrado': doc_cerrado.get('AGX_id')
                    }
                    solicitudes_pendientes.append(dp)
                    
                    for d in docs_en_grupo:
                        if d != doc_abierto and d != doc_cerrado:
                            solicitudes_pendientes.append(mapear_doc(d))
                else:
                    for d in docs_en_grupo:
                        solicitudes_pendientes.append(mapear_doc(d))
                
        except Exception as e:
            print(f"⚠️ Error de red consultando la nube: {e}")
            time.sleep(30)
            continue
            
        if not solicitudes_pendientes:
            time.sleep(30)
            continue
            
        print(f"\n🔔 Se encontraron {len(solicitudes_pendientes)} solicitudes pendientes.")
        
        # Invocar la ventana gráfica emergente
        iniciar = preguntar_al_usuario(root_tk, len(solicitudes_pendientes))
        
        if not iniciar:
            print("🛑 Proceso pospuesto por el usuario. Durmiendo por 5 minutos...")
            time.sleep(300) # Dormir 5 minutos antes de volver a preguntar
            continue
            
        # ====================================================
        # INICIA LA RÁFAGA
        # ====================================================
        print("\n▶️ Despertando equipo y arrancando motores de automatización...")
        import pyautogui
        import ctypes
        
        # 1. Desactivar el Fail-Safe de PyAutoGUI para evitar bloqueos si el sistema lee (0,0)
        pyautogui.FAILSAFE = False
        
        # 2. Matar el proceso del protector de pantalla (scrnsave.scr) si está ejecutándose
        import os
        os.system("taskkill /IM scrnsave.scr /F >nul 2>&1")
        
        # 3. Forzar el encendido del monitor (por si estaba en ahorro de energía)
        HWND_BROADCAST = 0xFFFF
        WM_SYSCOMMAND = 0x0112
        SC_MONITORPOWER = 0xF170
        ctypes.windll.user32.SendMessageW(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, -1)
        
        time.sleep(2.0) # Dar 2 segundos para que la pantalla encienda y reaccione
        
        for indice, solicitud in enumerate(solicitudes_pendientes, start=1):
            print(f"\n{'-'*50}")
            print(f"🚀 INICIANDO SOLICITUD {indice}/{len(solicitudes_pendientes)}")
            print(f"{'-'*50}")
            
            datos_extraidos = procesar_solicitud(solicitud)
            
            try:
                archivos_generados = ejecutar_bot(datos_extraidos)
                
                id_solicitud = datos_extraidos['id_solicitud']
                chat_id = datos_extraidos.get('chat_id', '')
                mention_id = datos_extraidos.get('mention_id', None)
                
                import re
                print(f"\n➤ Subiendo archivos al Storage (Supabase) para la solicitud ID: {id_solicitud}...")
                
                archivos_para_subir = []
                for ruta in archivos_generados:
                    file_name = os.path.basename(ruta)
                    # Saneamos el nombre solo para la ruta de la nube (reemplazamos todo lo raro con guión bajo)
                    safe_file_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', file_name)
                    storage_path = f"AGX Solicitados/{id_solicitud}_{safe_file_name}"
                    
                    try:
                        with open(ruta, "rb") as f:
                            db.storage.from_("agx_archivos").upload(
                                path=storage_path,
                                file=f,
                                file_options={"content-type": "application/x-zip-compressed"}
                            )
                        url_publica = db.storage.from_("agx_archivos").get_public_url(storage_path)
                        archivos_para_subir.append({
                            "file_name": file_name,  # Mantenemos el nombre original para WhatsApp
                            "url": url_publica
                        })
                    except Exception as e:
                        print(f"⚠️ Error subiendo {file_name} al Storage: {e}")
                    
                def update_supabase_with_retry(table_id, data_update):
                    subida_exitosa = False
                    intentos = 0
                    while not subida_exitosa:
                        try:
                            db.table('AGX').update(data_update).eq('AGX_id', table_id).execute()
                            subida_exitosa = True
                        except Exception as req_e:
                            intentos += 1
                            print(f"⚠️ Error actualizando Supabase (Intento {intentos}). Reintentando... Error: {req_e}")
                            time.sleep(10)

                agx_ids_merged = solicitud.get('AGX_ids_merged')
                if agx_ids_merged and db:
                    archivo_abierto = [a for a in archivos_para_subir if "[A]" in a["file_name"]]
                    archivo_cerrado = [a for a in archivos_para_subir if "[C]" in a["file_name"]]
                    if archivo_abierto:
                        update_supabase_with_retry(agx_ids_merged['Abierto'], {'Status_AGX': 'Finalizado', 'Archivos_AGX': archivo_abierto})
                    if archivo_cerrado:
                        update_supabase_with_retry(agx_ids_merged['Cerrado'], {'Status_AGX': 'Finalizado', 'Archivos_AGX': archivo_cerrado})
                    print(f"✅ Archivos subidos y tablas combinadas (Abierto/Cerrado) actualizadas exitosamente.")
                else:
                    supabase_id = solicitud.get('supabase_id')
                    if supabase_id and db:
                        update_supabase_with_retry(supabase_id, {'Status_AGX': 'Finalizado', 'Archivos_AGX': archivos_para_subir})
                        print(f"✅ Archivos subidos y tabla actualizada exitosamente.")
                
                # Limpieza obligatoria post-ejecución (destrucción de instancia)
                print("\n➤ Ejecutando purga del entorno ForgeAG (Taskkill)...")
                os.system("taskkill /IM ForgeAG.exe /F /T >nul 2>&1")
                time.sleep(1.0) # Breve pausa para asegurar el cierre antes de la siguiente solicitud
                
            except Exception as e:
                print(f"\n❌ El bot se detuvo en esta solicitud debido a un error: {e}")
                print("Pausando el bot por 5 minutos antes del próximo intento...")
                os.system("taskkill /IM ForgeAG.exe /F /T >nul 2>&1")
                # Dormir 5 minutos para que el ciclo no arroje un popup instantáneo otra vez
                time.sleep(300)
                break
                
        print("\n✅ RÁFAGA FINALIZADA. Volviendo a modo vigía...")
        time.sleep(30) # Espera normal antes del siguiente chequeo

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido manualmente por el usuario. ¡Hasta pronto!")
        sys.exit(0)