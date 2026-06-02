# Bot de Gestión de Vacaciones — TPI Organización Empresarial

**Tecnicatura Universitaria en Programación — UTN TUPaD**
Organización Empresarial

## Descripción

Chatbot desarrollado en Python sobre la plataforma Telegram
que automatiza el proceso de solicitud y gestión de vacaciones
de la empresa ficticia Bikes Benitez S.A.

El bot implementa una Máquina de Estados Finitos (FSM) que
gestiona el flujo completo del proceso, modelado previamente
con la metodología BPMN 2.0.

## Tecnologías utilizadas

- Python 3.14
- python-telegram-bot 21.5
- python-dotenv 1.0.0
- Base de datos simulada en JSON

## Estructura del proyecto

bot-vacaciones-utn/
├── bot.py                 → Punto de entrada del bot
├── fsm.py                 → Máquina de estados (lógica de negocio)
├── requirements.txt       → Dependencias del proyecto
├── .env                   → Token del bot (NO incluido en el repo)
├── .gitignore             → Archivos excluidos del repositorio
└── database/
├── empleados.json     → Base de datos de empleados
├── solicitudes.json   → Registro de solicitudes
└── sesiones.json      → Estado de sesiones activas

## Empleados de prueba

| Legajo | Nombre | Días disponibles |
|--------|--------|-----------------|
| EMP001 | María García | 15 |
| EMP002 | Carlos López | 10 |
| EMP003 | Ana Martínez | 20 |
| EMP004 | Pedro Sánchez | 0 |
| EMP005 | Laura Fernández | 8 |