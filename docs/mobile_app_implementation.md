# Documentación de Implementación: Citas Multiprofesional

Esta guía detalla los cambios necesarios en la aplicación móvil de clientes para soportar el nuevo sistema de gestión de equipo y disponibilidad concurrente de **Booksmart**.

## 1. Cambio de Paradigma
Anteriormente, la disponibilidad era única por negocio. Ahora, la disponibilidad es **por profesional capacitado**. Esto permite que un mismo horario sea reservado varias veces siempre que haya diferentes trabajadores libres.

## 2. Endpoints Actualizados

### A. Consulta de Disponibilidad (Slots)
El endpoint ahora acepta un filtro opcional por trabajador y calcula la capacidad real del equipo.

- **URL:** `GET /api/v1/appointments/availability/slots`
- **Query Params:**
    - `servicio_id` (int, Requerido)
    - `target_date` (date, Requerido, Formato: `YYYY-MM-DD`)
    - `trabajador_id` (int, Opcional): Si no se envía, el sistema busca disponibilidad sumando a todos los trabajadores que ofrecen el servicio.

**Ejemplo de Respuesta Mejorada:**
```json
{
  "date": "2024-10-25",
  "servicio_id": 5,
  "worker_count": 3,
  "available_slots": ["09:00", "09:30", "15:00"],
  "busy_slots": ["10:00", "11:00"],
  "closed": false,
  "closure_reason": null
}
```

### B. Creación de Cita (Reserva)
El campo `trabajador_id` ahora es el que determina si la cita es asignada manualmente o por el sistema.

- **URL:** `POST /api/v1/appointments/`
- **Payload:**
```json
{
  "cliente_id": 10,
  "servicio_id": 5,
  "fecha": "2024-10-25",
  "hora_inicio": "09:00:00",
  "trabajador_id": null 
}
```
> **Nota:** Al enviar `trabajador_id: null`, el backend activa el **algoritmo de auto-asignación** y buscará al profesional disponible con menos carga.

---

## 3. Guía de Interfaz de Usuario (UX)

### Paso 1: Filtro de Profesionales
Después de seleccionar un servicio, es recomendable dar la opción al cliente de elegir un profesional.
- **Opción recomendada:** "Cualquiera" (seleccionada por defecto).
- **Opción específica:** Listar a los trabajadores que devuelva `GET /api/v1/workers?establishment_id=X`.

### Paso 2: Calendario Dinámico
- Si el cliente deja "Cualquiera", llama a los *slots* sin `trabajador_id`. Verá más horarios disponibles.
- Si el cliente elige a un profesional, llama a los *slots* pasando el `trabajador_id`. Verá solo los huecos de esa persona.

### Paso 3: Pantalla de Éxito
En la respuesta del `POST`, el backend devolverá el objeto Cita completo con el `trabajador_id` ya asignado. Puedes usar esto para mostrar: *"¡Reserva confirmada con Juan!"*.

---

## 4. Códigos de Error
- `404 Service not found`: El servicio no existe.
- `400 No hay profesionales registrados...`: El negocio no ha configurado qué trabajadores hacen este servicio.
- `400 Lo sentimos, no hay profesionales disponibles...`: Al intentar confirmar, los trabajadores libres ya fueron ocupados por otros clientes.
