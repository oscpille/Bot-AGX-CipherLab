import sys
import os
import time
import base64
import requests
import threading
import tkinter as tk
import logging
import warnings
from google.cloud.firestore_v1.base_query import FieldFilter

# Suprimir warnings visuales de Google Cloud
warnings.filterwarnings("ignore", category=UserWarning, module="google.cloud")
logging.getLogger("google").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

from config import db
from extractor_datos import procesar_solicitud
from bot_motor import ejecutar_bot

def preguntar_al_usuario(cantidad):
    """
    Despliega una ventana emergente de Tkinter preguntando si se debe iniciar.
    Retorna True si se presionó Sí o si pasaron 10 segundos.
    Retorna False si se presionó Posponer.
    """
    resultado = [False]
    root = tk.Tk()
    root.title("AGX Bot - Modo Vigía")
    
    # Centrar la ventana y hacerla flotar sobre todo
    ancho = 420
    alto = 150
    pantalla_ancho = root.winfo_screenwidth()
    pantalla_alto = root.winfo_screenheight()
    x = int((pantalla_ancho/2) - (ancho/2))
    y = int((pantalla_alto/2) - (alto/2))
    root.geometry(f"{ancho}x{alto}+{x}+{y}")
    root.attributes('-topmost', True)
    
    # Evitar que la ventana colapse visualmente
    root.resizable(False, False)

    lbl = tk.Label(root, text=f"Hay {cantidad} AGX pendientes.\n¿Comenzar creación? (Iniciará automáticamente en 10s)", font=("Arial", 11, "bold"))
    lbl.pack(pady=20)

    tiempo_restante = 10
    
    def on_yes():
        resultado[0] = True
        root.destroy()
        
    def on_no():
        resultado[0] = False
        root.destroy()
        
    def update_timer():
        nonlocal tiempo_restante
        tiempo_restante -= 1
        if tiempo_restante <= 0:
            on_yes()
        else:
            try:
                lbl.config(text=f"Hay {cantidad} AGX pendientes.\n¿Comenzar creación? (Iniciará automáticamente en {tiempo_restante}s)")
                root.after(1000, update_timer)
            except tk.TclError:
                pass # Ignorar si la ventana ya fue cerrada manualmente

    btn_frame = tk.Frame(root)
    btn_frame.pack()
    
    btn_yes = tk.Button(btn_frame, text="Sí, Iniciar Ahora", command=on_yes, bg="#28a745", fg="white", font=("Arial", 10, "bold"), width=15)
    btn_yes.pack(side=tk.LEFT, padx=10)
    
    btn_no = tk.Button(btn_frame, text="Posponer (5 min)", command=on_no, bg="#dc3545", fg="white", font=("Arial", 10, "bold"), width=15)
    btn_no.pack(side=tk.RIGHT, padx=10)

    root.after(1000, update_timer)
    
    # Traer al frente y dar foco
    root.lift()
    root.focus_force()

    root.mainloop()
    return resultado[0]


def actualizar_latido():
    while True:
        if db:
            try:
                db.collection('configuracion').document('estado_servidor').set({
                    'ultimo_latido': time.time()
                }, merge=True)
            except Exception:
                pass
        time.sleep(60)

