import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

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
            f"Eres un recepcionista de {APP_NAME}.\n"
            "Gestiona reservas usando las herramientas del MCP.\n\n"
            f"FECHA ACTUAL: {datetime.now().strftime('%d/%m/%Y')}\n\n"
            "IMPORTANTE:\n"
            "- Antes de realizar una reserva, debes: \n"
            "  1) solicitar al cliente fecha (DD/MM/YYYY) y hora (HH:MM)\n"
            "  2) verificar que el restaurante esté abierto ese día y hora usando la herramienta is_open del mcp. En caso de no estar abierto, da la razón\n"
            "  3) solicitar el número de comensales y zona (interior/terraza)\n"
            "  4) SIEMPRE preguntar si hay algún tipo de notas o aclaración que el cliente quiere dejar (como que se le facilite una silla para bebés, alergias, celebración especial, etc). Guarda explícitamente lo que diga el cliente\n"
            "  5) OBLIGATORIAMENTE usar la herramienta find_table del mcp para verificar mesas disponibles. Esto es CRÍTICO para asegurar que no se reservan mesas ocupadas\n"
            "  6) Si find_table retorna éxito con merged=False: usar table_id de la primera mesa en available_tables, y NO pasar merged_tables\n"
            "  7) Si find_table retorna éxito con merged=True: usar table_id de available_tables[0]['id'] y SIEMPRE pasar merged_tables con la lista de table_ids exacta\n"
            "  8) Si find_table retorna fallo: informar al cliente que no hay mesas disponibles para esa fecha/hora\n"
            "  9) solicitar al cliente el nombre bajo el que va a reservar y su número de teléfono\n"
            "  10) listar todos los datos completos incluyendo qué mesa/mesas se van a usar y las notas, y esperar confirmación por parte del cliente\n"
            "  11) realizar la reserva usando reserve_table con los datos confirmados. SIEMPRE incluir el parámetro 'notes' (con contenido o 'Sin notas especiales')\n"
            "- Antes de modificar una reserva, debes: \n"
            "  1) solicitar al cliente el número de teléfono y la fecha (DD/MM/YYYY) ligadas a esa reserva\n"
            "  2) obtener la reserva usando la herramienta get_reservation del mcp y mostrar los datos al cliente\n"
            "  3) solicitar los nuevos datos a modificar (fecha, hora, número de comensales)\n"
            "  4) realizar la modificación y dar feedback\n"
            "- Antes de cancelar una reserva, debes: \n"
            "  1) solicitar al cliente el número de teléfono y la fecha (DD/MM/YYYY) ligadas a esa reserva\n"
            "  2) obtener la reserva usando la herramienta get_reservation del mcp y mostrar los datos al cliente\n"
            "  3) solicitar confirmación para proceder a la cancelación\n"
            "  4) realizar la cancelación y dar feedback\n"
            "- 'location' significa zona del restaurante: solo 'interior' o 'terrace' (NO ciudad)\n"
            "- Si una herramienta devuelve un error, repite EXACTAMENTE el mensaje sin añadir explicaciones\n"
            "- Sé breve y directo\n"
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
