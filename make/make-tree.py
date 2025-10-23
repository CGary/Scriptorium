import os
import sys
import fnmatch
from typing import List, Tuple

def read_exceptions(file: str) -> Tuple[List[str], List[str]]:
    """
    Lee una lista de archivos y directorios para excluir.
    - Ignora líneas que empiezan con '#'.
    - Ignora comentarios en la misma línea.
    - Separa las exclusiones en dos listas: nombres exactos y patrones (ej. *.log).
    """
    exact_matches = []
    patterns = []
    try:
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                # Ignorar comentarios y limpiar la línea
                rule = line.split('#', 1)[0].strip()
                if not rule:
                    continue
                
                # Separar patrones de nombres exactos
                if '*' in rule or '?' in rule:
                    patterns.append(rule)
                else:
                    exact_matches.append(rule)
                    
    except FileNotFoundError:
        print(f"Info: El archivo de excepciones '{file}' no fue encontrado. No se excluirá ningún archivo.")
    
    return exact_matches, patterns

def is_file_excluded(file_name: str, exact_exceptions: List[str], pattern_exceptions: List[str]) -> bool:
    """
    Verifica si un archivo debe ser excluido, ya sea por nombre exacto o por patrón.
    """
    if file_name in exact_exceptions:
        return True
    for pattern in pattern_exceptions:
        if fnmatch.fnmatch(file_name, pattern):
            return True
    return False

def generate_tree_structure(directory: str, exact_exceptions: List[str], pattern_exceptions: List[str]) -> str:
    """Genera una cadena con la estructura de árbol del directorio."""
    tree_lines = []
    # Almacenar la ruta absoluta para una comparación precisa
    abs_directory = os.path.abspath(directory)
    
    for root, dirs, files in os.walk(directory, topdown=True):
        # Excluir directorios
        dirs[:] = [d for d in dirs if not is_file_excluded(d, exact_exceptions, pattern_exceptions)]
        
        # Calcular el nivel de indentación
        abs_root = os.path.abspath(root)
        relative_root = os.path.relpath(abs_root, abs_directory)
        
        if relative_root == '.':
            level = 0
            # Mostrar solo el nombre base para el directorio raíz
            tree_lines.append(f"{os.path.basename(abs_directory)}/")
        else:
            level = relative_root.count(os.sep) + 1
            indent = ' ' * 4 * (level -1)
            tree_lines.append(f"{indent}└── {os.path.basename(root)}/")

        sub_indent = ' ' * 4 * level
        for f in sorted(files):
            if not is_file_excluded(f, exact_exceptions, pattern_exceptions):
                tree_lines.append(f"{sub_indent}└── {f}")
                
    return "\n".join(tree_lines)

def create_tree_markdown(directory: str):
    """
    Crea un archivo Markdown con la estructura de árbol del proyecto.
    """
    # Normalizar la ruta del directorio
    directory = os.path.normpath(directory)
    base_name = os.path.basename(directory)
    
    if not os.path.isdir(directory):
        print(f"Error: {directory} no es un directorio válido")
        return

    exact_exceptions, pattern_exceptions = read_exceptions('exceptions')
    
    output_filename = f"{base_name}_tree.md"
    
    # Asegurarse de que el propio script no procese los archivos que genera
    exact_exceptions.append(output_filename)
    # También es buena idea excluir el propio script
    exact_exceptions.append(os.path.basename(__file__))


    try:
        with open(output_filename, 'w', encoding='utf-8') as output_file:
            print(f"Generando archivo de árbol: {output_filename}")

            tree_structure = generate_tree_structure(directory, exact_exceptions, pattern_exceptions)
            
            header = (
                f"# Proyecto: `{base_name}`\n\n"
                f"## Estructura del Proyecto\n\n"
                f"```\n{tree_structure}\n```\n\n"
            )
            
            output_file.write(header)
            
        print(f"\nProceso completado. Se ha generado el archivo '{output_filename}' con la estructura del directorio.")

    except Exception as e:
        print(f"Ha ocurrido un error inesperado: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python nombre_del_script.py <ruta_del_directorio>")
    else:
        create_tree_markdown(sys.argv[1])
