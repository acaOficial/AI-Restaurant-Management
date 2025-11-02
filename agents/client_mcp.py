import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Cargar configuración desde .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")
MCP_SERVER_NAME = os.getenv("MCP_SERVER_NAME", "booking-mcp")
APP_NAME = os.getenv("APP_NAME", "AI Booking System")

client = OpenAI(api_key=OPENAI_API_KEY)

tools = [
    {
        "type": "mcp",
        "server_label": MCP_SERVER_NAME,
        "server_description": f"Servidor MCP para {APP_NAME}",
        "server_url": MCP_SERVER_URL,
        "require_approval": "never",
    }
]

messages = [
    {
        "role": "system",
        "content": (
            f"Eres un recepcionista de {APP_NAME}. "
            "Gestiona reservas usando las herramientas del MCP.\n\n"
            "IMPORTANTE:\n"
            "- 'location' significa zona del restaurante: solo 'interior' o 'terrace'\n"
            "- NO es ubicación geográfica, NO preguntes por ciudad\n"
            "- Pide: nombre, teléfono, personas, zona (interior/terraza), fecha (DD/MM/YYYY) y hora (HH:MM)\n"
            "- Sé amable y confirma la reserva antes de despedirte"
        ),
    }
]

print(f"=== {APP_NAME} - Chat de Reservas ===\n")

while True:
    user_message = input("👤 Tú: ").strip()
    if not user_message:
        continue

    messages.append({"role": "user", "content": user_message})

    response = client.responses.create(
        model=OPENAI_MODEL,
        tools=tools,
        input=messages,
    )

    assistant_reply = response.output_text.strip()
    print(f"\n🤖 Recepcionista: {assistant_reply}\n")


    messages.append({"role": "assistant", "content": assistant_reply})

    if any(
        phrase in assistant_reply.lower()
        for phrase in [
            "gracias por tu reserva",
            "gracias por su reserva",
            "que tengas un buen día",
            "te esperamos",
        ]
    ):
        print("[DEBUG] Conversación finalizada automáticamente.")
        break
