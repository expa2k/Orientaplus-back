import os
import json
import google.generativeai as genai
from flask import current_app
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    @staticmethod
    def analizar_texto_riasec(texto: str) -> dict:
        """
        Envía texto libre del estudiante a Gemini y pide un JSON exacto con valores RIASEC.
        Utiliza el modelo gemini-1.5-flash para velocidad y precisión estricta.
        """
        # Obtenemos la llave de las variables de entorno o la configuración de Flask
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("CUIDADO: No se encontró la GEMINI_API_KEY guardada en el archivo .env")

        # Inicializar cliente de Gemini
        genai.configure(api_key=api_key)
        
        # Modelo recomendado y rápido
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = f"""
        Actúa como un psicólogo vocacional experto en la teoría de Holland (RIASEC).
        Analiza el siguiente texto escrito por un estudiante de preparatoria sobre sus pasiones, hobbies y cómo se ve en el futuro:
        
        "{texto}"
        
        Tus instrucciones estrictas:
        1. Identifica qué tanta afinidad tiene hacia las 6 áreas: Realista (R), Investigador (I), Artístico (A), Social (S), Emprendedor (E), Convencional (C).
        2. Califica cada letra con un número entero dándole de 0 a 10 puntos a cada una (donde 10 es pasión máxima y 0 es nula).
        3. No uses texto extra. Devuelve ÚNICAMENTE un objeto JSON plano. Sin formato markdown ni backticks. Exactamente con este formato:
        {{
          "R": 5,
          "I": 8,
          "A": 2,
          "S": 3,
          "E": 0,
          "C": 4
        }}
        """

        try:
            # Enviamos el texto a la IA
            response = model.generate_content(prompt)
            
            # Limpieza exhaustiva en caso de que Gemini mande formato Markdown (```json ... ```)
            clean_text = response.text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
            
            # Convertimos la respuesta cruda de texto a un Diccionario en Python
            resultado_json = json.loads(clean_text)
            
            # Validación sencilla: asegurar que devolvió las 6 letras
            for letra in ['R', 'I', 'A', 'S', 'E', 'C']:
                if letra not in resultado_json:
                    resultado_json[letra] = 0
                    
            return resultado_json

        except Exception as e:
            print(f"Error procesando la IA de Gemini: {e}")
            # Si se cae el internet o falla algo, regresamos ceros para no crashear la app.
            return {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}

    @staticmethod
    def predecir_carreras_directas(texto: str, lista_carreras: list) -> list:
        """
        Lee el texto del usuario y selecciona de forma estricta los 3 IDs de las carreras
        que hacen match perfecto (Ej. Si menciona código, elegirá Informática).
        """
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return []

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        carreras_texto = json.dumps(lista_carreras, ensure_ascii=False)

        prompt = f"""
        Actúa como un psicólogo vocacional infalible. Un estudiante escribió esto sobre sus pasiones:
        "{texto}"
        
        Aquí tienes una lista oficial de las carreras universitarias disponibles:
        {carreras_texto}
        
        Tu tarea es seleccionar EXACTAMENTE las 3 carreras que mejor hagan 'match' con ese texto empírico.
        Considera palabras clave (ej. Si habla de tecnología, descarta biología/historia y escoge ciencias computacionales).
        
        DEVUELVE ÚNICAMENTE un arreglo JSON plano con los 3 'id' numéricos de las carreras elegidas.
        Sin formato markdown, sin texto extra.
        Ejemplo estricto: [15, 3, 80]
        """

        try:
            response = model.generate_content(prompt)
            import re
            match = re.search(r'\[.*?\]', response.text, re.DOTALL)
            
            if match:
                lista_ids = json.loads(match.group())
                # Asegurar que es lista de ints
                if isinstance(lista_ids, list):
                    return [int(x) for x in lista_ids[:3]]
            
            return []

        except Exception as e:
            print(f"Error procesando IDs directos en Gemini: {e}")
            return []
