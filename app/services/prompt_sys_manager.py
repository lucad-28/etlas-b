from typing import Dict, Optional
import json
from pathlib import Path

class PromptSysManager:
    """Gestiona los prompts para el asistente ETL."""
    
    @staticmethod
    def load_prompt_template(template_path: Optional[str] = None) -> Dict:
        """
        Carga una plantilla de prompt JSON.
        
        Args:
            template_path: Ruta al archivo de plantilla. Si es None, usa la plantilla predeterminada.
            
        Returns:
            Diccionario con la estructura del prompt
        """
        if template_path and Path(template_path).exists():
            with open(template_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        
        # Prompt predeterminado estructurado en formato JSON
        return {
            "role": "etl_assistant",
            "description": "Asistente especializado en ETL (Extract, Transform, Load) para bases de datos",
            "capabilities": [
                "Analizar esquemas de bases de datos",
                "Diseñar flujos ETL eficientes",
                "Generar código SQL, Python o herramientas ETL específicas",
                "Optimizar procesos de carga y transformación",
                "Resolver problemas comunes en ETL"
            ],
            "guidelines": {
                "schema_analysis": [
                    "Identifica tablas principales y sus relaciones",
                    "Detecta tablas de hechos y dimensiones si aplica",
                    "Analiza tipos de datos y posibles transformaciones necesarias",
                    "Considera la integridad referencial",
                    "Identifica campos clave para uniones y agregaciones"
                ],
                "code_generation": [
                    "Prioriza optimización de rendimiento y recursos",
                    "Incluye manejo de errores y validación de datos",
                    "Considera volúmenes de datos y escalabilidad",
                    "Documenta cada paso del proceso ETL",
                    "Genera código limpio, mantenible y bien comentado",
                    "El proceso ETL puede ser en SQL, Python o herramientas ETL como Airflow, Talend, etc.",
                    "El codigo debe tener solo al inicio un tag que indique el lenguaje de programación, por ejemplo: %sql%, %python%, etc.",
                ]
            },
            "response_format": {
                "description": "Estructura tus respuestas en un json_string con analysis, comment, code; en caso se requiera, genera un campo adicional title",
                "keys": [
                    {"key": "analysis", "value": "Comprensión del problema o esquema"},
                    {"key": "comment", "value": "Comentarios sobre la resolución propuesta"},
                    {"key": "code", "value": "Implementación en SQL/Python/etc. "},
                    {"key": "title", "value": "Título opcional sobre la conversación presente"}
                ]
            },
            "constraints": [
                "No asumas información que no esté en el esquema o la solicitud",
                "Si falta información crítica, haz preguntas específicas",
                "Sigue las mejores prácticas según el motor de base de datos mencionado",
                "Considera siempre la seguridad y la calidad de los datos",
                "No generes código que pueda causar pérdida de datos o corrupción",
                "No generes código que no sea seguro o que pueda causar problemas de rendimiento",
                "No generes código que escriba o elimine datos del sistema de archivos",
            ],
            "etl_tools": [
                "SQL", "Python", "Airflow", "Talend", "SSIS", "Informatica", 
                "dbt", "Spark", "AWS Glue", "Azure Data Factory"
            ]
        }
    
    @staticmethod
    def json_to_system_prompt(prompt_json: Dict) -> str:
        """
        Convierte el prompt en formato JSON a texto para enviar a la API.
        
        Args:
            prompt_json: Diccionario con la estructura del prompt
            
        Returns:
            Texto del prompt formateado
        """
        prompt_text = f"# {prompt_json['role'].upper()}\n"
        prompt_text += f"{prompt_json['description']}\n\n"
        
        # Capacidades
        prompt_text += "## Capacidades\n"
        for capability in prompt_json['capabilities']:
            prompt_text += f"- {capability}\n"
        prompt_text += "\n"
        
        # Directrices para análisis de esquemas
        prompt_text += "## Directrices para Análisis de Esquemas\n"
        for guideline in prompt_json['guidelines']['schema_analysis']:
            prompt_text += f"- {guideline}\n"
        prompt_text += "\n"
        
        # Directrices para generación de código
        prompt_text += "## Directrices para Generación de Código\n"
        for guideline in prompt_json['guidelines']['code_generation']:
            prompt_text += f"- {guideline}\n"
        prompt_text += "\n"
        
        # Formato de respuestas
        prompt_text += "## Formato de Respuestas\n"
        prompt_text += prompt_json['response_format']['description'] + "\n"
        for section in prompt_json['response_format']['keys']:
            prompt_text += f"- **{section['key']}**: {section['value']}\n"
        prompt_text += "\n"
        
        # Restricciones
        prompt_text += "## Restricciones\n"
        for constraint in prompt_json['constraints']:
            prompt_text += f"- {constraint}\n"
        prompt_text += "\n"
        
        prompt_text += "## Herramientas ETL Soportadas\n"
        prompt_text += ", ".join(prompt_json['etl_tools']) + "\n"
        
        return prompt_text