def main():
    threading.Thread(target=actualizar_latido, daemon=True).start()
    print("=====================================================")
    print("      ORQUESTADOR DE BOT AGX INICIADO (MODO VIGÍA)   ")
    print("=====================================================")
    print("➤ El bot está monitoreando en segundo plano...")
    print("➤ Puedes minimizar esta ventana negra y seguir trabajando.")
    
    while True:
        if not db:
            print("⚠️ Esperando a que se configure la conexión con Firebase...")
            time.sleep(30)
            continue
            
        try:
            docs = db.collection('solicitudes').where(filter=FieldFilter('ESTATUS', '==', 'PENDIENTE')).get()
            todas_las_docs = list(docs)
            
            solicitudes_pendientes = []
            for doc in todas_las_docs:
                datos_crudos = doc.to_dict()
                
                # Aplanar los datos para el extractor_datos.py
                datos_planos = {}
                if '2_Respuestas_del_Cliente' in datos_crudos:
                    resp = datos_crudos['2_Respuestas_del_Cliente']
                    datos_planos['¿QUÉ MODELO DE AGX NECESITAS?'] = resp.get('Modelo_AGX', '')
                    datos_planos['INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:'] = resp.get('Cliente', '')
                    datos_planos['¿DE QUÉ TIPO SERÁ?'] = resp.get('Tipo', '')
                    datos_planos['FLUJO OPERATIVO:'] = resp.get('Flujo_Operativo', '')
                    datos_planos['¿QUÉ NIVEL DE PRIORIDAD DAREMOS?'] = resp.get('Prioridad', '')
                    datos_planos['DATOS REQUERIDOS'] = resp.get('Variables_Requeridas', '')
                    datos_planos['MARBETE Y UBICACIÓN'] = resp.get('Marbete_Ubicacion', '')
                else:
                    # Formato viejo
                    datos_planos = datos_crudos.copy()
                
                if '3_Metadatos_Internos' in datos_crudos:
                    meta = datos_crudos['3_Metadatos_Internos']
                    datos_planos['id_solicitud'] = meta.get('id_solicitud', doc.id)
                    datos_planos['chat_id'] = meta.get('chat_id', '')
                    datos_planos['mention_id'] = meta.get('mention_id', None)
                else:
                    # Formato viejo
                    datos_planos['id_solicitud'] = datos_crudos.get('id_solicitud', doc.id)
                    datos_planos['chat_id'] = datos_crudos.get('chat_id', '')
                    datos_planos['mention_id'] = datos_crudos.get('mention_id', None)
                    
                datos_planos['firebase_id'] = doc.id
                solicitudes_pendientes.append(datos_planos)
                
        except Exception as e:
            print(f"⚠️ Error de red consultando la nube: {e}")
            time.sleep(30)
            continue
            
        if not solicitudes_pendientes:
            time.sleep(30)
            continue
            
        print(f"\n🔔 Se encontraron {len(solicitudes_pendientes)} solicitudes pendientes.")
        
        # Invocar la ventana gráfica emergente
        iniciar = preguntar_al_usuario(len(solicitudes_pendientes))
        
        if not iniciar:
            print("🛑 Proceso pospuesto por el usuario. Durmiendo por 5 minutos...")
            time.sleep(300) # Dormir 5 minutos antes de volver a preguntar
            continue
            
        # ====================================================
        # INICIA LA RÁFAGA
        # ====================================================
        print("\n▶️ Arrancando motores de automatización...")
        
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
                
                print(f"\n➤ Subiendo archivos a la Nube (Firebase) para la solicitud ID: {id_solicitud}...")
                
                archivos_para_subir = []
                for ruta in archivos_generados:
                    with open(ruta, "rb") as f:
                        file_b64 = base64.b64encode(f.read()).decode('utf-8')
                    file_name = os.path.basename(ruta)
                    
                    archivos_para_subir.append({
                        "file_base64": file_b64,
                        "file_name": file_name
                    })
                    
                firebase_id = solicitud.get('firebase_id')
                if firebase_id and db:
                    subida_exitosa = False
                    intentos = 0
                    while not subida_exitosa:
                        try:
                            db.collection('solicitudes').document(firebase_id).set({
                                '1_Estado_de_Orden': {
                                    'Estatus': 'COMPLETADO',
                                    'Entregado_al_usuario': False
                                },
                                '4_Archivos_Entregados': archivos_para_subir,
                                'ESTATUS': 'COMPLETADO',
                                'archivos': archivos_para_subir,
                                'entregado_al_usuario': False
                            }, merge=True)
                            print(f"✅ Archivos subidos a la nube y cola actualizada.")
                            subida_exitosa = True
                        except Exception as req_e:
                            intentos += 1
                            print(f"⚠️ No se pudo subir el archivo a Firebase (Intento {intentos}). Reintentando en 10 segundos... Error: {req_e}")
                            time.sleep(10)
                
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