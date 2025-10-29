import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

tools = [
    {
        "type": "mcp",
        "server_label": "restaurant_mcp",
        "server_description": "Servidor MCP para reservas en restaurante",
        "server_url": "https://superimproved-mandy-nondiametral.ngrok-free.dev/mcp",
        "require_approval": "never",
    }
]

user_message = "Hola, soy Ana. Queremos reservar una mesa para 4 personas en interior mañana a las 23:00."

print("Enviando mensaje al modelo...\n")

response = client.responses.create(
    model="gpt-5",
    tools=tools,
    input=[{"role": "user", "content": user_message}],
    instructions=(
        "Eres un recepcionista de restaurante. "
        "Usa las herramientas del MCP para encontrar una mesa y reservarla. "
        "Si falta información (nombre, personas o zona), pídesela al cliente."
    ),
)

print("Respuesta del modelo:\n")
print(response.output_text)
