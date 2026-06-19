import sys
from extractor_datos import procesar_fila_excel
from bot_motor import ejecutar_bot
from actualizador_excel import actualizar_estatus_excel
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
            
        try:
            ejecutar_bot(datos_extraidos)
            # Si el bot termina exitosamente, actualizamos el estatus
            actualizar_estatus_excel(
                fila=datos_extraidos['fila_excel'], 
                columna=datos_extraidos['col_estatus'], 
                nuevo_estatus='COMPLETADO'
            )
        except Exception as e:
            print(f"\n❌ El bot se detuvo inesperadamente debido a un error: {e}")
            # Si hubo un error en tiempo de ejecución, marcamos como ERROR
            actualizar_estatus_excel(
                fila=datos_extraidos['fila_excel'], 
                columna=datos_extraidos['col_estatus'], 
                nuevo_estatus='ERROR'
            )

if __name__ == "__main__":
    main()