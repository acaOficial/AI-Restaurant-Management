import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

tools = [
    {
        "type": "mcp",
        "server_label": "restaurant_mcp",
        "server_description": "Servidor MCP para reservas en restaurante",
        "server_url": "https://superimproved-mandy-nondiametral.ngrok-free.dev/mcp",
        "require_approval": "never",
    }
]

messages = [
    {
        "role": "system",
        "content": (
            "Eres un recepcionista de restaurante. "
            "Usa las herramientas del MCP para buscar y crear reservas. "
            "Si falta información (nombre, personas, zona, fecha, hora o teléfono), pídesela al cliente. "
            "Cuando la reserva esté confirmada, despídete con un mensaje amable como "
            "'¿Puedo ayudarte con algo más?' o 'Gracias por tu reserva, ¡te esperamos!'. "
            "Si el cliente indica que no necesita nada más, finaliza la conversación con un agradecimiento."
        ),
    }
]

print("=== Chat con el recepcionista ===\n")

while True:
    user_message = input("👤 Tú: ").strip()
    if not user_message:
        continue

    messages.append({"role": "user", "content": user_message})

    response = client.responses.create(
        model="gpt-5",
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
