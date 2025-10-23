import os
import sys
import json
from typing import List, Optional, TextIO
import hashlib

def read_exceptions(file: str) -> List[str]:
    try:
        with open(file, 'r') as f:
            return [line.strip() for line in f]
    except FileNotFoundError:
        print(f"Warning: The exceptions file '{file}' was not found.")
        return []

def create_new_file(base_name: str, counter: int) -> tuple:    
    hash_object = hashlib.sha1(f"{base_name}_{counter}".encode('utf-8'))
    hash_5_digits = hash_object.hexdigest()[:5]
    file_name = f'{base_name}_{hash_5_digits}_{counter}.txt'
    return open(file_name, 'w', encoding='utf-8'), counter + 1

def write_content(file: TextIO, content: str, json_info: str, index: int = 0) -> int:
    info = json.loads(json_info)
    info['index'] = index
    updated_json_info = json.dumps(info, ensure_ascii=False)
    file.write(f'"""{updated_json_info}"""\n\n')
    file.write(content)
    return len(content.splitlines()) + 2

def process_directory(directory: str, max_lines: int = 2000):
    base_name = os.path.basename(directory)
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        return

    exceptions = read_exceptions('exceptions')
    file_counter = 1
    current_lines = 0
    current_file: Optional[TextIO] = None
    buffer = []

    try:
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in exceptions]
            
            for file in files:
                if file in exceptions:
                    continue
                
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, directory)
                file_info = json.dumps({"relativePath": relative_path}, ensure_ascii=False)
                
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    lines = content.splitlines()
                    index = 0
                    
                    while lines:
                        available_lines = max(1, max_lines - current_lines)
                        chunk = lines[:available_lines]
                        chunk_content = '\n'.join(chunk) + '\n'
                        buffer.append({'content': chunk_content, 'info': file_info, 'index': index})
                        current_lines += len(chunk) + 2
                        lines = lines[available_lines:]
                        index += 1

                        if current_lines >= max_lines:
                            current_file, file_counter = create_new_file(base_name, file_counter)
                            for item in buffer:
                                write_content(current_file, item['content'], item['info'], item['index'])
                            buffer = []
                            current_lines = 0

                except Exception as e:
                    error_message = f"Error reading file {file}: {e}\n"
                    buffer.append({'content': error_message, 'info': file_info, 'index': 0})
                    current_lines += 1

        # Write remaining buffer
        if buffer:
            current_file, file_counter = create_new_file(base_name, file_counter)
            for item in buffer:
                write_content(current_file, item['content'], item['info'], item['index'])

    finally:
        if current_file:
            current_file.close()

    print(f"Processing completed. {file_counter - 1} {base_name}.txt files have been generated")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide the directory path")
    else:
        process_directory(sys.argv[1])
