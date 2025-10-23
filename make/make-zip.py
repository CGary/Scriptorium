# -*- coding: utf-8 -*-

import os
import sys
import zipfile

def leer_excepciones(ruta_archivo='exceptions'):
    """
    Lee el archivo de excepciones y devuelve un conjunto (set) de nombres a ignorar.
    Si el archivo no existe, devuelve un conjunto vacío.
    """
    if not os.path.exists(ruta_archivo):
        print(f"Advertencia: No se encontró el archivo de excepciones en '{ruta_archivo}'. No se excluirá nada.")
        return set()
    
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        # Leemos cada línea, quitamos espacios en blanco y las añadimos al conjunto.
        excepciones = {line.strip() for line in f if line.strip()}
    
    print(f"Excepciones cargadas: {excepciones}")
    return excepciones

def crear_zip(ruta_carpeta, nombre_zip, excepciones):
    """
    Crea un archivo .zip a partir de una carpeta, excluyendo los archivos y
    directorios especificados.
    """
    print(f"Creando archivo '{nombre_zip}' desde la carpeta '{ruta_carpeta}'...")
    
    try:
        # Creamos un nuevo archivo zip en modo escritura
        with zipfile.ZipFile(nombre_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # os.walk recorre el árbol de directorios de forma recursiva
            for root, dirs, files in os.walk(ruta_carpeta):
                # --- Lógica de exclusión de carpetas ---
                # Modificamos la lista 'dirs' en el lugar para que os.walk
                # no entre en los directorios que queremos excluir.
                # Usamos dirs[:] para crear una copia y poder modificar la original.
                dirs[:] = [d for d in dirs if d not in excepciones]

                # --- Lógica de exclusión de archivos ---
                archivos_a_incluir = [f for f in files if f not in excepciones]

                for file in archivos_a_incluir:
                    # Creamos la ruta completa del archivo a añadir
                    ruta_completa = os.path.join(root, file)
                    
                    # Creamos la ruta relativa para que la estructura de carpetas
                    # dentro del zip sea correcta.
                    ruta_relativa = os.path.relpath(ruta_completa, ruta_carpeta)
                    
                    print(f"  + Añadiendo: {ruta_relativa}")
                    zipf.write(ruta_completa, ruta_relativa)
                    
        print(f"\n¡Éxito! El archivo '{nombre_zip}' ha sido creado correctamente.")

    except FileNotFoundError:
        print(f"Error: La carpeta '{ruta_carpeta}' no fue encontrada.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")


def main():
    """
    Función principal del script.
    """
    # 1. Verificar los argumentos de la línea de comandos
    if len(sys.argv) != 2:
        print("Uso incorrecto.")
        print(f"Ejemplo: python {sys.argv[0]} nombre_de_la_carpeta")
        sys.exit(1) # Salir del script con un código de error

    # El primer argumento (índice 1) es el nombre de la carpeta
    nombre_carpeta = sys.argv[1]

    # Quitar una posible barra al final del nombre para consistencia
    if nombre_carpeta.endswith('/'):
        nombre_carpeta = nombre_carpeta[:-1]

    # 2. Comprobar si la carpeta a comprimir existe
    if not os.path.isdir(nombre_carpeta):
        print(f"Error: La carpeta '{nombre_carpeta}' no existe o no es un directorio.")
        sys.exit(1)

    # 3. Definir el nombre del archivo .zip de salida
    nombre_archivo_zip = f"{nombre_carpeta}.zip"

    # 4. Cargar la lista de excepciones
    excepciones = leer_excepciones()

    # 5. Llamar a la función para crear el zip
    crear_zip(nombre_carpeta, nombre_archivo_zip, excepciones)


if __name__ == "__main__":
    main()

