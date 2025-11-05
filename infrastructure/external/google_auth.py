"""Autenticación con Google Calendar API."""
import os
from pathlib import Path
from typing import Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle


# Si modificas los SCOPES, elimina el archivo token.pickle
SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleAuthManager:
    """Gestor de autenticación OAuth2 para Google Calendar."""
    
    def __init__(self, credentials_path: str, token_path: Optional[str] = None):
        """
        Inicializa el gestor de autenticación.
        
        Args:
            credentials_path: Ruta al archivo credentials.json de Google
            token_path: Ruta donde guardar el token (por defecto junto a credentials)
        """
        self.credentials_path = Path(credentials_path)
        if token_path:
            self.token_path = Path(token_path)
        else:
            self.token_path = self.credentials_path.parent / "token.pickle"
    
    def get_credentials(self) -> Optional[Credentials]:
        """
        Obtiene credenciales válidas para Google Calendar API.
        
        Si no existen credenciales guardadas o están expiradas,
        inicia el flujo de autenticación OAuth2.
        
        Returns:
            Credenciales válidas o None si falla
        """
        creds = None
        
        # Cargar credenciales guardadas si existen
        if self.token_path.exists():
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Si no hay credenciales válidas, obtenerlas
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Refrescar token expirado
                creds.refresh(Request())
            else:
                # Iniciar flujo OAuth2
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"No se encontró el archivo de credenciales: {self.credentials_path}\n"
                        "Descárgalo desde Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path),
                    SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Guardar credenciales para la próxima vez
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        return creds
