import pandas as pd

# 1. Definir las rutas
ruta_excel = r"C:\Users\dell\OneDrive - Profesionales en Inventarios SA de CV\FORMATO DE SOLICITUD DE AGX.xlsx"
ruta_csv_salida = r"C:\Users\dell\Documents\Bot AGX\UltimaFila.csv"

try:
    # 2. Leer SOLO las columnas de la F a la K del Excel
    # El parámetro usecols="F:K" evita cargar en memoria datos innecesarios
    df = pd.read_excel(ruta_excel, usecols="F:K", engine='openpyxl')

    # 3. Extraer únicamente la última fila
    # Al usar [-1:] en lugar de [-1], mantenemos la estructura de tabla (DataFrame)
    ultima_fila = df.iloc[-1:]

    # 4. Convertir y guardar en formato CSV
    # index=False evita que se imprima el número de fila original
    # encoding='utf-8-sig' garantiza que los acentos y caracteres especiales no se rompan
    ultima_fila.to_csv(ruta_csv_salida, index=False, encoding='utf-8-sig')

    print("✅ ¡Éxito! La extracción se completó correctamente.")
    print(f"El archivo se guardó como: {ruta_csv_salida}")
    
    # Imprimir en consola para validación visual rápida
    print("\n--- Vista previa de los datos extraídos ---")
    print(ultima_fila.to_string(index=False))

except FileNotFoundError:
    print("❌ Error: No se pudo encontrar el archivo de Excel. Verifica que la ruta y el nombre sean correctos y que OneDrive esté sincronizado.")
except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")   