# 📚 Documentación - Workers & Appointments (2026-04-14)

## 🎯 Resumen Ejecutivo

A partir del 2026-04-12, el sistema de citas en Booksmart cambió de forma fundamental:

**Antes:** Un calendario compartido por negocio → Una cita máximo por slot horario  
**Ahora:** Cada trabajador tiene su propio calendario → Múltiples citas simultáneas posibles

Esto significa:
- ✅ Mejor uso de recursos (múltiples profesionales trabajan en paralelo)
- ✅ Mayor flexibilidad para clientes (elijen profesional específico)
- ✅ Auto-asignación inteligente si no importa el profesional
- ✅ Cada cita debe especificar el `trabajador_id` (no es opcional)

---

## 📖 Documentos Disponibles

### Para el Frontend 👨‍💻
👉 **[USO_CREACION_CITAS_CON_TRABAJADORES.md](booksmart_pwa/docs/usos/USO_CREACION_CITAS_CON_TRABAJADORES.md)**
- Cambio arquitectónico explicado
- Flujos completos de creación de citas
- Componentes involucrados
- Servicio `AppointmentService` con código TypeScript listo
- Estructura de DTOs
- Ejemplos de componentes Angular
- Manejo de errores
- 4 casos de uso completos

**Ideal para:** Implementar la UI de reserva o calendario de trabajador

---

### Para el Backend 🔧
👉 **[ANALISIS_BACKEND_CITAS_TRABAJADORES_2026-04-14.md](ANALISIS_BACKEND_CITAS_TRABAJADORES_2026-04-14.md)**
- Arquitectura completa de modelos (Worker, Appointment, Agenda, WorkerService)
- Todos los schemas/DTOs Python
- CRUD logic paso a paso
- 6 endpoints principales con ejemplos
- Matriz de control de acceso por rol
- Últimos 5 commits relevantes

**Ideal para:** Entender cómo funciona el backend, debug de problemas

---

### Referencia Rápida 🚀
👉 **[QUICK_REFERENCE_ENDPOINTS_2026-04-14.md](QUICK_REFERENCE_ENDPOINTS_2026-04-14.md)**
- `curl` ejemplos para CADA endpoint
- JSON request/response reales
- Casos de uso practicos
- Manejo de errores
- Status transitions de citas

**Ideal para:** Testing rápido, debugging, integración

---

### Diagramas & Flujos 📊
👉 **[DIAGRAMAS_RELACIONES_FLUJOS_2026-04-14.md](DIAGRAMAS_RELACIONES_FLUJOS_2026-04-14.md)**
- ER Diagram ASCII de modelos
- Relaciones entidades
- Flujo visual: Creación de cita (5 pasos)
- Flujo visual: Consulta de disponibilidad (5 pasos)
- Matriz de validaciones
- Ciclo de vida de cita
- Matriz de permisos por rol

**Ideal para:** Presentaciones, onboarding, comprensión visual

---

### Puntos Clave 💡
👉 **[CONCLUSIONES_PUNTOS_CLAVE_2026-04-14.md](CONCLUSIONES_PUNTOS_CLAVE_2026-04-14.md)**
- 10 hallazgos principales resumidos
- Auto-asignación explicada
- Flujo completo: 2 escenarios (manual vs auto)
- Puntos bien implementados ✅
- Consideraciones futuras ⚠️
- Recomendaciones 💡
- Índice rápido de ubicaciones

**Ideal para:** Ejecutivos, resumen rápido, puntos clave

---

## 🔥 Lo Más Importante

### 1. Cambio Arquitectónico Clave
```
GET /api/v1/appointments/availability/slots
├─ Con trabajador_id: slots de ESE trabajador específico
└─ Sin trabajador_id=null: slots de TODOS los profesionales
```

### 2. Creación de Cita
```json
POST /api/v1/appointments
{
  "cliente_id": 42,
  "servicio_id": 5,
  "trabajador_id": 7,      ← REQUERIDO (o null para auto-asignar)
  "hora_inicio": "2026-04-15T14:30:00",
  "nota": "opcional"
}
```

### 3. Auto-asignación
```json
{
  "trabajador_id": null    ← Backend elige el primer disponible
}
```

### 4. Validaciones Críticas
- ✓ Trabajador existe
- ✓ Trabajador ofrece servicio (tabla M:N `trabajador_servicio`)
- ✓ Sin conflicto de horario
- ✓ Dentro del schedule del trabajador

---

## 📋 Flujo de Lectura Recomendado

### Si tienes 10 minutos:
1. Este archivo (resumen)
2. [CONCLUSIONES_PUNTOS_CLAVE_2026-04-14.md](CONCLUSIONES_PUNTOS_CLAVE_2026-04-14.md) (5 min)

