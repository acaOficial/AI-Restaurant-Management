from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
from core.domain.booking_date import BookingDate
from core.domain.reservation import Reservation
from core.domain.calendar_repository import CalendarRepository
from core.utils.reservation_utils import estimate_duration


class BookingService:
    """
    Capa de aplicación que coordina la lógica de reservas.
    Orquesta las entidades del dominio y los repositorios de infraestructura.
    """

    def __init__(self, reservation_repo, table_repo, holiday_repo, calendar_repo: Optional[CalendarRepository] = None):
        self.reservation_repo = reservation_repo
        self.table_repo = table_repo
        self.holiday_repo = holiday_repo
        self.calendar_repo = calendar_repo
    
    # ============================================================
    # CREAR RESERVA
    # ============================================================
    def create_reservation(
        self, 
        table_id: int, 
        name: str, 
        guests: int, 
        date: str, 
        time: str, 
        phone: str, 
        notes: Optional[str] = None,
        merged_tables: Optional[List[int]] = None
    ):
        """
        Crea una reserva. Puede ser para una mesa individual o mesas combinadas.
        
        Args:
            table_id: ID de la mesa principal
            merged_tables: Lista de IDs si son mesas combinadas (ej: [1, 2, 3])
        """
        booking_date = BookingDate(date, time, self.holiday_repo)
        normalized = booking_date.normalized_date()
        
        existing = self.reservation_repo.find_by_phone_and_date(phone, normalized)
        if existing:
            return {"success": False, "message": f"Ya existe una reserva registrada con el número {phone} para el {normalized}."}

        duration = estimate_duration(guests, time)
        
        # Si hay mesas combinadas, verificar que todas sean de la misma ubicación y tengan capacidad suficiente
        if merged_tables:
            locations = []
            total_capacity = 0
            for tid in merged_tables:
                table_info = self.table_repo.get_table_by_id(tid)
                if not table_info:
                    return {"success": False, "message": f"La mesa {tid} no existe."}
                locations.append(table_info["location"])
                total_capacity += table_info["capacity"]
            
            # Verificar que todas las mesas sean de la misma ubicación
            if len(set(locations)) > 1:
                return {"success": False, "message": f"No se pueden combinar mesas de diferentes ubicaciones (interior/terraza)."}
            
            # Verificar capacidad combinada
            if total_capacity < guests:
                return {"success": False, "message": f"La capacidad total de las mesas combinadas ({total_capacity}) es insuficiente para {guests} personas."}
        else:
            # Si es una mesa individual, verificar que tenga capacidad suficiente
            table_info = self.table_repo.get_table_by_id(table_id)
            if not table_info:
                return {"success": False, "message": f"La mesa {table_id} no existe."}
            if table_info["capacity"] < guests:
                return {"success": False, "message": f"La mesa {table_id} tiene capacidad para {table_info['capacity']} personas, pero se solicitan {guests}. Usa find_table para buscar mesas disponibles."}
        
        # Verificar disponibilidad de todas las mesas (individual o combinadas)
        tables_to_check = merged_tables if merged_tables else [table_id]
        for tid in tables_to_check:
            if not self.table_repo.is_table_available(tid, normalized, time, duration):
                return {"success": False, "message": f"La mesa {tid} no está disponible a las {time} el {normalized}."}

        # Crear evento en Google Calendar si está configurado
        calendar_event_id = None
        if self.calendar_repo:
            table_info = f"mesas {merged_tables}" if merged_tables else f"mesa {table_id}"
            calendar_event_id = self._create_calendar_event(name, guests, normalized, time, duration, phone, table_info)
        
        # Convertir lista de mesas a JSON si existe
        merged_tables_json = json.dumps(merged_tables) if merged_tables else None
        
        # Crear reserva
        reservation = Reservation(
            table_id=table_id,
            name=name,
            guests=guests,
            date=normalized,
            time=time,
            phone=phone,
            duration=duration,
            notes=notes,
            calendar_event_id=calendar_event_id,
            merged_tables=merged_tables_json
        )
        self.reservation_repo.insert(reservation)
        
        # Mensaje de confirmación
        if merged_tables:
            table_msg = f"mesas combinadas {merged_tables}"
        else:
            table_msg = f"mesa {table_id}"
        
        message = f"Reserva creada con éxito para {table_msg} (duración estimada: {duration} min)."
        if calendar_event_id:
            message += " Evento sincronizado con Google Calendar."
        
        return {
            "success": True,
            "message": message,
            "table_id": table_id,
            "merged_tables": merged_tables,
            "duration": duration,
            "calendar_event_id": calendar_event_id
        }

    # ============================================================
    # OBTENER UNA RESERVA
    # ============================================================
    def get_reservation(self, phone: str, date: str):
        date = BookingDate(date, "00:00", self.holiday_repo).normalized_date()
        reservation = self.reservation_repo.find_by_phone_and_date(phone, date)
        if not reservation:
            return {"success": False, "message": f"No existe ninguna reserva con el número {phone} para el {date}."}
        return {"success": True, "reservation": reservation[0]}

    # ============================================================
    # CANCELAR RESERVA
    # ============================================================
    def cancel_reservation(self, phone: str, date: str):
        date = BookingDate(date, "00:00", self.holiday_repo).normalized_date()
        existing = self.reservation_repo.find_by_phone_and_date(phone, date)
        if not existing:
            return {"success": False, "message": f"No existe ninguna reserva con el número {phone} para el {date}."}
        
        # Eliminar evento de Google Calendar si existe
        reservation = existing[0]
        if self.calendar_repo and reservation.get("calendar_event_id"):
            self.calendar_repo.delete_event(reservation["calendar_event_id"])
        
        self.reservation_repo.delete_by_phone_and_date(phone, date)
        return {"success": True, "message": f"Reserva eliminada con éxito para el {date} y número {phone}."}

    # ============================================================
    # MODIFICAR RESERVA
    # ============================================================
    def modify_reservation(self, phone: str, date: str, updates: dict):
        """Modifica una reserva existente. Si cambia el número de comensales, busca una mesa óptima."""
        # Normalizar la fecha de búsqueda
        date = BookingDate(date, "00:00", self.holiday_repo).normalized_date()
        existing = self.reservation_repo.find_by_phone_and_date(phone, date)
        if not existing:
            return {"success": False, "message": f"No existe una reserva con el número {phone} para el {date}."}
        
        reservation = existing[0]
        
        # Normalizar la nueva fecha en updates si existe
        if "date" in updates:
            updates["date"] = BookingDate(updates["date"], "00:00", self.holiday_repo).normalized_date()
        
        # Si cambia el número de comensales, buscar mesa óptima
        if "guests" in updates:
            new_guests = updates["guests"]
            old_guests = reservation["guests"]
            
            if new_guests != old_guests:
                # Solo reasignar mesa si HAY MÁS comensales
                if new_guests > old_guests:
                    # Verificar si la mesa actual es suficiente para más personas
                    current_table = self.table_repo.get_table_by_id(reservation["table_id"])
                    if not current_table:
                        return {"success": False, "message": "Error: la mesa actual no existe."}
                    
                    # Si la mesa actual NO es suficiente, buscar una mejor
                    if current_table["capacity"] < new_guests:
                        # Obtener información de la reserva actual
                        current_time = reservation["time"]
                        current_date = reservation["date"]
                        
                        # Calcular duración para los nuevos comensales
                        duration = estimate_duration(new_guests, current_time)
                        
                        location = current_table["location"]
                        
                        # Buscar mesa óptima para los nuevos comensales
                        new_table_info = self._find_optimal_table(new_guests, location, current_date, current_time, duration, reservation["table_id"])
                        
                        if new_table_info["status"] == "single":
                            # Hay una mesa individual disponible
                            updates["table_id"] = new_table_info["table_id"]
                            updates["merged_tables"] = None
                            mesa_msg = f"Se reasignó a la mesa {new_table_info['table_id']}"
                        elif new_table_info["status"] == "merged":
                            # Hay que combinar mesas
                            updates["table_id"] = new_table_info["table_ids"][0]
                            updates["merged_tables"] = json.dumps(new_table_info["table_ids"])
                            mesa_msg = f"Se reasignó a las mesas combinadas {new_table_info['table_ids']}"
                        else:
                            # No hay mesas disponibles
                            return {"success": False, "message": f"No hay mesas disponibles en {location} para {new_guests} personas en esa fecha y hora."}
                    else:
                        # La mesa actual es suficiente, no reasignar
                        mesa_msg = ""
                else:
                    # Si disminuyen los comensales, mantener la misma mesa
                    mesa_msg = ""
            else:
                mesa_msg = ""
        else:
            mesa_msg = ""
        
        # Actualizar evento en Google Calendar si existe
        if self.calendar_repo and reservation.get("calendar_event_id"):
            self._update_calendar_event(
                reservation["calendar_event_id"],
                reservation,
                updates
            )
        
        self.reservation_repo.update(phone, date, updates)
        msg = f"Reserva modificada con éxito."
        if mesa_msg:
            msg += f" {mesa_msg}."
        
        return {"success": True, "message": msg}
    
    # ============================================================
    # MÉTODO PRIVADO: BUSCAR MESA ÓPTIMA
    # ============================================================
    def _find_optimal_table(
        self, 
        guests: int, 
        location: str, 
        date: str, 
        time: str, 
        duration: int,
        exclude_table_id: int = None
    ) -> dict:
        """
        Busca la mesa óptima para los comensales.
        Primero busca una mesa individual, si no hay, intenta combinar.
        Excluye la mesa actual (exclude_table_id) de la búsqueda.
        
        Returns:
            {
                "status": "single|merged|unavailable",
                "table_id": id (si single),
                "table_ids": [ids] (si merged)
            }
        """
        # 1. Buscar mesa individual
        candidate_tables = self.table_repo.find_by_location_and_capacity(location, guests)
        
        available_tables = []
        for table in candidate_tables:
            # Excluir la mesa actual
            if exclude_table_id and table["id"] == exclude_table_id:
                continue
            
            if self.table_repo.is_table_available(table["id"], date, time, duration):
                available_tables.append(table)
        
        if available_tables:
            # Retornar la primera mesa disponible (la más pequeña que cabe)
            return {
                "status": "single",
                "table_id": available_tables[0]["id"]
            }
        
        # 2. Si no hay mesa individual, buscar combinación de mesas
        all_tables = self.table_repo.find_by_location_and_capacity(location, 1)
        
        available_for_merge = []
        for table in all_tables:
            # Excluir la mesa actual
            if exclude_table_id and table["id"] == exclude_table_id:
                continue
            
            if self.table_repo.is_table_available(table["id"], date, time, duration):
                available_for_merge.append(table)
        
        if not available_for_merge:
            return {"status": "unavailable"}
        
        # Buscar mejor combinación
        best_combination = self._find_best_combination_for_merge(available_for_merge, guests)
        
        if best_combination:
            return {
                "status": "merged",
                "table_ids": [t["id"] for t in best_combination]
            }
        
        return {"status": "unavailable"}
    
    def _find_best_combination_for_merge(self, tables: List[Dict[str, Any]], target_capacity: int) -> Optional[List[Dict[str, Any]]]:
        """Encuentra la mejor combinación de mesas (mínimo número de mesas)."""
        # Ordenar por capacidad descendente
        tables_sorted = sorted(tables, key=lambda t: t["capacity"], reverse=True)
        
        # Intentar con 2 mesas
        for i in range(len(tables_sorted)):
            for j in range(i + 1, len(tables_sorted)):
                if tables_sorted[i]["capacity"] + tables_sorted[j]["capacity"] >= target_capacity:
                    return [tables_sorted[i], tables_sorted[j]]
        
        # Intentar con 3 mesas
        for i in range(len(tables_sorted)):
            for j in range(i + 1, len(tables_sorted)):
                for k in range(j + 1, len(tables_sorted)):
                    if tables_sorted[i]["capacity"] + tables_sorted[j]["capacity"] + tables_sorted[k]["capacity"] >= target_capacity:
                        return [tables_sorted[i], tables_sorted[j], tables_sorted[k]]
        
        return None
    
    # ============================================================
    # MÉTODOS PRIVADOS PARA GOOGLE CALENDAR
    # ============================================================
    def _create_calendar_event(
        self, 
        name: str, 
        guests: int, 
        date: str, 
        time: str, 
        duration: int, 
        phone: str,
        table_info: str = None
    ) -> Optional[str]:
        """Crea un evento en Google Calendar para la reserva."""
        try:
            # Construir fecha/hora en formato ISO 8601
            start_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            end_dt = start_dt + timedelta(minutes=duration)
            
            title = f"Reserva: {name} ({guests} personas)"
            description = f"Reserva para {guests} personas\nTeléfono: {phone}\nDuración estimada: {duration} min"
            
            if table_info:
                description += f"\n{table_info}"
            
            event_id = self.calendar_repo.create_event(
                title=title,
                description=description,
                start_datetime=start_dt.isoformat(),
                end_datetime=end_dt.isoformat()
            )
            
            return event_id
        except Exception as e:
            print(f"Error al crear evento en calendario: {e}")
            return None
    
    def _update_calendar_event(self, event_id: str, current_reservation: dict, updates: dict):
        """Actualiza un evento existente en Google Calendar."""
        try:
            # Determinar nuevos valores
            new_date = updates.get("date", current_reservation["date"])
            new_time = updates.get("time", current_reservation["time"])
            new_name = updates.get("name", current_reservation["name"])
            new_guests = updates.get("guests", current_reservation["guests"])
            new_duration = updates.get("duration", current_reservation["duration"])
            
            # Construir nuevas fechas
            start_dt = datetime.strptime(f"{new_date} {new_time}", "%Y-%m-%d %H:%M")
            end_dt = start_dt + timedelta(minutes=new_duration)
            
            title = f"Reserva: {new_name} ({new_guests} personas)"
            description = f"Reserva para {new_guests} personas\nTeléfono: {current_reservation['phone']}\nDuración estimada: {new_duration} min"
            
            self.calendar_repo.update_event(
                event_id=event_id,
                title=title,
                description=description,
                start_datetime=start_dt.isoformat(),
                end_datetime=end_dt.isoformat()
            )
        except Exception as e:
            print(f"Error al actualizar evento en calendario: {e}")
