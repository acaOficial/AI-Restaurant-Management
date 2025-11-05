# Configuración de Google Calendar

Para integrar Google Calendar con el sistema de reservas, sigue estos pasos:

## 1. Crear un proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la **Google Calendar API**:
   - En el menú lateral, ve a "APIs y servicios" > "Biblioteca"
   - Busca "Google Calendar API"
   - Haz clic en "Habilitar"

## 2. Crear credenciales OAuth 2.0

1. Ve a "APIs y servicios" > "Credenciales"
2. Haz clic en "+ CREAR CREDENCIALES" > "ID de cliente de OAuth"
3. Selecciona "Aplicación de escritorio" como tipo de aplicación
4. Dale un nombre (ej: "Restaurant Booking System")
5. Haz clic en "Crear"
6. Descarga el archivo JSON de credenciales
7. Guárdalo como `resources/google_credentials.json`

## 3. Configurar el archivo .env

Edita tu archivo `.env` y configura las siguientes variables:

```env
# Google Calendar Configuration
GOOGLE_CALENDAR_ENABLED=true
GOOGLE_CALENDAR_ID=primary
GOOGLE_CREDENTIALS_PATH=resources/google_credentials.json
```

### Opciones de configuración:

- **GOOGLE_CALENDAR_ENABLED**: `true` para activar, `false` para desactivar
- **GOOGLE_CALENDAR_ID**: 
  - `primary` = tu calendario principal
  - O el ID específico de un calendario (ej: `abc123@group.calendar.google.com`)
- **GOOGLE_CREDENTIALS_PATH**: Ruta al archivo de credenciales JSON descargado

## 4. Primera autenticación

La primera vez que ejecutes el servidor con Google Calendar habilitado:

1. Se abrirá automáticamente una ventana del navegador
2. Inicia sesión con tu cuenta de Google
3. Autoriza la aplicación para acceder a tu calendario
4. Se generará un archivo `token.pickle` que guardará las credenciales

**⚠️ IMPORTANTE**: Mantén `token.pickle` y `google_credentials.json` en privado. Añádelos a `.gitignore`.

## 5. Instalar dependencias

Actualiza tu entorno conda:

```bash
conda env update -f environment.yml
```

O instala manualmente:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## 6. Reiniciar la base de datos

Como hemos añadido el campo `calendar_event_id` a la tabla de reservas:

```bash
python init_db.py
```

## 7. Probar la integración

1. Inicia el servidor MCP:
   ```bash
   python infrastructure/mcp_server.py
   ```

2. Crea una reserva desde el cliente

3. Verifica que el evento aparece en tu Google Calendar

## Funcionamiento

### Cuando creas una reserva:
- Se crea automáticamente un evento en Google Calendar
- El evento incluye:
  - Título: "Reserva: [nombre] ([N] personas)"
  - Descripción: Detalles de la reserva
  - Fecha y hora: Según la reserva
  - Duración: Estimada automáticamente

### Cuando modificas una reserva:
- Se actualiza el evento en Google Calendar con los nuevos datos

### Cuando cancelas una reserva:
- Se elimina el evento de Google Calendar

## Desactivar Google Calendar

Si quieres desactivar la integración temporalmente:

```env
GOOGLE_CALENDAR_ENABLED=false
```

El sistema seguirá funcionando normalmente, solo que las reservas no se sincronizarán con Google Calendar.

## Uso de calendarios compartidos

Para sincronizar con un calendario específico (no el principal):

1. En Google Calendar, crea un calendario dedicado para reservas
2. Obtén su ID:
   - Ve a la configuración del calendario
   - Copia el "ID del calendario" (formato: `xyz@group.calendar.google.com`)
3. Actualiza el `.env`:
   ```env
   GOOGLE_CALENDAR_ID=xyz@group.calendar.google.com
   ```

## Solución de problemas

### Error: "No se encontró el archivo de credenciales"
- Verifica que el archivo `google_credentials.json` existe en la ruta especificada
- Comprueba que la ruta en `GOOGLE_CREDENTIALS_PATH` es correcta

### Error: "No se pudieron obtener credenciales de Google"
- Elimina el archivo `token.pickle` y vuelve a autenticarte
- Verifica que has habilitado la Google Calendar API en tu proyecto

### Las reservas no aparecen en el calendario
- Verifica que `GOOGLE_CALENDAR_ENABLED=true`
- Comprueba que el `GOOGLE_CALENDAR_ID` es correcto
- Revisa los logs del servidor MCP para errores

### Error de permisos
- Asegúrate de que has autorizado todos los permisos solicitados durante la autenticación
- Si cambiaste los SCOPES en `google_auth.py`, elimina `token.pickle` y vuelve a autenticarte