### Si tienes 30 minutos:
1. [DIAGRAMAS_RELACIONES_FLUJOS_2026-04-14.md](DIAGRAMAS_RELACIONES_FLUJOS_2026-04-14.md) (10 min)
2. [USO_CREACION_CITAS_CON_TRABAJADORES.md](booksmart_pwa/docs/usos/USO_CREACION_CITAS_CON_TRABAJADORES.md) - Primeras 3 secciones (20 min)

### Si tienes 1 hora (Developer):
1. [USO_CREACION_CITAS_CON_TRABAJADORES.md](booksmart_pwa/docs/usos/USO_CREACION_CITAS_CON_TRABAJADORES.md) - Todo (30 min)
2. [QUICK_REFERENCE_ENDPOINTS_2026-04-14.md](QUICK_REFERENCE_ENDPOINTS_2026-04-14.md) - Endpoints completos (20 min)
3. Testing en postman/curl

### Si necesitas profundizar:
1. Todos los documentos en orden
2. [ANALISIS_BACKEND_CITAS_TRABAJADORES_2026-04-14.md](ANALISIS_BACKEND_CITAS_TRABAJADORES_2026-04-14.md) - Reference completo

---

## ✅ Checklist: Cambios Implementados

### Backend ✓ Hecho
- [x] Modelos: Worker, Appointment con `trabajo_id` REQUERIDO
- [x] M:N: WorkerService (worker puede hacer múltiples servicios)
- [x] CRUD: Auto-asignación inteligente si `trabajador_id = null`
- [x] Validaciones: Trabajador ofrece servicio
- [x] Endpoint: `/availability/slots` con filtro `trabajador_id`
- [x] 6 endpoints principales para citas

### Frontend 📝 Documentación Nueva
- [x] Guía completa: `USO_CREACION_CITAS_CON_TRABAJADORES.md`
- [x] Ejemplos de componentes Angular
- [x] Estructura de servicios TypeScript
- [x] DTOs y validaciones
- [x] Casos de uso completos

### A Implementar en Frontend
- [ ] Actualizar `AppointmentService` con nuevo `getAvailableSlots(servicioId, date, trabajadorId?)`
- [ ] Componente de reserva: selector de trabajador
- [ ] Componente de reserva: opción de auto-asignación
- [ ] Calendario de trabajador: filtro por `trabajador_id`
- [ ] Manejo de errores específicos

---

## 🔗 Relaciones Clave

```
Usuario (1:N) Trabajador
     ┌──────────────┴─────────────┐
     │                            │
   Owner               Worker (perfil en negocio)
[owner-only]          [nuevo rol posible]

Negocio (1:N) Trabajador
     │
     ├─→ Trabajador (1:N) Servicio [M:N table]
     │
     └─→ Negocio (1:N) Cita
            ├─→ Cliente (User)
            ├─→ Servicio
            └─→ Trabajador ← CAMBIO: Obligatorio ahora
```

---

## 🎓 Glosario de Términos

- **Trabajador**: Especialista que ofrece servicios (antes User, ahora Worker)
- **Cita (Appointment)**: Reserva de un cliente con un trabajador específico
- **Slot**: Intervalo de tiempo disponible en el calendario de un trabajador
- **Auto-asignación**: Sistema asigna automáticamente un trabajador disponible
- **M:N Table**: Tabla intermedia (WorkerService) para relación muchos-a-muchos
- **Agenda**: Horarios de trabajo por día de semana del negocio
- **SpecialClosure**: Cierre especial (feriado, licencia, etc.)

---

## 📞 Si Tienes Dudas

Consulta primero:
1. **Sobre implementación Frontend**: [USO_CREACION_CITAS_CON_TRABAJADORES.md](booksmart_pwa/docs/usos/USO_CREACION_CITAS_CON_TRABAJADORES.md)
2. **Sobre endpoints**: [QUICK_REFERENCE_ENDPOINTS_2026-04-14.md](QUICK_REFERENCE_ENDPOINTS_2026-04-14.md)
3. **Sobre arquitectura**: [ANALISIS_BACKEND_CITAS_TRABAJADORES_2026-04-14.md](ANALISIS_BACKEND_CITAS_TRABAJADORES_2026-04-14.md)
4. **Visualmente**: [DIAGRAMAS_RELACIONES_FLUJOS_2026-04-14.md](DIAGRAMAS_RELACIONES_FLUJOS_2026-04-14.md)

---

**Generado:** 2026-04-14  
**Estado:** Documentación Operativa ✅  
**Última revisión:** Backend commit a4db821 (2026-04-12)
