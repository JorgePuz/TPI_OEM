# ─────────────────────────────────────────────────────
# fsm.py — Maquina de Estados Finitos del bot
# Contiene toda la logica de negocio del proceso
# de gestion de vacaciones
# ─────────────────────────────────────────────────────

import json
from datetime import datetime, timedelta

# ── 1. DEFINICION DE ESTADOS ──────────────────────────
# Cada constante representa un estado posible del bot
class Estado:
    INICIO               = "INICIO"
    IDENTIFICADO         = "IDENTIFICADO"
    CONSULTANDO_SALDO    = "CONSULTANDO_SALDO"
    INGRESANDO_FECHAS    = "INGRESANDO_FECHAS"
    VALIDANDO            = "VALIDANDO"
    PENDIENTE_APROBACION = "PENDIENTE_APROBACION"
    APROBADO             = "APROBADO"
    RECHAZADO            = "RECHAZADO"


# ── 2. FUNCIONES DE BASE DE DATOS ────────────────────
# Estas funciones leen y escriben los archivos JSON
# simulando las operaciones de una base de datos real

def leer_json(archivo):
    """Lee un archivo JSON y devuelve su contenido."""
    try:
        with open(f"database/{archivo}", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def escribir_json(archivo, datos):
    """Escribe datos en un archivo JSON."""
    with open(f"database/{archivo}", "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)


# ── 3. FUNCIONES DE SESION ────────────────────────────
# Gestionan el estado actual de cada usuario

def obtener_sesion(chat_id):
    """
    Busca la sesion del usuario en sesiones.json.
    Si no existe, crea una nueva en estado INICIO.
    """
    sesiones = leer_json("sesiones.json")
    
    for sesion in sesiones:
        if sesion["chat_id"] == str(chat_id):
            return sesion
    
    # Si no existe la sesion, la creamos
    nueva_sesion = {
        "chat_id":           str(chat_id),
        "estado_actual":     Estado.INICIO,
        "id_empleado":       None,
        "fecha_inicio_temp": None,
        "cantidad_dias_temp": None,
        "timestamp":         str(datetime.now())
    }
    sesiones.append(nueva_sesion)
    escribir_json("sesiones.json", sesiones)
    return nueva_sesion

def guardar_sesion(sesion):
    """Actualiza la sesion del usuario en sesiones.json."""
    sesiones = leer_json("sesiones.json")
    
    for i, s in enumerate(sesiones):
        if s["chat_id"] == sesion["chat_id"]:
            sesion["timestamp"] = str(datetime.now())
            sesiones[i] = sesion
            escribir_json("sesiones.json", sesiones)
            return

def reiniciar_sesion(chat_id):
    """
    Reinicia la sesion del usuario al estado INICIO.
    Se llama cuando el usuario usa /start o /cancelar.
    """
    sesiones = leer_json("sesiones.json")
    
    for i, s in enumerate(sesiones):
        if s["chat_id"] == str(chat_id):
            sesiones[i] = {
                "chat_id":            str(chat_id),
                "estado_actual":      Estado.INICIO,
                "id_empleado":        None,
                "fecha_inicio_temp":  None,
                "cantidad_dias_temp": None,
                "timestamp":          str(datetime.now())
            }
            escribir_json("sesiones.json", sesiones)
            return


# ── 4. FUNCIONES DE NEGOCIO ───────────────────────────
# Implementan las reglas del proceso de vacaciones

def buscar_empleado(legajo):
    """
    Busca un empleado por su legajo en empleados.json.
    Devuelve el empleado si existe, None si no.
    """
    empleados = leer_json("empleados.json")
    
    for emp in empleados:
        if emp["legajo"].upper() == legajo.upper():
            return emp
    return None

def buscar_empleado_por_id(id_empleado):
    """Busca un empleado por su ID."""
    empleados = leer_json("empleados.json")
    
    for emp in empleados:
        if emp["id_empleado"] == id_empleado:
            return emp
    return None

def validar_fecha(texto):
    """
    Verifica que el texto tenga formato DD/MM/AAAA.
    Devuelve True si es valido, False si no.
    """
    try:
        datetime.strptime(texto, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def calcular_fecha_fin(fecha_inicio_str, cantidad_dias):
    """Calcula la fecha de fin sumando los dias solicitados."""
    fecha_inicio = datetime.strptime(fecha_inicio_str, "%d/%m/%Y")
    fecha_fin = fecha_inicio + timedelta(days=cantidad_dias - 1)
    return fecha_fin.strftime("%d/%m/%Y")

def hay_superposicion(fecha_inicio_str, cantidad_dias, id_empleado):
    """
    Verifica si las fechas solicitadas se superponen con
    vacaciones ya aprobadas o pendientes de otros empleados.
    Devuelve True si hay superposicion, False si estan libres.
    """
    solicitudes = leer_json("solicitudes.json")
    
    fecha_inicio = datetime.strptime(fecha_inicio_str, "%d/%m/%Y")
    fecha_fin = fecha_inicio + timedelta(days=cantidad_dias - 1)
    
    for sol in solicitudes:
        # Solo revisamos solicitudes aprobadas o pendientes
        # de OTROS empleados (no del mismo)
        if (sol["estado"] in ["APROBADA", "PENDIENTE"] and
                sol["id_empleado"] != id_empleado):
            
            sol_inicio = datetime.strptime(sol["fecha_inicio"], "%d/%m/%Y")
            sol_fin = datetime.strptime(sol["fecha_fin"], "%d/%m/%Y")
            
            # Hay superposicion si los rangos se solapan
            if not (fecha_fin < sol_inicio or fecha_inicio > sol_fin):
                return True
    
    return False

def registrar_solicitud(sesion):
    """
    Guarda una nueva solicitud en solicitudes.json
    con estado PENDIENTE.
    """
    solicitudes = leer_json("solicitudes.json")
    
    fecha_fin = calcular_fecha_fin(
        sesion["fecha_inicio_temp"],
        sesion["cantidad_dias_temp"]
    )
    
    # Generamos un ID unico
    nuevo_id = len(solicitudes) + 1
    
    nueva_solicitud = {
        "id_solicitud":   nuevo_id,
        "id_empleado":    sesion["id_empleado"],
        "fecha_inicio":   sesion["fecha_inicio_temp"],
        "cantidad_dias":  sesion["cantidad_dias_temp"],
        "fecha_fin":      fecha_fin,
        "estado":         "PENDIENTE",
        "fecha_solicitud": str(datetime.now()),
        "motivo_rechazo": None
    }
    
    solicitudes.append(nueva_solicitud)
    escribir_json("solicitudes.json", solicitudes)
    return nuevo_id

def aprobar_solicitud(id_empleado, cantidad_dias):
    """
    Cambia el estado de la solicitud a APROBADA
    y descuenta los dias del saldo del empleado.
    """
    # Actualizar solicitud
    solicitudes = leer_json("solicitudes.json")
    for i, sol in enumerate(solicitudes):
        if (sol["id_empleado"] == id_empleado and
                sol["estado"] == "PENDIENTE"):
            solicitudes[i]["estado"] = "APROBADA"
            break
    escribir_json("solicitudes.json", solicitudes)
    
    # Descontar dias del empleado
    empleados = leer_json("empleados.json")
    for i, emp in enumerate(empleados):
        if emp["id_empleado"] == id_empleado:
            empleados[i]["dias_disponibles"] -= cantidad_dias
            empleados[i]["dias_tomados"]     += cantidad_dias
            break
    escribir_json("empleados.json", empleados)

def rechazar_solicitud(id_empleado, motivo):
    """Cambia el estado de la solicitud a RECHAZADA."""
    solicitudes = leer_json("solicitudes.json")
    for i, sol in enumerate(solicitudes):
        if (sol["id_empleado"] == id_empleado and
                sol["estado"] == "PENDIENTE"):
            solicitudes[i]["estado"]         = "RECHAZADA"
            solicitudes[i]["motivo_rechazo"] = motivo
            break
    escribir_json("solicitudes.json", solicitudes)


# ── 5. FUNCION PRINCIPAL: EL SWITCH DE ESTADOS ────────
# Esta es la funcion que llama bot.py con cada mensaje.
# Lee el estado actual y decide que hacer.

def procesar_mensaje(chat_id, texto):
    """
    Recibe el chat_id del usuario y el texto que escribio.
    Devuelve la respuesta que el bot debe enviar.
    """
    
    # Obtenemos la sesion actual del usuario
    sesion = obtener_sesion(chat_id)
    estado = sesion["estado_actual"]
    
    
    # ── ESTADO: INICIO ────────────────────────────────
    # Esperamos el legajo del empleado
    if estado == Estado.INICIO:
        
        empleado = buscar_empleado(texto)
        
        if empleado:
            # Legajo valido: guardamos datos y avanzamos
            sesion["id_empleado"]  = empleado["id_empleado"]
            sesion["estado_actual"] = Estado.IDENTIFICADO
            guardar_sesion(sesion)
            
            return (
                f"Bienvenido, {empleado['nombre']} {empleado['apellido']}.\n\n"
                f"Que deseas hacer?\n"
                f"1. Consultar saldo de vacaciones\n"
                f"2. Solicitar vacaciones"
            )
        else:
            # Legajo invalido: camino infeliz, pedimos reintento
            return (
                "Legajo no encontrado en el sistema.\n"
                "Por favor verifica el numero e intentalo nuevamente.\n"
                "Ejemplo: EMP001"
            )
    
    
    # ── ESTADO: IDENTIFICADO ──────────────────────────
    # Esperamos que el usuario elija 1 o 2
    elif estado == Estado.IDENTIFICADO:
        
        if texto == "1":
            # Opcion 1: consultar saldo
            empleado = buscar_empleado_por_id(sesion["id_empleado"])
            sesion["estado_actual"] = Estado.CONSULTANDO_SALDO
            guardar_sesion(sesion)
            
            return (
                f"Tu saldo de vacaciones:\n\n"
                f"Dias disponibles: {empleado['dias_disponibles']}\n"
                f"Dias tomados este año: {empleado['dias_tomados']}\n\n"
                f"Deseas hacer algo mas?\n"
                f"1. Volver al menu\n"
                f"2. Solicitar vacaciones"
            )
        
        elif texto == "2":
            # Opcion 2: solicitar vacaciones
            sesion["estado_actual"] = Estado.INGRESANDO_FECHAS
            guardar_sesion(sesion)
            
            return (
                "Ingresa la fecha de inicio de tus vacaciones.\n"
                "Formato: DD/MM/AAAA\n"
                "Ejemplo: 15/03/2025"
            )
        
        else:
            # Camino infeliz: opcion invalida
            return (
                "Opcion no valida.\n"
                "Por favor ingresa 1 o 2.\n\n"
                "1. Consultar saldo\n"
                "2. Solicitar vacaciones"
            )
    
    
    # ── ESTADO: CONSULTANDO_SALDO ─────────────────────
    # El usuario vio su saldo, esperamos que elija que hacer
    elif estado == Estado.CONSULTANDO_SALDO:
        
        if texto == "1":
            sesion["estado_actual"] = Estado.IDENTIFICADO
            guardar_sesion(sesion)
            return (
                "Que deseas hacer?\n"
                "1. Consultar saldo\n"
                "2. Solicitar vacaciones"
            )
        
        elif texto == "2":
            sesion["estado_actual"] = Estado.INGRESANDO_FECHAS
            guardar_sesion(sesion)
            return (
                "Ingresa la fecha de inicio.\n"
                "Formato: DD/MM/AAAA\n"
                "Ejemplo: 15/03/2025"
            )
        
        else:
            return "Ingresa 1 para volver al menu o 2 para solicitar vacaciones."
    
    
    # ── ESTADO: INGRESANDO_FECHAS ─────────────────────
    # Primero esperamos la fecha, luego la cantidad de dias
    elif estado == Estado.INGRESANDO_FECHAS:
        
        # Paso A: todavia no tenemos la fecha de inicio
        if sesion["fecha_inicio_temp"] is None:
            
            if validar_fecha(texto):
                # Fecha valida: la guardamos y pedimos los dias
                sesion["fecha_inicio_temp"] = texto
                guardar_sesion(sesion)
                
                return (
                    f"Fecha de inicio: {texto}\n\n"
                    f"Cuantos dias necesitas?"
                )
            else:
                # Camino infeliz: formato incorrecto
                return (
                    "Formato de fecha incorrecto.\n"
                    "Usa DD/MM/AAAA\n"
                    "Ejemplo: 15/03/2025"
                )
        
        # Paso B: ya tenemos la fecha, esperamos la cantidad
        else:
            
            if texto.isdigit() and int(texto) > 0:
                # Cantidad valida: guardamos y pasamos a validar
                sesion["cantidad_dias_temp"] = int(texto)
                sesion["estado_actual"]      = Estado.VALIDANDO
                guardar_sesion(sesion)
                
                # Llamamos directamente a validar
                return validar_solicitud(sesion)
            
            else:
                # Camino infeliz: no es un numero valido
                return (
                    "Por favor ingresa un numero entero mayor a cero.\n"
                    "Ejemplo: 5"
                )
    
    
    # ── ESTADO: PENDIENTE_APROBACION ──────────────────
    # Simulamos la respuesta del jefe
    elif estado == Estado.PENDIENTE_APROBACION:
        
        if texto.lower() in ["si", "sí", "1", "aprobar"]:
            # El jefe aprueba
            aprobar_solicitud(
                sesion["id_empleado"],
                sesion["cantidad_dias_temp"]
            )
            sesion["estado_actual"] = Estado.APROBADO
            guardar_sesion(sesion)
            
            fecha_fin = calcular_fecha_fin(
                sesion["fecha_inicio_temp"],
                sesion["cantidad_dias_temp"]
            )
            
            return (
                "Solicitud APROBADA.\n\n"
                f"Fecha inicio: {sesion['fecha_inicio_temp']}\n"
                f"Fecha fin:    {fecha_fin}\n"
                f"Dias tomados: {sesion['cantidad_dias_temp']}\n\n"
                "Los dias fueron descontados de tu saldo.\n"
                "Escribe /start para realizar otra consulta."
            )
        
        elif texto.lower() in ["no", "2", "rechazar"]:
            # El jefe rechaza
            rechazar_solicitud(
                sesion["id_empleado"],
                "Rechazada por el jefe"
            )
            sesion["estado_actual"] = Estado.RECHAZADO
            guardar_sesion(sesion)
            
            return (
                "Solicitud RECHAZADA.\n\n"
                "Tu jefe no pudo aprobar la solicitud "
                "en esas fechas.\n"
                "Escribe /start para intentar con otras fechas."
            )
        
        else:
            return (
                "Por favor responde si o no.\n"
                "El jefe aprueba la solicitud? (si/no)"
            )
    
    
    # ── ESTADOS FINALES ───────────────────────────────
    # Si el proceso ya termino, invitamos a reiniciar
    elif estado in [Estado.APROBADO, Estado.RECHAZADO]:
        return (
            "El proceso ya finalizo.\n"
            "Escribe /start para comenzar una nueva consulta."
        )
    
    
    # ── ESTADO DESCONOCIDO ────────────────────────────
    # Por si acaso algo sale mal
    else:
        reiniciar_sesion(chat_id)
        return (
            "Ocurrio un error inesperado.\n"
            "Tu sesion fue reiniciada.\n"
            "Ingresa tu legajo para comenzar."
        )


# ── 6. FUNCION DE VALIDACION ──────────────────────────
# Verifica saldo y fechas antes de registrar la solicitud

def validar_solicitud(sesion):
    """
    Aplica las dos compuertas de decision del BPMN:
    1. Tiene dias suficientes?
    2. Las fechas estan disponibles?
    """
    empleado     = buscar_empleado_por_id(sesion["id_empleado"])
    dias_pedidos = sesion["cantidad_dias_temp"]
    
    # ── COMPUERTA 1: Tiene dias suficientes? ──────────
    if empleado["dias_disponibles"] < dias_pedidos:
        sesion["estado_actual"] = Estado.RECHAZADO
        guardar_sesion(sesion)
        
        return (
            f"No tienes saldo suficiente.\n\n"
            f"Dias disponibles: {empleado['dias_disponibles']}\n"
            f"Dias solicitados: {dias_pedidos}\n\n"
            "Solicitud cancelada.\n"
            "Escribe /start para intentar con menos dias."
        )
    
    # ── COMPUERTA 2: Fechas disponibles? ─────────────
    if hay_superposicion(
        sesion["fecha_inicio_temp"],
        dias_pedidos,
        sesion["id_empleado"]
    ):
        # Fechas ocupadas: reiniciamos la fecha y pedimos otra
        sesion["fecha_inicio_temp"] = None
        sesion["estado_actual"]     = Estado.INGRESANDO_FECHAS
        guardar_sesion(sesion)
        
        return (
            "Esas fechas no estan disponibles.\n"
            "Otro empleado tiene vacaciones aprobadas "
            "en ese periodo.\n\n"
            "Por favor ingresa una nueva fecha de inicio:"
        )
    
    # ── TODO OK: Registrar y pasar a pendiente ────────
    registrar_solicitud(sesion)
    
    fecha_fin = calcular_fecha_fin(
        sesion["fecha_inicio_temp"],
        dias_pedidos
    )
    
    sesion["estado_actual"] = Estado.PENDIENTE_APROBACION
    guardar_sesion(sesion)
    
    return (
        f"Resumen de tu solicitud:\n\n"
        f"Fecha inicio: {sesion['fecha_inicio_temp']}\n"
        f"Fecha fin:    {fecha_fin}\n"
        f"Dias pedidos: {dias_pedidos}\n"
        f"Saldo actual: {empleado['dias_disponibles']} dias\n\n"
        "Solicitud registrada con estado PENDIENTE.\n\n"
        "--- SIMULACION JEFE ---\n"
        "El jefe aprueba la solicitud? (si/no)"
    )