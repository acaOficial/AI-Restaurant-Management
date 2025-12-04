# 🍽️ AI Restaurant Management System

Sistema de gestión de reservas de restaurante utilizando MCP (Model Context Protocol) y OpenAI.

## 📋 Descripción

Este proyecto implementa un sistema de reservas inteligente para restaurantes que utiliza:
- **MCP Server** (`fastmcp`): Expone herramientas de reservas vía protocolo MCP.
- **Cliente OpenAI con MCP**: Chat interactivo con recepcionista virtual usando GPT-4-turbo.
- **Arquitectura limpia**: Separación por capas (domain, services, infrastructure).
- **Base de datos SQLite**: Sistema de reservas con control de solapamientos temporales.
- **Ngrok**: Exposición del servidor MCP para acceso público.
- **Google Calendar**: Se añade la fecha de la reserva a un calendario, usando la API de Google Calendar.

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone git@github.com:acaOficial/AI-Restaurant-Management.git
```

Una vez clonado el repositorio, navegar hacia el directorio principal del proyecto

```bash
cd AI-Restaurant-Management
```

### 2. Crear el entorno conda

```bash
conda env create -f environment.yml
conda activate restaurant-env
```

### 2. Instalar ngrok

Este proyecto depende de `ngrok`, un software que permite exponer la IP privada al exterior,
para realizar las comunicaciones con la API de OpenAI. Por este motivo, es necesario realizar
la instalación de este programa.

Existen dos formas de hacerlo:
- La más cómoda, descarlo e instalarlo desde la tienda de Windows (Microsoft Store).
- Evidentemente el método anterior solo funciona desde Windows, por tanto, la otra opción sería descargarlo desde su [página oficial](https://ngrok.com/) y luego instalarlo.

**Independientemente de la opción que se escoja para descargar e instalar `ngrok`, es necesario crear una cuenta a través de su [página web](https://ngrok.com/)**

Una vez creada la cuenta e iniciada la sesión, debería llevarnos a la página de descarga. En el posible caso que no nos redireccione, los enlaces de descarga son los siguientes:

**Windows:**
`https://dashboard.ngrok.com/get-started/setup/windows`

**Linux:**
`https://dashboard.ngrok.com/get-started/setup/linux`

**Mac:**
`https://dashboard.ngrok.com/get-started/setup/macos`

En esta página se encuentra el token de autenticación y el comando necesario para asignarlo a nuestro cliente de `ngrok`, independientemente del sistema operativo, el comando para añadir este token es el siguiente:

```bash
ngrok config add-authtoken your-token-here
```

Tras haber hecho esto, `ngrok` ya estaría completamente listo, un ejemplo de uso sería el siguiente:

```bash
ngrok http 8000
```

### 3. Configurar la API Key de OpenAI

Se dispone de un archivo `.env` en el que se podría introducir la API Key de OpenAI, sin embargo,
es posible ignorar este archivo y establecer la API Key como variable de entorno. A continuación se
muestran las posibles opciones para diferentes sistemas operativos:

**Windows PowerShell:**
```powershell
$env:OPENAI_API_KEY="tu-api-key-aqui"
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY="tu-api-key-aqui"
```

### 4. Configurar Google Calendar

Este proyecto integra **Google Calendar** para sincronizar automáticamente las fechas de las reservas con un calendario de Google.

#### Pasos para configurar Google Calendar

