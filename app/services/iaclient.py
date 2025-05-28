from .prompt_sys_manager import PromptSysManager
from pydantic import BaseModel
from typing import Dict, Optional, List
from openai import OpenAI
import time
import json

class ApiMessage(BaseModel):
    """Modelo para representar un mensaje en la conversación."""
    role: str
    content: str

class ApiResponse(BaseModel):
    """Modelo para representar la respuesta de la API."""
    content_analysis: Optional[str] = None
    content_comment: Optional[str] = None
    content_code: Optional[str] = None
    content_executable_code: Optional[str] = None
    title: Optional[str] = None


class ChatGPTClient:
    """Cliente para interactuar con la API de ChatGPT para generar sentencias ETL."""
    
    def __init__(self, api_key: str, model: str = "o4-mini", prompt_template_path: Optional[str] = None, conversion_history: List[ApiMessage] = [], base_prompt_json: Optional[Dict] = None, max_retries: int = 3, retry_delay: int = 2):
        """
        Inicializa el cliente de ChatGPT.
        
        Args:
            api_key: La clave API de OpenAI
            model: El modelo de OpenAI a utilizar (por defecto: gpt-4)
            prompt_template_path: Ruta opcional al archivo de plantilla de prompt
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.conversation_history = conversion_history
        self.prompt_template_path = prompt_template_path
        self.base_prompt_json = base_prompt_json 
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
    def initialize_conversation(self, scheme: str = None):
        """
        Inicializa la conversación con el prompt del sistema y ejemplos.
        
        Args:
            schema: Esquema de base de datos analizado (opcional)
        """

        if not self.base_prompt_json:
            raise ValueError("There is no prompt template loaded.")

        # Personaliza el prompt si hay un esquema
        prompt_json = self.base_prompt_json

        # Convierte el JSON a texto para el prompt del sistema
        system_prompt = PromptSysManager.json_to_system_prompt(prompt_json)

        if scheme:
            # Si se proporciona un esquema, lo agrega al prompt
            system_prompt += f"\n\nEsquema de base de datos:\n{scheme}"
        
        
        # Agrega el prompt del sistema
        self.conversation_history.insert(0, {
            "role": "system",
            "content": system_prompt
        })

        return self.conversation_history
        
    def send_message(self, message: ApiMessage, title: bool) -> ApiResponse:
        """
        Envía un mensaje a ChatGPT y obtiene la respuesta.
        
        Args:
            message: El mensaje para enviar a ChatGPT
            schema: Esquema de base de datos analizado (opcional)
            
        Returns:
            La respuesta generada por ChatGPT
        """        
        # Agrega el mensaje del usuario a la conversación
        
        content = message.content
        if title:
            content += f"\nAl formato de respuesta agrega el campo 'title', cuyo valor sera una frase muy corta que defina el contexto de la conversacion."
        
        self.conversation_history.append({"role": "user", "content": content })
                
        for attempt in range(self.max_retries):
            try:
                # Usa la biblioteca de OpenAI para hacer la solicitud
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.conversation_history,
                )
                
                # Obtiene la respuesta
                assistant_response = response.choices[0].message.content
                
                # Agrega la respuesta al historial
                self.conversation_history.append({"role": "assistant", "content": assistant_response})


                response_json = json.loads(assistant_response)

                return ApiResponse(
                    content_analysis=response_json.get("analysis"),
                    content_comment=response_json.get("comment"),
                    content_code=response_json.get("code"),
                    content_executable_code=response_json.get("executable_code"),
                    title=response_json.get("title")
                )
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"Error al comunicarse con la API después de {self.max_retries} intentos: {str(e)}")
                
                # Espera con backoff exponencial
                time.sleep(self.retry_delay * (2 ** attempt))
    
    def clear_conversation(self):
        """Limpia el historial de la conversación."""
        self.conversation_history = []
    

