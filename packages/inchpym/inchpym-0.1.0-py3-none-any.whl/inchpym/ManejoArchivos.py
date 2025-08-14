import numpy as np
import pandas as pd
import os 
import shutil
from unidecode import unidecode

# Borrar los archivos si existen en la carpeta de bases Banrep
def BorrrarArchivo(rutaArchivo):  
    if os.path.exists(rutaArchivo):# Verificar si el archivo ya existe
        os.remove(rutaArchivo)

# Mueve los archivos descargados a la carpeta que se requiere
def moverArchivo(RutaOrigen, RutaDestino):
    try:
        shutil.move(RutaOrigen, RutaDestino)
        print(f"El archivo '{RutaOrigen}' se ha movido correctamente a '{RutaDestino}'.")
    except Exception as e:
        print(f"No se pudo mover el archivo '{RutaOrigen}' a '{RutaDestino}': {e}")

def copiarArchivo(RutaOrigen, RutaDestino):
    try:
        shutil.copy2(RutaOrigen, RutaDestino)  # `copy2` copia metadatos (marca de tiempo) además del archivo
        print(f"El archivo '{RutaOrigen}' se ha copiado correctamente a '{RutaDestino}'.")
    except Exception as e:
        print(f"No se pudo copiar el archivo '{RutaOrigen}' a '{RutaDestino}': {e}")

def obteneArchivoMasReciente(rutaCarpeta):
    # Obtener la lista de archivos en la carpeta
    archivos_en_carpeta = [archivo for archivo in os.listdir(rutaCarpeta) if archivo.endswith('.txt')]
    # Verificar si hay archivos en la carpeta
    if archivos_en_carpeta:
        # Obtener el archivo más reciente basado en la última modificación
        archivo_mas_reciente = max(archivos_en_carpeta, key=lambda x: os.path.getmtime(os.path.join(rutaCarpeta, x)))
        # Obtener la fecha de modificación del archivo más reciente
        fecha_modificacion = os.path.getmtime(os.path.join(rutaCarpeta, archivo_mas_reciente))
        return fecha_modificacion
    else:
        return None

# Quita las tildes de un DataFrame
def dfSinTildes(df_inicial):
    for columna in df_inicial.columns:
        if df_inicial[columna].dtype == 'object':
            df_inicial[columna] = df_inicial[columna].apply(unidecode)
    return  df_inicial

# Quita las tildes de los encabezados de un DataFrame        
def dfEncabezadosSinTildes(df_inicial):
    nuevos_nombres_columnas = [unidecode(columna) 
        if df_inicial[columna].dtype == 'object' else columna for columna in df_inicial.columns]
    df_inicial.columns = nuevos_nombres_columnas
    return  df_inicial

def GuardarRemplazarExcel(dataframe,ruta_salida,nombre_hoja, ejecutar=True):  
    if ejecutar:
        if os.path.exists(ruta_salida):
            os.remove(ruta_salida)
        dataframe.to_excel(ruta_salida,sheet_name=nombre_hoja, index=False)

def GuardarRemplazarCsv(dataframe,ruta_salida,nombre_hoja, ejecutar=True):  
    if ejecutar:
        if os.path.exists(ruta_salida):
            os.remove(ruta_salida)
        dataframe.to_csv(ruta_salida, index=False)

def GuardarRemplazarParquet(dataframe,ruta_salida,nombre_hoja, ejecutar=True):  
    if ejecutar:
        if os.path.exists(ruta_salida):
            os.remove(ruta_salida)
        dataframe.to_parquet(ruta_salida, index=False)
