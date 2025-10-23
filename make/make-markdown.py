import os
import sys
import random
import string
import fnmatch # Importado para el manejo de patrones
from typing import List, Optional, TextIO, Tuple # 'Tuple' añadido
from datetime import datetime

def get_language_from_extension(file_name: str) -> str:
    """
    Busca el lenguaje de programación basado en la extensión del archivo.
    Esta versión maneja correctamente los "dotfiles" (ej. .dockerignore).
    Si la extensión no se encuentra, lanza un error de tipo ValueError.
    """
    extension_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".java": "java",
        ".c": "c",
        ".cpp": "cpp",
        ".cs": "csharp",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php",
        ".html": "html",
        ".css": "css",
        ".scss": "scss",
        ".sql": "sql",
        ".json": "json",
        ".xml": "xml",
        ".md": "markdown",
        ".sh": "shell",
        ".bat": "batch",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".dockerignore": "dockerignore",
        ".prettierrc": "json",
        "":"",
        ".lock": "jsonc",
        ".gitkeep": "plaintext",
        ".svg": "svg",
        ".txt": "plaintext",
        ".svelte": "svelte",
        ".editorconfig": "ini",
        ".envrc": "shell",
        ".nvmrc": "text",
        ".python-version": "text",
        ".mjs": "javascript",
        ".toml": "toml",
        ".mermaid": "mermaid",
        ".empty": "text",
        ".cjs": "javascript",
        ".tsx": ".tsx",
        ".cfg": "ini",
        ".example": ".env",
        ".env": ".env",
        ".ini": "ini",
        ".webmanifest": "json",
        ".flow": "javascript",
    }

    base, ext = os.path.splitext(file_name)
    extension_to_check = base if not ext and base.startswith('.') else ext

    if extension_to_check in extension_map:
        return extension_map[extension_to_check]
    else:
        error_message = (
            f"\n--- ERROR: Extensión de archivo no reconocida: '{extension_to_check}' ---\n"
            f"El script se ha detenido. Para continuar, necesita informar al script cómo manejar este tipo de archivo.\n\n"
            f"Por favor, edite este script y agregue la siguiente línea al diccionario 'extension_map' en la función 'get_language_from_extension':\n\n"
            f'    "{extension_to_check}": "nombre_del_lenguaje",\n\n'
            f"Reemplace \"nombre_del_lenguaje\" con el identificador correcto (ej. \"dockerignore\", \"plaintext\", etc.).\n"
            f"Después de guardar el cambio, puede volver a ejecutar el script.\n"
        )
        raise ValueError(error_message)


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
    for root, dirs, files in os.walk(directory):
        # La exclusión de directorios solo se aplica a nombres exactos
        dirs[:] = [d for d in dirs if d not in exact_exceptions]

        level = root.replace(directory, '').count(os.sep)
        indent = ' ' * 4 * level
        tree_lines.append(f"{indent}{os.path.basename(root)}/")

        sub_indent = ' ' * 4 * (level + 1)
        for f in sorted(files):
            # La exclusión de archivos considera nombres exactos y patrones
            if not is_file_excluded(f, exact_exceptions, pattern_exceptions):
                tree_lines.append(f"{sub_indent}{f}")
    return "\n".join(tree_lines)

def process_directory(directory: str, max_lines: int = 50000):
    """
    Procesa un directorio, creando archivos Markdown semánticos con la estructura del proyecto,
    metadatos y el contenido completo de los archivos.
    """
    base_name = os.path.basename(directory)
    if not os.path.isdir(directory):
        print(f"Error: {directory} no es un directorio válido")
        return

    exact_exceptions, pattern_exceptions = read_exceptions('exceptions')

    output_file: Optional[TextIO] = None
    part_counter = 1
    current_lines = 0
    generated_files = []

    def create_new_part_file():
        nonlocal output_file, part_counter, current_lines
        if output_file:
            output_file.close()

        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        file_name = f"{base_name}_{random_suffix}.md"
        generated_files.append(file_name)
        # Asegurarse de que el propio script no procese los archivos que genera
        exact_exceptions.append(file_name)


        output_file = open(file_name, 'w', encoding='utf-8')
        print(f"Generando nuevo archivo: {file_name}")
        part_counter += 1
        current_lines = 0

    try:
        create_new_part_file()

        tree_structure = generate_tree_structure(directory, exact_exceptions, pattern_exceptions)
        header = (
            f"# Project: `{base_name}`\n\n"
            f"## Project Structure\n\n"
            f"```\n{tree_structure}\n```\n\n"
            f"---\n\n"
        )
        output_file.write(header)
        current_lines += header.count('\n')

        for root, dirs, files in os.walk(directory):
            # Excluir directorios por nombre exacto
            dirs[:] = [d for d in dirs if d not in exact_exceptions]

            for file_name in sorted(files):
                if is_file_excluded(file_name, exact_exceptions, pattern_exceptions):
                    continue

                full_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(full_path, directory)

                language = get_language_from_extension(file_name)

                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                stats = os.stat(full_path)
                
                file_header = (
                    f"## File: `{relative_path}`\n\n"
                    f"Metadata:\n"
                    f"- Size: {stats.st_size} bytes\n"
                    f"- Last Modified: {datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    f"Content:\n\n"
                )

                if language == "markdown":
                    file_content_block = f"{content}\n\n"
                else:
                    file_content_block = (
                        f"```{language}\n"
                        f"{content}\n"
                        f"```\n\n"
                    )
                
                file_block = (
                    f"{file_header}"
                    f"{file_content_block}"
                    f"---\n\n"
                )

                block_line_count = file_block.count('\n')

                if current_lines + block_line_count > max_lines and current_lines > 0:
                    create_new_part_file()
                    new_part_header = (
                        f"# Project: `{base_name}` (Part {part_counter - 1})\n\n"
                        f"## File Contents (Continued)\n\n"
                        f"---\n\n"
                    )
                    output_file.write(new_part_header)
                    current_lines += new_part_header.count('\n')

                output_file.write(file_block)
                current_lines += block_line_count

    except ValueError as e:
        print(str(e))

        if output_file and not output_file.closed:
            file_path_to_remove = output_file.name
            output_file.close()
            os.remove(file_path_to_remove)
            print(f"Se ha eliminado el archivo incompleto: {file_path_to_remove}")
        return

    except Exception as e:
        print(f"Ha ocurrido un error inesperado: {e}")
        return

    finally:
        if output_file and not output_file.closed:
            output_file.close()

    print(f"\nProceso completado. Se generaron {part_counter - 1} archivo(s) Markdown para '{base_name}'.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python make_markdown.py <ruta_del_directorio>")
    else:
        process_directory(sys.argv[1])