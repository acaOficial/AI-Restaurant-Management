import os
import re
import json
import requests
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MCP_BASE = "http://localhost:8000"


def extract_info(user_msg: str):
    """Extrae invitados y ubicación"""
    guests = None
    match = re.search(r"(\d+)\s*(personas|comensales)", user_msg.lower())
    if match:
        guests = int(match.group(1))

    if "terraza" in user_msg.lower():
        location = "terrace"
    elif "interior" in user_msg.lower():
        location = "interior"
    else:
        location = None

    return guests, location


def extract_name(user_msg: str):
    """Extrae nombre si aparece en 'soy X' o 'a nombre de X'"""
    text = user_msg.strip()

    p1 = re.search(r"soy ([A-Za-zÁÉÍÓÚáéíóúñÑ ]+)", text, re.IGNORECASE)
    if p1:
        return p1.group(1).strip()

    p2 = re.search(r"a nombre de ([A-Za-zÁÉÍÓÚáéíóúñÑ ]+)", text, re.IGNORECASE)
    if p2:
        return p2.group(1).strip()

    return None


def receptionist(user_msg: str):

    # Extraer datos básicos
    guests, location = extract_info(user_msg)
    name = extract_name(user_msg)

    # Si faltan datos → pedir
    if not guests or not location or not name:
        return (
            "Para procesar tu reserva necesito:\n"
            "- Nombre (ej: 'Soy Juan Pérez')\n"
            "- Número de personas (ej: '3 personas')\n"
            "- Zona (terraza o interior)\n"
        )

    # Encontrar mesa disponible
    r = requests.get(f"{MCP_BASE}/findTable?guests={guests}&location={location}")
    table = r.json()

    if not table:
        return (
            f"No hay mesas disponibles para {guests} personas en {location}. "
            "¿Deseas interior o cambiar horario?"
        )

    table_id = table[0]["id"]

    # Reservar
    date = "2025-10-29"   # para demo
    time = "20:00"        # para demo

    reserve_resp = requests.post(
        f"{MCP_BASE}/reserveTable",
        params={
            "table_id": table_id,
            "name": name,
            "guests": guests,
            "date": date,
            "time": time,
        },
    )

    if reserve_resp.json().get("success"):
        return (
            f"✅ ¡Reserva confirmada!\n"
            f"Mesa {table_id} para {guests} personas en {location}.\n"
            f"Fecha: {date} a las {time}\n"
            f"A nombre de {name}.\n"
        )

    return "❌ Error al registrar la reserva."
