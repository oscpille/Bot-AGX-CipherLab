import sys
from extractor_datos import procesar_fila_excel
from bot_motor import ejecutar_bot

def main():
    print("=====================================================")
    print("           ORQUESTADOR DE BOT AGX INICIADO           ")
    print("=====================================================")
    
    # Extrae y formatea toda la información del documento
    datos_extraidos = procesar_fila_excel()
    
    # Si hubo información a procesar, solicita permiso para iniciar la inyección
    if datos_extraidos:
        respuesta = input("\n¿Comenzamos? (s/n): ").strip().lower()
        if respuesta != 's':
            print("\n🛑 Proceso abortado por el usuario. Saliendo del sistema...")
            sys.exit()
            
        ejecutar_bot(datos_extraidos)

if __name__ == "__main__":
    main()