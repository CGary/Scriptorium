import os
import google.generativeai as genai
from typing import Optional

class GeminiAPI:
    def __init__(self, api_key: Optional[str] = None, 
                 modelo: str = "gemini-1.5-flash",
                 usar_grpc: bool = False):
        # Configurar entorno antes de inicializar
        os.environ["GRPC_VERBOSITY"] = "ERROR"
        os.environ["GLOG_minloglevel"] = "2"
        os.environ["GOOGLE_API_KEY"] = api_key or 'AIzaSyAXcnyAj85MNy0JK_48PyMatl4gjgu1E8c'
        
        self.modelo = modelo
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        
        if not self.api_key:
            raise ValueError("API key requerida")
            
        # Configurar transporte
        config = {"transport": "grpc" if usar_grpc else "rest"}
        genai.configure(api_key=self.api_key, **config)

    def generar_texto(self, prompt: str, **params) -> str:
        try:
            model = genai.GenerativeModel(self.modelo)
            response = model.generate_content(prompt, **params)
            return response.text
        except Exception as e:
            raise RuntimeError(f"Error en generación: {str(e)}") from e

    @staticmethod
    def listar_modelos():
        return [m.name for m in genai.list_models()]

# Uso básico de la librería
if __name__ == "__main__":
    # Ejemplo de implementación
    try:
        gemini = GeminiAPI()
        # print("Modelos disponibles:", gemini.listar_modelos_disponibles())
        print(gemini.generar_texto("Haz un resumen sobre Python", temperature=0.1))
    except Exception as e:
        print(f"Error: {str(e)}")