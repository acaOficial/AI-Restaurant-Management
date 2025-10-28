import os
import json
from openai import OpenAI
import requests
from datetime import date

MCP_BASE = "http://localhost:8000"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_from_llm(user_msg: str):
    """
    Usa GPT para extraer datos estructurados desde un mensaje de cliente.
    """
    prompt = f"""
    Analiza el siguiente mensaje de un cliente que desea hacer una reserva en un restaurante.
    Devuelve ÚNICAMENTE un JSON con los siguientes campos (sin texto adicional):

    - name: nombre completo del cliente (string o null)
    - guests: número de personas (entero o null)
    - location: 'interior', 'terraza' o null
    - date: fecha de la reserva (YYYY-MM-DD o null)
    - time: hora de la reserva (HH:MM o null)

    Mensaje del cliente:
    \"\"\"{user_msg}\"\"\"
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres un asistente que convierte texto en JSON estructurado."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )
    print("LLM response:", response.choices[0].message.content)

    return json.loads(response.choices[0].message.content)


def receptionist(user_msg: str):
    """
    Usa el LLM para extraer información y luego llama a la MCP (API) para hacer la reserva.
    """

    data = extract_from_llm(user_msg)

    name = data.get("name")
    guests = data.get("guests")
    location = data.get("location")
    date_str = data.get("date") or str(date.today())
    time = data.get("time") or "20:00"

    if not all([name, guests, location]):
        return (
            "Necesito algunos datos para confirmar tu reserva:\n"
            "- Nombre\n- Número de personas\n- Zona (interior o terraza)\n"
            "Por favor, proporciónalos todos en un solo mensaje."
        )

    # Buscar mesa
    r = requests.get(f"{MCP_BASE}/findTable", params={"guests": guests, "location": location})
    table = r.json()

    if not table:
        return f"No hay mesas disponibles para {guests} personas en {location}."

    table_id = table[0]["id"]

    # Reservar
    reserve_resp = requests.post(
        f"{MCP_BASE}/reserveTable",
        params={
            "table_id": table_id,
            "name": name,
            "guests": guests,
            "date": date_str,
            "time": time,
        },
    )

    if reserve_resp.json().get("success"):
        return (
            f"✅ ¡Reserva confirmada!\n"
            f"Mesa {table_id} para {guests} personas en {location}.\n"
            f"Fecha: {date_str} a las {time}\n"
            f"A nombre de {name}."
        )

    return "❌ Error al registrar la reserva."
