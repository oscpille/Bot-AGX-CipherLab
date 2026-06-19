import win32com.client as win32
import os
import time
from config import RUTA_EXCEL

def actualizar_estatus_excel(fila, columna, nuevo_estatus):
    """
    Actualiza una celda específica del archivo de Excel usando la API COM de Windows.
    Esto permite esquivar el bloqueo de archivos (File Lock) en OneDrive si el usuario
    tiene el archivo abierto en su escritorio en ese momento.
    """
    print(f"\n➤ Intentando actualizar Estatus a '{nuevo_estatus}' en la fila {fila}...")
    
    try:
        target_path = os.path.abspath(RUTA_EXCEL)
        
        try:
            # 1. Intentar atrapar el libro si ya está abierto en la pantalla del usuario (esquiva File Lock)
            wb = win32.GetObject(target_path)
            opened_by_bot = False
        except Exception:
            # 2. Si no estaba abierto, creamos una instancia invisible y lo abrimos
            excel = win32.Dispatch("Excel.Application")
            excel.DisplayAlerts = False
            wb = excel.Workbooks.Open(target_path)
            opened_by_bot = True
            
        # Seleccionar la hoja y columna correcta dinámicamente
        ws_target = None
        col_target = columna
        
        for sheet in wb.Sheets:
            for c in range(1, 40):
                val = sheet.Cells(1, c).Value
                if val and "ESTATUS:" in str(val).upper().strip():
                    ws_target = sheet
                    col_target = c
                    break
            if ws_target:
                break
                
        if not ws_target:
            # Fallback a la primera hoja si no se encontró
            ws_target = wb.Sheets(1)
        
        # Inyectar el estatus
        ws_target.Cells(fila, col_target).Value = nuevo_estatus
        
        # Guardar los cambios
        wb.Save()
        
        # Si el bot fue quien lo abrió en memoria, lo cerramos limpiamente para no dejar procesos zombis
        if opened_by_bot:
            wb.Close(SaveChanges=True)
            
        print(f"✅ Estatus actualizado exitosamente a '{nuevo_estatus}'.")
            
    except Exception as e:
        print(f"⚠️ No se pudo actualizar el Excel automáticamente debido a un bloqueo o error COM: {e}")
        # Si falla, no crasheamos el bot principal, simplemente mostramos la advertencia
