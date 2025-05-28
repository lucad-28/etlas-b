import os
import json
from typing import List, Dict, Optional, Union
import time
from openai import OpenAI
from pathlib import Path

class ETLPromptManager:
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
                    "Si el codigo es en python, recuerda mostrar la tabla de salida con <TABLESTART @nombre de la tabla>funcion print<TABLEEND>)",
                ]
            },
            "response_format": {
                "description": "Estructura tus respuestas en un json_string con analysis, comment, code, executable_code",
                "keys": [
                    {"key": "analysis", "value": "Comprensión del problema o esquema"},
                    {"key": "comment", "value": "Comentarios sobre la resolución propuesta"},
                    {"key": "code", "value": "Implementación en SQL/Python/etc. "},
                    {"key": "executable_code", "value": "Versión ejecutable del código, sin el uso de dependencias externas con servicios como AWS, Azure, GCP, etc., siendo reemplazadas por funciones de python como pandas, numpy, etc. para una simulacion de las tablas resultantes."},
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
    
    @staticmethod
    def get_few_shot_examples() -> List[Dict]:
        """
        Proporciona ejemplos de few-shot learning para mejorar las respuestas.
        
        Returns:
            Lista de mensajes que actúan como ejemplos
        """
        return [
            {
                "role": "user",
                "content": """Tengo estas dos tablas:
                    
                    CREATE TABLE orders (
                        order_id INT PRIMARY KEY,
                        customer_id INT,
                        order_date DATE,
                        total_amount DECIMAL(10,2)
                    );
                    
                    CREATE TABLE order_items (
                        item_id INT PRIMARY KEY,
                        order_id INT,
                        product_id INT,
                        quantity INT,
                        unit_price DECIMAL(10,2)
                    );
                    
                    Necesito un proceso ETL para consolidar pedidos diarios."""
            },
            {
                "role": "assistant",
                "content": """
                # Análisis
                He analizado el esquema proporcionado que consta de dos tablas relacionadas:
                - `orders`: Almacena información general de pedidos
                - `order_items`: Contiene detalles de los productos en cada pedido
                
                La relación es one-to-many (un pedido puede tener múltiples ítems).
                
                # Enfoque
                Para consolidar pedidos diarios, propongo un proceso ETL que:
                1. Extraiga datos de ambas tablas
                2. Transforme agregando por fecha y calculando métricas clave
                3. Cargue en una tabla de resumen diario
                
                # Código
                ```sql
                -- 1. Crear tabla destino
                CREATE TABLE IF NOT EXISTS daily_order_summary (
                    summary_date DATE PRIMARY KEY,
                    total_orders INT,
                    total_revenue DECIMAL(12,2),
                    total_items_sold INT,
                    avg_order_value DECIMAL(10,2)
                );
                
                -- 2. Proceso ETL
                INSERT INTO daily_order_summary
                WITH daily_stats AS (
                    SELECT
                        o.order_date AS summary_date,
                        COUNT(DISTINCT o.order_id) AS total_orders,
                        SUM(o.total_amount) AS total_revenue,
                        SUM(oi.quantity) AS total_items_sold
                    FROM
                        orders o
                    JOIN
                        order_items oi ON o.order_id = oi.order_id
                    WHERE
                        o.order_date = CURRENT_DATE - INTERVAL '1 day'
                    GROUP BY
                        o.order_date
                )
                SELECT
                    summary_date,
                    total_orders,
                    total_revenue,
                    total_items_sold,
                    (total_revenue / NULLIF(total_orders, 0)) AS avg_order_value
                FROM
                    daily_stats;
                ```
                
                # Optimización
                - Añadí índices para mejorar el rendimiento:
                ```sql
                CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
                CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
                ```
                
                # Consideraciones
                - Este proceso debe ejecutarse una vez al día
                - Incluye manejo de divisiones por cero con NULLIF
                - Considera implementar lógica de upsert si necesitas recalcular datos históricos
                - Podrías extender el análisis incluyendo productos más vendidos o segmentación de clientes
                """
            }
        ]
    
    @staticmethod
    def customize_prompt_for_schema(base_prompt_json: Dict, schema: Dict) -> Dict:
        """
        Personaliza el prompt JSON según el esquema proporcionado.
        
        Args:
            base_prompt_json: Prompt base en formato JSON
            schema: Esquema de base de datos analizado
            
        Returns:
            Prompt JSON personalizado para el esquema
        """
        # Crea una copia para no modificar el original
        customized_prompt = json.loads(json.dumps(base_prompt_json))
        
        # Analiza el esquema
        table_count = len(schema.get("tables", []))
        tables_with_pk = sum(1 for table in schema.get("tables", []) 
                            for col in table.get("columns", []) 
                            if col.get("primary_key", False))
        
        # Añade información específica del esquema
        if "schema_context" not in customized_prompt:
            customized_prompt["schema_context"] = {}
        
        customized_prompt["schema_context"].update({
            "table_count": table_count,
            "tables_with_pk": tables_with_pk,
            "tables": [table["name"] for table in schema.get("tables", [])],
            "has_relationships": tables_with_pk > 0
        })
        
        return customized_prompt

class ChatGPTClient:
    """Cliente para interactuar con la API de ChatGPT para generar sentencias ETL."""
    
    def __init__(self, api_key: str, model: str = "o4-mini", prompt_template_path: Optional[str] = None):
        """
        Inicializa el cliente de ChatGPT.
        
        Args:
            api_key: La clave API de OpenAI
            model: El modelo de OpenAI a utilizar (por defecto: gpt-4)
            prompt_template_path: Ruta opcional al archivo de plantilla de prompt
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.conversation_history = []
        self.prompt_template_path = prompt_template_path
        self.base_prompt_json = ETLPromptManager.load_prompt_template(prompt_template_path)
        
    def initialize_conversation(self, schema: Optional[Dict] = None):
        """
        Inicializa la conversación con el prompt del sistema y ejemplos.
        
        Args:
            schema: Esquema de base de datos analizado (opcional)
        """
        # Limpia la conversación anterior
        self.conversation_history = []
        
        # Personaliza el prompt si hay un esquema
        prompt_json = self.base_prompt_json
        if schema:
            prompt_json = ETLPromptManager.customize_prompt_for_schema(self.base_prompt_json, schema)
        
        # Convierte el JSON a texto para el prompt del sistema
        system_prompt = ETLPromptManager.json_to_system_prompt(prompt_json)

        system_prompt = f"""
        {system_prompt}
        
        toma en cuenta el siguiente esquema de base de datos:

        -- Tabla de Autores
CREATE TABLE autores (
    autor_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    fecha_nacimiento DATE,
    nacionalidad VARCHAR(50)
);

-- Tabla de Categorías
CREATE TABLE categorias (
    categoria_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT
);

-- Tabla de Libros
CREATE TABLE libros (
    libro_id INT PRIMARY KEY AUTO_INCREMENT,
    titulo VARCHAR(100) NOT NULL,
    autor_id INT,
    categoria_id INT,
    precio DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    fecha_publicacion DATE,
    FOREIGN KEY (autor_id) REFERENCES autores(autor_id),
    FOREIGN KEY (categoria_id) REFERENCES categorias(categoria_id)
);

-- Tabla de Clientes
CREATE TABLE clientes (
    cliente_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    telefono VARCHAR(20),
    fecha_registro DATE DEFAULT CURRENT_DATE
);

-- Tabla de Ventas
CREATE TABLE ventas (
    venta_id INT PRIMARY KEY AUTO_INCREMENT,
    cliente_id INT,
    fecha_venta DATETIME DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
);

-- Tabla de Detalles de Venta (tabla intermedia)
CREATE TABLE detalle_ventas (
    detalle_id INT PRIMARY KEY AUTO_INCREMENT,
    venta_id INT,
    libro_id INT,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (venta_id) REFERENCES ventas(venta_id),
    FOREIGN KEY (libro_id) REFERENCES libros(libro_id)
);
        """
        
        # Agrega el prompt del sistema
        self.conversation_history.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Agrega ejemplos de few-shot learning
        #self.conversation_history.extend(ETLPromptManager.get_few_shot_examples())
    
    def send_message(self, message: str, schema: Optional[Dict] = None) -> str:
        """
        Envía un mensaje a ChatGPT y obtiene la respuesta.
        
        Args:
            message: El mensaje para enviar a ChatGPT
            schema: Esquema de base de datos analizado (opcional)
            
        Returns:
            La respuesta generada por ChatGPT
        """
        # Inicializa la conversación si es el primer mensaje o si se proporciona un esquema
        if not self.conversation_history:
            self.initialize_conversation()
        
        # Agrega el mensaje del usuario a la conversación
        self.conversation_history.append({"role": "user", "content": message})
        
        # Implementa reintentos con backoff exponencial
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
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
                
                return assistant_response
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Error al comunicarse con la API después de {max_retries} intentos: {str(e)}")
                
                # Espera con backoff exponencial
                time.sleep(retry_delay * (2 ** attempt))
    
    def clear_conversation(self):
        """Limpia el historial de la conversación."""
        self.conversation_history = []

def parse_schema(schema_text: str) -> Dict:
    """
    Función auxiliar para analizar un esquema de base de datos en formato de texto.
    
    Args:
        schema_text: Texto que representa el esquema de la base de datos
        
    Returns:
        Diccionario con el esquema analizado
    """
    # Implementación mejorada del parser
    schema = {"tables": []}
    current_table = None
    in_create_table = False
    
    for line in schema_text.strip().split('\n'):
        line = line.strip()
        
        # Ignora líneas vacías y comentarios
        if not line or line.startswith('--') or line.startswith('#'):
            continue
        
        # Detecta inicio de definición de tabla
        if "CREATE TABLE" in line.upper():
            # Extrae el nombre de la tabla
            table_parts = line.split("CREATE TABLE", 1)[1].strip()
            if "(" in table_parts:
                table_name = table_parts.split("(", 1)[0].strip('` "\';[]')
            else:
                table_name = table_parts.strip('` "\';[]')
            
            current_table = {"name": table_name, "columns": [], "constraints": []}
            in_create_table = True
        
        # Detecta final de definición de tabla
        elif in_create_table and (line.endswith(';') or line.startswith(')')):
            in_create_table = False
            if current_table:
                schema["tables"].append(current_table)
                current_table = None
        
        # Procesa columnas y restricciones
        elif in_create_table and current_table:
            # Elimina comas finales y paréntesis
            clean_line = line.rstrip(',;)')
            
            # Detecta restricciones de tabla
            if any(keyword in clean_line.upper() for keyword in ["CONSTRAINT", "PRIMARY KEY", "FOREIGN KEY", "UNIQUE"]):
                current_table["constraints"].append(clean_line)
            
            # Detecta definiciones de columnas
            elif clean_line and "(" not in clean_line.split()[0]:
                parts = clean_line.split()
                if len(parts) >= 2:
                    column_name = parts[0].strip('`"[]')
                    data_type = parts[1].strip(',;()')
                    
                    column = {"name": column_name, "type": data_type}
                    
                    # Detecta atributos de columna (NULL, NOT NULL, DEFAULT, etc.)
                    remaining = " ".join(parts[2:]).upper()
                    if "PRIMARY KEY" in remaining:
                        column["primary_key"] = True
                    if "NOT NULL" in remaining:
                        column["nullable"] = False
                    if "NULL" in remaining and "NOT NULL" not in remaining:
                        column["nullable"] = True
                    if "DEFAULT" in remaining:
                        default_value = remaining.split("DEFAULT", 1)[1].strip().split()[0].strip(',;')
                        column["default"] = default_value
                    
                    current_table["columns"].append(column)
    
    # Captura la última tabla si no terminaba con punto y coma
    if current_table:
        schema["tables"].append(current_table)
    
    return schema

def create_config_template(output_path: str = "etl_prompt_template.json"):
    """
    Crea un archivo de plantilla de configuración JSON para el prompt del sistema.
    
    Args:
        output_path: Ruta de salida para el archivo de configuración
    """
    config = ETLPromptManager.load_prompt_template()
    
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=2)
    
    print(f"Plantilla de configuración JSON creada en: {output_path}")

def generate_etl_code(api_key: str, schema_or_request: str, prompt_template_path: Optional[str] = None) -> str:
    """
    Función principal para generar código ETL basado en un esquema o solicitud.
    
    Args:
        api_key: La clave API de OpenAI
        schema_or_request: Esquema de base de datos o solicitud en texto
        prompt_template_path: Ruta opcional al archivo de plantilla de prompt
        
    Returns:
        Código ETL generado
    """
    client = ChatGPTClient(api_key, prompt_template_path=prompt_template_path)
    
    prompt = f"""

{prompt}
\n\n"""
    # Obtiene la respuesta
    response = client.send_message(prompt, schema=parsed_schema)
    return response

def interactive_etl_assistant(api_key: str, prompt_template_path: Optional[str] = None):
    """
    Ejecuta un asistente interactivo de ETL en la consola.
    
    Args:
        api_key: La clave API de OpenAI
        prompt_template_path: Ruta opcional al archivo de plantilla de prompt
    """
    client = ChatGPTClient(api_key, prompt_template_path=prompt_template_path)
    
    print("=== Asistente ETL con ChatGPT ===")
    print("Comandos disponibles:")
    print("  'salir' - Terminar la sesión")
    print("  'nueva' - Iniciar una nueva conversación")
    print("  'config' - Crear una plantilla de configuración JSON")
    print("\nPuedes proporcionar un esquema de BD o simplemente hacer preguntas sobre ETL.")
    
    while True:
        user_input = input("> ")
        
        if user_input.lower() == 'salir':
            break
        elif user_input.lower() == 'nueva':
            client.clear_conversation()
            print("Nueva conversación iniciada.")
            continue
        elif user_input.lower() == 'config':
            config_path = input("Nombre del archivo de configuración (default: etl_prompt_template.json): ")
            if not config_path:
                config_path = "etl_prompt_template.json"
            create_config_template(config_path)
            continue
        try:
            # Intenta analizar como esquema
            parsed_schema = None
            try:
                parsed_schema = parse_schema(user_input)
                if not parsed_schema["tables"]:
                    parsed_schema = None
            except:
                parsed_schema = None
                
            # Envía el mensaje y muestra la respuesta
            response = client.send_message(user_input, schema=parsed_schema)
            print(f"\n{response}")
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    # Obtiene la clave API desde una variable de entorno por seguridad
    api_key = os.environ.get("OPENAI_API_KEY")
    
    # Obtiene la ruta de la plantilla de prompt (si existe)
    default_template_path = "etl_prompt_template.json"
    prompt_template_path = None
    
    if Path(default_template_path).exists():
        prompt_template_path = default_template_path
        print(f"Usando plantilla de prompt JSON: {default_template_path}")
    
    if not api_key:
        api_key = input("Introduce tu clave API de OpenAI: ")
    
    interactive_etl_assistant(api_key, prompt_template_path)