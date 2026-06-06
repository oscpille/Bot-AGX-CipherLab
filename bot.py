import pandas as pd
import pyautogui
import time
import sys # Nos sirve para detener el bot por completo si hay un error
# Al inicio de tu bot, junto a tus otros imports:
from mapeo_batch import MAPA_UI

# ¡Listo! Ya puedes usar las coordenadas directamente:
coord_x_prompt = MAPA_UI["vista_form"]["tabla"]["columnas_x"]["prompt"]
print(f"El bot hará clic en la coordenada X: {coord_x_prompt}")

# --- FASE 1: LEER EL CSV Y OBTENER EL CLIENTE ---
ruta_csv = r"C:\Users\dell\Documents\Bot AGX\UltimaFila.csv"

try:
    # Leemos el CSV
    df_csv = pd.read_csv(ruta_csv, encoding='utf-8-sig')
    
    # iloc[0] significa "la primera fila de datos" (que equivale a la fila 2 del Excel)
    solicitud = df_csv.iloc[0]
    
    # Tomamos la columna B por su encabezado exacto
    cliente = str(solicitud['INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:']).strip()
    
    print(f"✅ Dato extraído exitosamente. Cliente: {cliente}")

except KeyError:
    print("❌ Error: No se encontró la columna exacta. Verifica que el título sea 'INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:'")
    sys.exit() # Detiene el script
except Exception as e:
    print(f"❌ Error al leer el CSV: {e}")
    sys.exit() # Detiene el script


# --- FASE 2: BOT CLICKER ---
print("\n🤖 Iniciando el Bot Clicker en 5 segundos...")
print("⚠️ Por favor, cambia a la ventana de Forge AG y NO MUEVAS el ratón.")
time.sleep(5) 

try:
    # 1. Desplegar menú de "Forms"
    print("➤ Abriendo menú Forms...")
    pyautogui.click(301, 280)
    time.sleep(1) 

    # 2. Clickear en el Form 1
    print("➤ Seleccionando Form 1...")
    pyautogui.click(360, 295)
    time.sleep(1.5) 

    # 3. Clickear en la celda del nombre (1 solo clic, como descubriste)
    print("➤ Ubicando la celda de texto...")
    pyautogui.click(650, 550)
    time.sleep(0.5) 

    # 4. Escribir el nombre del inventario
    print(f"➤ Escribiendo el cliente: {cliente}")
    pyautogui.write(cliente, interval=0.05)
    time.sleep(0.5)
    
    # Confirmar la entrada
    pyautogui.press('enter')
    
    print("\n✅ ¡Modificación del Form 1 completada!")

except Exception as e:
    print(f"\n❌ El bot se detuvo en los clics por un error: {e}")