1. **Crear un proyecto en Google Cloud Console**
  - Acceder a [Google Cloud Console](https://console.cloud.google.com/)
  - Crear un nuevo proyecto
  - Habilitar la API de Google Calendar
  - Crear credenciales (OAuth 2.0 - Cuenta de servicio)

2. **Generar credenciales**
  - Descargar el archivo JSON de credenciales
  - Guardar como `resources/google_credentials.json`

3. **Compartir calendario con la cuenta de prueba**
  - En Google Calendar, compartir el calendario con la dirección de correo asociada a las credenciales
  - Asignar permisos de escritura

#### Verificar la integración

Una vez configurado, cada reserva que se cree a través del sistema se añadirá automáticamente al calendario de Google con:
- **Título**: Nombre del cliente + número de comensales
- **Fecha/Hora**: Según la reserva
- **Descripción**: Detalles de la reserva (teléfono, mesa, notas)

## 🗄️ Configuración de la Base de Datos

### **IMPORTANTE: Inicializar la BD antes de usar el sistema**

```bash
python init_db.py
```

Este script:
- Crea las tablas `tables` y `reservations`
- Elimina datos anteriores (TRUNCATE)
- **Popula con datos de prueba** (se crean 5 mesas con diferentes capacidades)
- Resetea la base de datos cada vez que se ejecuta

### Verificar el estado de la BD

```bash
python check_db.py
```

Este script muestra:
- Todas las tablas existentes
- El contenido completo de cada tabla (mesas y reservas)
- Historial de reservas con duración estimada

## 🎯 Ejecución del Sistema

### Paso 1: Exponer el MCP Server con ngrok

En una terminal o desde el cliente de `ngrok`, ejecuta:

```bash
ngrok http 8000
```

Esto creará un túnel público hacia tu servidor MCP local. **Copia la URL pública** (ejemplo: `https://xxxx-xxx-xxx-xxx.ngrok-free.app`) que aparecerá en la consola de ngrok.

**⚠️ IMPORTANTE:** Debes actualizar la URL en el archivo `.env` con la URL generada por ngrok:

```python
# Línea ~8
MCP_SERVER_URL=your-ngrok-url/mcp
```

### Paso 2: Iniciar el MCP Server

En una **nueva terminal**, ejecuta:

```bash
python infrastructure/mcp_server.py
```

El servidor se ejecutará en `http://0.0.0.0:8000` y expondrá las siguientes herramientas:
- **`find_table`**: Buscar mesas disponibles considerando capacidad, ubicación, fecha y hora. Permite combinaciones automáticas de mesas si no hay una individual suficiente.
- **`reserve_table`**: Crear una nueva reserva en una mesa específica con validación de solapamientos temporales.
- **`get_tables`**: Listar todas las mesas disponibles del restaurante.
- **`cancel_reservation`**: Cancelar una reserva existente usando teléfono y fecha.
- **`modify_reservation_by_phone`**: Modificar una reserva existente (hora, fecha o número de comensales).
- **`get_reservation`**: Obtener información detallada de una reserva existente.
- **`get_opening_hours`**: Obtener el horario de apertura del restaurante.
- **`is_open`**: Verificar si el restaurante está abierto en una fecha y hora específicas.
- **`get_opening_days`**: Obtener los días de apertura del restaurante.

### Paso 3: Ejecutar el cliente conversacional

En **otra terminal**, ejecuta:

```bash
python agents/client_mcp.py
```

Esto iniciará un chat interactivo donde puedes:
- Solicitar reservas de forma natural
- El recepcionista virtual te pedirá datos faltantes (nombre, teléfono, fecha, hora, etc.)
- El sistema validará disponibilidad automáticamente
- Se confirmarán o rechazarán reservas según el estado del restaurante

## 📁 Estructura del Proyecto

```
.
├── init_db.py                       # Script para crear/resetear la base de datos
├── check_db.py                      # Script para inspeccionar el estado de la BD
├── environment.yml                  # Dependencias del proyecto (conda)
├── README.md                        # Este archivo
│
├── agents/
│   └── client_mcp.py               # Cliente conversacional (chat con recepcionista)
│
├── core/                           # Capa de negocio
│   ├── domain/
│   │   └── models.py              # Modelos de datos (Table, Reservation)
│   ├── services/
│   │   └── booking_service.py    # Lógica de reservas y disponibilidad
│   └── utils/
│       └── reservation_utils.py  # Utilidades (estimación de duración)
│
├── infrastructure/                 # Capa de infraestructura
│   ├── mcp_server.py              # Servidor MCP (expone herramientas)
│   └── db_repository.py           # Acceso a base de datos SQLite
│
└── db/
    └── restaurant.sqlite          # Base de datos (se genera con init_db.py)
```

## 🧪 Funcionalidad de los Scripts

### `init_db.py`
- **Propósito:** Inicializar la base de datos del restaurante
- **Qué hace:**
  - Crea tablas `tables` y `reservations`
  - Elimina datos anteriores (TRUNCATE)
  - Inserta **1 mesa de prueba** (para testing de conflictos)
  - Añade columna `duration` a las reservas
- **Cuándo usarlo:** Antes del primer uso o para resetear el sistema

### `check_db.py`
- **Propósito:** Inspeccionar el estado actual de la base de datos
- **Qué hace:**
  - Lista todas las tablas
  - Muestra el contenido de cada tabla en formato legible con `pandas`
  - Útil para debugging y verificar reservas con sus duraciones
- **Cuándo usarlo:** Después de ejecutar reservas para verificar cambios
- **Requiere:** `pandas` (instalar con `pip install pandas`)

### `infrastructure/mcp_server.py`
- **Propósito:** Servidor MCP que expone herramientas de reservas
- **Qué hace:**
  - Levanta un servidor HTTP en puerto 8000 (host 0.0.0.0)
  - Expone 9 herramientas vía protocolo MCP
  - Delega la lógica de negocio a los servicios correspondientes
- **Herramientas expuestas:**
  - `find_table(guests, location, date, time)` - Busca mesas disponibles (con combinaciones automáticas)
  - `reserve_table(table_id, name, guests, date, time, phone, notes, merged_tables)` - Crea una nueva reserva
  - `get_tables()` - Lista todas las mesas disponibles
  - `cancel_reservation(phone, date)` - Cancela una reserva existente
  - `modify_reservation_by_phone(phone, date, new_time, new_date, new_guests)` - Modifica una reserva
  - `get_reservation(phone, date)` - Obtiene información de una reserva
  - `get_opening_hours()` - Devuelve horario de apertura
  - `is_open(date, time)` - Verifica si está abierto
  - `get_opening_days()` - Devuelve días de apertura
- **Cuándo usarlo:** Debe estar corriendo para que el cliente funcione

### `agents/client_mcp.py`
- **Propósito:** Cliente conversacional con recepcionista virtual
- **Qué hace:**
  - Inicia un chat interactivo usando OpenAI GPT-5
  - Se conecta al servidor MCP vía ngrok
  - El modelo llama automáticamente a las herramientas del MCP
  - Gestiona el flujo conversacional completo
- **Cuándo usarlo:** Después de iniciar el MCP server y ngrok
- **Nota:** Debes actualizar la `server_url` con tu URL de ngrok

### `core/services/booking_service.py`
- **Propósito:** Lógica de negocio para reservas
- **Qué hace:**
  - Implementa búsqueda de mesas considerando solapamientos temporales
  - Valida que no haya reservas duplicadas por teléfono/día
  - Calcula duración estimada de cada reserva
  - Comprueba disponibilidad por intervalos de tiempo
- **Funciones principales:**
  - `find_table()` - Busca mesa libre en fecha/hora específica
  - `reserve_table()` - Crea reserva con validaciones
  - `is_table_available()` - Verifica solapamientos temporales

### `core/domain/models.py`
- **Propósito:** Definición de modelos de datos
- **Qué hace:**
  - Define `Table` (id, capacity, location, available)
  - Define `Reservation` (id, table_id, name, guests, date, time, phone, duration)

### `core/utils/reservation_utils.py`
- **Propósito:** Utilidades para cálculos de reservas
- **Qué hace:**
  - `estimate_duration()` - Estima duración según número de comensales y hora
  - Añade 15 min por cada persona adicional
  - Cenas (≥21h) duran 30 min más
  - Máximo: 180 minutos (3 horas)

### `infrastructure/db_repository.py`
- **Propósito:** Capa de acceso a datos
- **Qué hace:**
  - Gestiona conexiones a SQLite
  - Funciones `query()` y `execute()` para operaciones DB
  - Manejo automático de rutas y conexiones

## 🔧 Troubleshooting

### Error: "No module named 'fastmcp'"
```bash
pip install fastmcp
```

### Error: "No module named 'pandas'"
```bash
pip install pandas
```

### Error: "OPENAI_API_KEY not set"
Configura la variable de entorno con tu API key de OpenAI:
```powershell
$env:OPENAI_API_KEY="tu-api-key-aqui"
```

O, agrega tu API Key de OpenAI al archivo `.env`:
```python
# Línea ~2
OPENAI_API_KEY=your-api-key-here
```

### Error: "database is locked"
- Cierra `check_db.py` si está abierto
- Cierra todas las conexiones al MCP server
- Reinicia el servidor MCP

### Error: "connection refused" al ejecutar el cliente
- Verifica que el MCP server esté corriendo (`infrastructure/mcp_server.py`)
- Verifica que ngrok esté activo
- Comprueba que la URL en `agents/client_mcp.py` coincida con la de ngrok

### No hay mesas disponibles
- Verifica con `python check_db.py` las reservas existentes
- Ejecuta `python init_db.py` para resetear la base de datos

### El MCP no responde o da errores 404
- Asegúrate de que la URL en el cliente termine en `/mcp`
- Ejemplo correcto: `https://xxxx.ngrok-free.app/mcp`
- Verifica que ngrok esté apuntando al puerto 8000

## 📝 Ejemplo de Flujo Completo

```bash
# Terminal 1: Preparar la BD
python init_db.py
python check_db.py  # Verificar estado inicial (verás 1 mesa vacía)

# Terminal 2: Iniciar MCP Server
python infrastructure/mcp_server.py

# Terminal 3: Exponer MCP Server con ngrok
ngrok http 8000
# ⚠️ IMPORTANTE: Copia la URL pública (ej: https://xxxx.ngrok-free.app)
# Y actualízala en agents/client_mcp.py línea ~9

# Terminal 4: Ejecutar el cliente conversacional
python agents/client_mcp.py
# Ahora puedes chatear con el recepcionista virtual

# Terminal 1: Verificar cambios en la BD después de reservar
python check_db.py
```

### Ejemplo de conversación:

```
👤 Tú: Hola, quiero reservar una mesa para 2 personas
🤖 Recepcionista: ¡Hola! Claro, para 2 personas. ¿Para qué fecha te gustaría hacer la reserva?

👤 Tú: Para mañana a las 20:00 en interior
🤖 Recepcionista: Perfecto. Solo necesito tu nombre y número de teléfono para confirmar la reserva.

👤 Tú: Juan Pérez, teléfono 612345678
🤖 Recepcionista: ¡Reserva confirmada! Mesa 1 para 2 personas el [fecha] a las 20:00 
a nombre de Juan Pérez. ¡Te esperamos!
```

## 🤝 Contribuciones

Este es un proyecto educativo para demostrar:
- Integración de MCP (Model Context Protocol) con OpenAI.
- Arquitectura limpia por capas en Python.
- Sistema de reservas con control temporal de solapamientos.
- Exposición de servicios locales con ngrok.
- Uso de GPT-4-turbo con herramientas MCP en conversaciones.
- Uso de Google Calendar para interacción del LLM con APIs externas.

## 🏗️ Arquitectura

**Patrón de diseño:** Arquitectura por capas (Clean Architecture)

- **Capa de Dominio** (`core/domain`): Modelos de negocio.
- **Capa de Servicios** (`core/services`): Lógica de negocio.
- **Capa de Infraestructura** (`infrastructure`): MCP server, acceso a datos.
- **Capa de Presentación** (`agents`): Cliente conversacional.

**Flujo de datos:**
```
Usuario → Client MCP → MCP Server → Booking Service → DB Repository → SQLite
         (GPT-4-turbo)  (FastMCP)     (Lógica)        (Query/Execute)
```

## 📚 Tecnologías Utilizadas

- **Python 3.10+**
- **FastMCP**: Framework para crear servidores MCP.
- **OpenAI API**: GPT-5 con soporte MCP.
- **SQLite**: Base de datos embebida.
- **Ngrok**: Túneles HTTP seguros.
- **Pandas**: Análisis de datos (para check_db.py).
- **Google Calendar**: Sincronizar el calendario con la fecha de resrva.


