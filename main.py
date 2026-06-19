import sys
import os
import time
import base64
import requests
from config import TERMUX_API_URL
from extractor_datos import procesar_solicitud
from bot_motor import ejecutar_bot

def main():
    print("=====================================================")
    print("           ORQUESTADOR DE BOT AGX INICIADO           ")
    print("=====================================================")
    
    print("➤ Conectando al servidor Termux local para obtener la cola...")
    try:
        response = requests.get(f"{TERMUX_API_URL}/queue", timeout=5)
        cola = response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ No se pudo conectar al celular (Termux): {e}")
        sys.exit()
        
    solicitudes_pendientes = [s for s in cola if s.get('ESTATUS:') == 'PENDIENTE']
    
    if not solicitudes_pendientes:
        print("\n✅ Bandeja limpia: No hay solicitudes PENDIENTES por procesar. Cerrando...")
        sys.exit()
        
    print(f"\n🔔 Se encontraron {len(solicitudes_pendientes)} solicitudes pendientes.")
    
    respuesta = input("¿Comenzar procesamiento en lote? (s/n): ").strip().lower()
    if respuesta != 's':
        print("\n🛑 Proceso abortado por el usuario. Saliendo del sistema...")
        sys.exit()
        
    # Iterar sobre todas las solicitudes en modo ráfaga
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
            
            print(f"\n➤ Avisando al servidor Termux para borrar solicitud ID: {id_solicitud}...")
            
            for ruta in archivos_generados:
                with open(ruta, "rb") as f:
                    file_b64 = base64.b64encode(f.read()).decode('utf-8')
                file_name = os.path.basename(ruta)
                
                payload = {
                    "id_solicitud": id_solicitud,
                    "chat_id": chat_id,
                    "mention_id": mention_id,
                    "file_base64": file_b64,
                    "file_name": file_name
                }
                
                try:
                    requests.post(f"{TERMUX_API_URL}/queue/complete", json=payload, timeout=20)
                    print(f"✅ Archivo {file_name} transmitido al celular y cola actualizada.")
                except Exception as req_e:
                    print(f"⚠️ No se pudo contactar al servidor Termux para subir el archivo: {req_e}")
            
            # Limpieza obligatoria post-ejecución (destrucción de instancia)
            print("\n➤ Ejecutando purga del entorno ForgeAG (Taskkill)...")
            os.system("taskkill /IM ForgeAG.exe /F /T >nul 2>&1")
            time.sleep(1.0) # Breve pausa para asegurar el cierre antes de la siguiente solicitud
            
        except Exception as e:
            print(f"\n❌ El bot se detuvo en esta solicitud debido a un error: {e}")
            print("La solicitud se mantiene en Termux para revisión manual o reinicio.")
            # Forzamos cierre para no arrastrar la ventana corrupta a la siguiente solicitud
            os.system("taskkill /IM ForgeAG.exe /F /T >nul 2>&1")
            
    print("\n=====================================================")
    print("✅ RÁFAGA FINALIZADA. COLA VACÍA. APAGANDO MOTORES.")
    print("=====================================================")

if __name__ == "__main__":
    main()