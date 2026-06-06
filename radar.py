import pyautogui
import time

print("Presiona Ctrl + C en la terminal para detener el script.")
print("Mueve el ratón a los botones de Forge AG para obtener sus coordenadas...\n")

try:
    while True:
        # Obtiene la posición actual del ratón
        x, y = pyautogui.position()
        posicion = f"Coordenadas actuales -> X: {str(x).rjust(4)} | Y: {str(y).rjust(4)}"
        
        # Imprime en la misma línea para no llenar toda tu terminal
        print(posicion, end='\r')
        time.sleep(0.1)
        
except KeyboardInterrupt:
    print("\n\n¡Mapeo terminado!")