# Creación de Citas con Trabajadores - Guía Frontend

**Versión:** 2026-04-14  
**Estado:** Documentación Operativa  
**Cambio Principal:** Las citas ahora están vinculadas al calendario de UN trabajador específico, no al calendario general del negocio.

---

## 📋 Tabla de Contenidos
1. [Cambio Arquitectónico](#cambio-arquitectónico)
2. [Flujo de Creación de Citas](#flujo-de-creación-de-citas)
3. [Componentes Frontend Involucrados](#componentes-frontend-involucrados)
4. [Servicio de Citas (AppointmentService)](#servicio-de-citas)
5. [Estructura de Datos](#estructura-de-datos)
6. [Validaciones y Reglas](#validaciones-y-reglas)
7. [Ejemplos de Implementación](#ejemplos-de-implementación)
8. [Manejo de Errores](#manejo-de-errores)
9. [Casos de Uso Completos](#casos-de-uso-completos)

---

## 🏗️ Cambio Arquitectónico

### Antes (Sin Trabajadores):
```
1 Negocio → 1 Calendario → N Citas máximo 1 por slot horario
Disponibilidad: Depende de horarios del negocio + cierres especiales
```

### Ahora (Con Trabajadores):
```
1 Negocio → N Trabajadores → Cada uno con su calendario
           └─ Trabajador 1 → Calendario propio → N Citas
           └─ Trabajador 2 → Calendario propio → N Citas
           
Disponibilidad: 
- Depende de horarios del negocio
- Depende del horario específico de cada TRABAJADOR
- Depende de citas ya agendadas para ese TRABAJADOR
- Auto-asignación: Si no especificas trabajador, elige el primero disponible
```

### Implicaciones:
| Aspecto | Anterior | Ahora |
|--------|----------|-------|
| **Asignación** | Automática (1 slot) | Manual O auto (por trabajador) |
| **Disponibilidad** | 1 lista por negocio | 1 lista por trabajador |
| **Citas simultáneas** | No (1 por slot) | Sí (si hay múltiples trabajadores) |
| **Calendario** | 1 por negocio | 1 por trabajador |
| **Permisos** | Cliente → Negocio | Cliente → Especialista específico |

---

## 🔄 Flujo de Creación de Citas

### Caso 1: Creación con Trabajador Específico
```
┌─────────────────────────────────────────────────┐
│ A. Usuario selecciona date, hora, servicio      │
├─────────────────────────────────────────────────┤
│ B. Frontend llama: GET /availability/slots      │
│    - servicio_id: ID del servicio               │
│    - target_date: Fecha deseada                 │
│    - trabajador_id: ID del trabajador (opcional)│
├─────────────────────────────────────────────────┤
│ C. Backend retorna: Lista de slots para ese día │
│    Si trabajador_id -> slots del trabajador     │
│    Si null -> slots de TODOS los trabajadores   │
├─────────────────────────────────────────────────┤
│ D. Usuario elige hora + trabajador (si auto)    │
├─────────────────────────────────────────────────┤
│ E. POST /appointments                           │
│    {                                            │
│      cliente_id: ...,                           │
│      servicio_id: ...,                          │
│      trabajador_id: ..., (REQUERIDO ahora)      │
│      hora_inicio: ...,                          │
│      nota: ...                                  │
│    }                                            │
├─────────────────────────────────────────────────┤
│ F. Backend:                                     │
│    - Valida que trabajador ofrece servicio      │
│    - Valida sin conflictos de horario           │
│    - Calcula hora_fin automáticamente           │
│    - Retorna cita creada                        │
└─────────────────────────────────────────────────┘
```

### Caso 2: Auto-asignación (trabajador_id = null)
```
┌──────────────────────────────────────────────────┐
│ A. Usuario selecciona date, hora, servicio      │
├──────────────────────────────────────────────────┤
│ B. Frontend NO especifica trabajador_id (null)  │
├──────────────────────────────────────────────────┤
│ C. POST /appointments                           │
│    {                                            │
│      cliente_id: ...,                           │
│      servicio_id: ...,                          │
│      trabajador_id: null, ← Auto-asignación     │
│      hora_inicio: ...,                          │
│      nota: ...                                  │
│    }                                            │
├──────────────────────────────────────────────────┤
│ D. Backend:                                     │
│    1. Busca trabajadores que hacen el servicio  │
│    2. Filtra los disponibles en esa fecha/hora  │
│    3. Asigna al PRIMERO disponible              │
│    4. Retorna cita con trabajador_id asignado   │
│    5. Si ninguno disponible → Error 409         │
└──────────────────────────────────────────────────┘
```

---

## 🎯 Componentes Frontend Involucrados

### 1. **Componente: Selección de Horarios**
**Ubicación:** `src/app/pages/agendas/`  
**Responsabilidades:**
- Obtener trabajadores disponibles del negocio
- Llamar a `/availability/slots` para ese trabajador
- Mostrar horarios disponibles (grid de horas)
- Permitir seleccionar un slot + trabajador

**Cambios necesarios:**
- ✅ Pasar `trabajador_id` al llamar a `/availability/slots`
- ✅ Mostrar nombre del trabajador en cada slot
- ✅ Permitir alternancia entre "ver slots de trabajador X" vs "ver todos"

### 2. **Componente: Formulario de Cita**
**Ubicación:** `src/app/pages/agendas/` o modal similar  
**Responsabilidades:**
- Seleccionar servicio
- Mostrar trabajadores disponibles (si manual)
- Mostrar horarios
- Capturar notas opcionales
- Enviar POST a `/appointments`

**Cambios necesarios:**
- ✅ Campo obligatorio: `trabajador_id` (select dropdown)
- ✅ Opción "Auto-asignar" que deja `trabajador_id = null`
- ✅ Mostrar especialistación del trabajador (qué servicios hace)

### 3. **Servicio: AppointmentService**
**Ubicación:** `src/app/services/appointment.service.ts`  
**Responsabilidades:**
- Comunicar con endpoints `/appointments`
- Gestionar estado de citas locales
- Manejar filtrados y búsquedas

**Cambios necesarios:**
- ✅ Método `getAvailableSlots(servicioId, targetDate, trabajadorId?)`
- ✅ Método `createAppointment(appointment)` con `trabajador_id` requerido
- ✅ Método `getAppointmentsByWorker(trabajadorId, filters?)`

### 4. **Servicio: WorkerService**
**Ubicación:** `src/app/services/worker.service.ts`  
**Responsabilidades:**
- Obtener lista de trabajadores del negocio
- Obtener perfil del trabajador actual (para workers)
- Datos de especialización (servicios que ofrece)

**Métodos disponibles:**
- `getWorkers(establishmentId)` → Lista de trabajadores
- `getWorkerServices(workerId)` → Servicios que ofrece
- `getMyWorkerProfile()` → Datos del trabajador logueado

---

## 💾 Servicio de Citas

### AppointmentService - Métodos Principales

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AppointmentService {
  private apiBase = '/api/v1/appointments';
  private appointmentsSubject = new BehaviorSubject<Appointment[]>([]);

  appointments$ = this.appointmentsSubject.asObservable();

  constructor(private http: HttpClient) {}

  /**
   * Obtener slots disponibles para un servicio en una fecha
   * 
   * @param servicioId - ID del servicio
   * @param targetDate - Fecha en formato YYYY-MM-DD
   * @param trabajadorId - (Opcional) Filtrar por trabajador específico
   * 
   * @returns Array de slots available
   * 
   * IMPORTANTE: Si trabajador_id es null, devuelve slots combinados de TODOS los 
   * trabajadores que ofrecen ese servicio
   */
  getAvailableSlots(
    servicioId: number,
    targetDate: string,
    trabajadorId?: number
  ): Observable<AvailableSlot[]> {
    let url = `${this.apiBase}/availability/slots?servicio_id=${servicioId}&target_date=${targetDate}`;
    if (trabajadorId) {
      url += `&trabajador_id=${trabajadorId}`;
    }
    return this.http.get<AvailableSlot[]>(url);
  }

  /**
   * Crear una nueva cita
   * 
   * @param appointment - Datos de la cita
   * REQUERIDO: appointment.trabajador_id (no puede ser null en creación)
   * 
   * @returns Cita creada con ID asignado
   * 
   * Validaciones en backend:
   * - Cliente existe
   * - Trabajador existe y pertenece al negocio
   * - Trabajador ofrece el servicio
   * - No hay conflicto de horario
   * - hora_fin > hora_inicio
   */
  createAppointment(appointment: CreateAppointmentDTO): Observable<Appointment> {
    // Si trabajador_id es null, backend hace auto-asignación
    return this.http.post<Appointment>(
      `${this.apiBase}`,
      appointment
    );
  }

  /**
   * Obtener citas de un trabajador
   */
  getWorkerAppointments(
    trabajadorId: number,
    filters?: AppointmentFilters
  ): Observable<Appointment[]> {
    let url = `${this.apiBase}?trabajador_id=${trabajadorId}`;
    if (filters?.status) {
      url += `&status=${filters.status}`;
    }
    if (filters?.from_date) {
      url += `&from_date=${filters.from_date}`;
    }
    if (filters?.to_date) {
      url += `&to_date=${filters.to_date}`;
    }
    return this.http.get<Appointment[]>(url);
  }

  /**
   * Obtener citas del negocio (filtradas opcionalmente por trabajador)
   */
  getBusinessAppointments(
    establishmentId: number,
    trabajadorId?: number
  ): Observable<Appointment[]> {
    let url = `${this.apiBase}?establishment_id=${establishmentId}`;
    if (trabajadorId) {
      url += `&trabajador_id=${trabajadorId}`;
    }
    return this.http.get<Appointment[]>(url);
  }

  /**
   * Actualizar una cita (cambiar status, notas, etc)
   */
  updateAppointment(
    appointmentId: number,
    update: Partial<Appointment>
  ): Observable<Appointment> {
    return this.http.patch<Appointment>(
      `${this.apiBase}/${appointmentId}`,
      update
    );
  }

  /**
   * Aceptar una cita (cambiar status a 'accepted')
   */
  acceptAppointment(appointmentId: number): Observable<Appointment> {
    return this.http.post<Appointment>(
      `${this.apiBase}/${appointmentId}/accept`,
      {}
    );
  }

  /**
   * Rechazar una cita
   */
  declineAppointment(appointmentId: number): Observable<Appointment> {
    return this.http.post<Appointment>(
      `${this.apiBase}/${appointmentId}/decline`,
      {}
    );
  }

  /**
   * Eliminar una cita
   */
  deleteAppointment(appointmentId: number): Observable<void> {
    return this.http.delete<void>(
      `${this.apiBase}/${appointmentId}`
    );
  }
}
```

---

## 📦 Estructura de Datos

### DTO: CreateAppointmentDTO
```typescript
interface CreateAppointmentDTO {
  // REQUERIDO: Cliente que hace la cita
  cliente_id: number;
  
  // REQUERIDO: Servicio a contratar
  servicio_id: number;
  
  // REQUERIDO AHORA: Trabajador que realiza el servicio
  // Si es null → auto-asignación (backend busca disponible)
  trabajador_id: number | null;
  
  // REQUERIDO: Hora de inicio (formato: HH:MM o ISO 8601)
  hora_inicio: string; // ej: "14:30"
  
  // OPCIONAL: Nota de cliente (especificaciones, alergias, etc)
  nota?: string;
}
```

### DTO: AvailableSlot
```typescript
interface AvailableSlot {
  // ID del trabajador que tiene este slot disponible
  trabajador_id: number;
  
  // Nombre del trabajador
  worker_name: string;
  
  // Hora de inicio disponible
  hora_inicio: string; // ej: "14:30"
  
  // Hora de fin (calculada según duración del servicio)
  hora_fin: string; // ej: "15:00"
  
  // Duración del servicio en minutos
  duracion_minutos: number;
}
```

### DTO: Appointment (Respuesta Completa)
```typescript
interface Appointment {
  // Identificadores
  id: number;
  establecimiento_id: number;
  cliente_id: number;
  
  // TRABAJADOR ESPECÍFICO (cambio principal)
  trabajador_id: number;
  
  // Servicio
  servicio_id: number;
  
  // Tiempos
  hora_inicio: string; // "2026-04-15T14:30:00"
  hora_fin: string;    // "2026-04-15T15:00:00"
  fecha: string;       // "2026-04-15"
  
  // Estado
  status: 'pending' | 'accepted' | 'declined' | 'completed' | 'cancelled';
  
  // Datos enriquecidos (computed fields del backend)
  client_name: string;
  worker_name: string;
  service_name: string;
  
  // Metadatos
  nota?: string;
  created_at: string;
  updated_at: string;
}
```

---

## ✅ Validaciones y Reglas

### Validación de Creación de Cita

```typescript
// Reglas que aplica el backend automáticamente:

✓ CLIENTE
  - Existe en la BD
  - Pertenece al negocio (establecimiento_id)

✓ SERVICIO
  - Existe
  - Está activo (no archivado)

✓ TRABAJADOR (si especificado)
  - Existe
  - Pertenece al negocio (establecimiento_id)
  - OFRECE el servicio (relación M:N en table trabajador_servicio)
  - Sus horarios incluyen la hora_inicio solicitada

✓ DISPONIBILIDAD
  - Sin conflicto: No hay otra cita del MISMO trabajador en ese horario
  - La hora_fin se calcula automáticamente (siempre mayor que hora_inicio)

✓ HORARIOS DEL NEGOCIO
  - La hora_inicio está dentro del schedule del negocio ese día
  - No coincide con cierres especiales (SpecialClosure)

✓ TURNO DEL TRABAJADOR
  - El trabajador trabaja ese día (día de semana)
  - La hora está dentro del turno específico del trabajador
```

### Errores Comunes

```typescript
// Error 400: Validación fallida
{
  "detail": "Trabajador no ofrece este servicio",
  "error_code": "WORKER_INVALID_SERVICE"
}

// Error 404: Recurso no encontrado
{
  "detail": "Trabajador no encontrado",
  "error_code": "WORKER_NOT_FOUND"
}

// Error 409: Conflicto (horario ocupado)
{
  "detail": "Conflicto de horario: trabajador ocupado",
  "error_code": "SCHEDULE_CONFLICT"
}

// Error 422: No hay disponibilidad
{
  "detail": "No hay trabajadores disponibles",
  "error_code": "NO_AVAILABILITY"
}
```

---

## 💡 Ejemplos de Implementación

### Ejemplo 1: Componente para Crear Cita (Simple)

```typescript
// example-create-appointment.component.ts

import { Component, OnInit } from '@angular/core';
import { AppointmentService } from '@app/services/appointment.service';
import { WorkerService } from '@app/services/worker.service';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-create-appointment',
  templateUrl: './create-appointment.component.html'
})
export class CreateAppointmentComponent implements OnInit {
  // Formulario
  clientId: number;
  serviceId: number;
  workerId: number | null = null; // null = auto-asignar
  selectedDate: string;
  selectedTime: string;
  notes: string = '';

  // Datos disponibles
  workers$ = this.workerService.getEstablishmentWorkers(this.currentEstablishmentId);
  availableSlots$ = new Observable<AvailableSlot[]>();
  
  isLoading = false;
  isAutoAssign = true;

  constructor(
    private appointmentService: AppointmentService,
    private workerService: WorkerService,
    private toastr: ToastrService
  ) {}

  ngOnInit() {
    // Cargar trabajadores del negocio actual
    this.workers$.subscribe({
      next: (workers) => {
        console.log('Trabajadores disponibles:', workers);
      }
    });
  }

  /**
   * Cuando usuario selecciona: servicio + fecha + trabajador(opt)
   * Obtener slots disponibles
   */
  onDateChange() {
    if (!this.serviceId || !this.selectedDate) {
      return;
    }

    this.isLoading = true;

    // Si es auto-asignación, NO pasar trabajador_id
    const trabajadorId = this.isAutoAssign ? undefined : this.workerId;

    this.availableSlots$ = this.appointmentService
      .getAvailableSlots(this.serviceId, this.selectedDate, trabajadorId)
      .pipe(
        tap(() => { this.isLoading = false; }),
        catchError(err => {
          this.toastr.error('No hay disponibilidad para esta fecha');
          this.isLoading = false;
          return of([]);
        })
      );
  }

  /**
   * Cuando usuario selecciona un slot
   */
  onSlotSelect(slot: AvailableSlot) {
    this.selectedTime = slot.hora_inicio;
    
    // Para auto-asignación, usar el trabajador del slot
    if (this.isAutoAssign) {
      this.workerId = slot.trabajador_id;
    }
  }

  /**
   * Enviar la cita
   */
  onSubmit() {
    if (!this.clientId || !this.serviceId || !this.workerId || !this.selectedDate) {
      this.toastr.error('Por favor completa todos los campos');
      return;
    }

    const appointmentData: CreateAppointmentDTO = {
      cliente_id: this.clientId,
      servicio_id: this.serviceId,
      trabajador_id: this.workerId,
      hora_inicio: `${this.selectedDate}T${this.selectedTime}:00`,
      nota: this.notes
    };

    this.isLoading = true;

    this.appointmentService.createAppointment(appointmentData).subscribe({
      next: (appointment) => {
        this.toastr.success(
          `Cita confirmada con ${appointment.worker_name} a las ${appointment.hora_inicio}`
        );
        this.resetForm();
      },
      error: (err) => {
        const message = err.error?.detail || 'Error al crear cita';
        this.toastr.error(message);
        console.error('Error creating appointment:', err);
      },
      complete: () => { this.isLoading = false; }
    });
  }

  private resetForm() {
    this.clientId = null;
    this.serviceId = null;
    this.workerId = null;
    this.selectedDate = '';
    this.selectedTime = '';
    this.notes = '';
  }
}
```

```html
<!-- example-create-appointment.component.html -->

<div class="appointment-form">
  <form>
    <!-- Seleccionar Servicio -->
    <div class="form-group">
      <label>Servicio</label>
      <select [(ngModel)]="serviceId" (change)="onDateChange()">
        <option value="">-- Selecciona servicio --</option>
        <!-- Iterar servicios -->
      </select>
    </div>

    <!-- Seleccionar Fecha -->
    <div class="form-group">
      <label>Fecha</label>
      <input 
        type="date" 
        [(ngModel)]="selectedDate" 
        (change)="onDateChange()"
      />
    </div>

    <!-- Auto-asignación vs Manual -->
    <div class="form-group">
      <label>
        <input type="checkbox" [(ngModel)]="isAutoAssign" />
        Auto-asignar trabajador disponible
      </label>
    </div>

    <!-- Seleccionar Trabajador (si NO auto) -->
    <div class="form-group" *ngIf="!isAutoAssign">
      <label>Trabajador Especialista</label>
      <select [(ngModel)]="workerId" (change)="onDateChange()">
        <option value="">-- Selecciona especialista --</option>
        <option *ngFor="let w of (workers$ | async)" [value]="w.id">
          {{ w.name }} ({{ w.services.length }} servicios)
        </option>
      </select>
    </div>

    <!-- Slots Disponibles -->
    <div class="slots-grid" *ngIf="(availableSlots$ | async) as slots">
      <div 
        *ngFor="let slot of slots"
        class="slot-card"
        [class.selected]="selectedTime === slot.hora_inicio && workerId === slot.trabajador_id"
        (click)="onSlotSelect(slot)"
      >
        <div class="slot-time">{{ slot.hora_inicio }} - {{ slot.hora_fin }}</div>
        <div class="slot-worker">Con: {{ slot.worker_name }}</div>
      </div>
    </div>

    <!-- Notas Opcionales -->
    <div class="form-group">
      <label>Notas especiales (opcional)</label>
      <textarea [(ngModel)]="notes" placeholder="Indicaciones del cliente..."></textarea>
    </div>

    <!-- Botón Enviar -->
    <button 
      type="button"
      (click)="onSubmit()"
      [disabled]="isLoading"
      class="btn btn-primary"
    >
      {{ isLoading ? 'Creando...' : 'Confirmar Cita' }}
    </button>
  </form>
</div>
```

### Ejemplo 2: Obtener Citas de un Trabajador

```typescript
// Ver citas asignadas a un trabajador específico

export class WorkerCalendarComponent implements OnInit {
  workerId: number;
  appointments$: Observable<Appointment[]>;

  constructor(private appointmentService: AppointmentService) {}

  ngOnInit() {
    // Cargar citas del trabajador con filtros
    this.appointments$ = this.appointmentService.getWorkerAppointments(
      this.workerId,
      {
        status: 'accepted', // Solo citas aceptadas
        from_date: '2026-04-14',
        to_date: '2026-04-20'
      }
    );
  }
}
```

### Ejemplo 3: Auto-asignación

```typescript
// El cliente NO elige trabajador - el sistema auto-asigna

const appointment: CreateAppointmentDTO = {
  cliente_id: 42,
  servicio_id: 5, // Masaje Relajante
  trabajador_id: null, // ← IMPORTANTE: null activa auto-asignación
  hora_inicio: '2026-04-15T14:30:00',
  nota: 'Cliente prefiere masaje suave'
};

this.appointmentService.createAppointment(appointment).subscribe({
  next: (result) => {
    // result.trabajador_id tendrá el ID del trabajador asignado
    console.log(`Auto-asignado a: ${result.worker_name}`);
  }
});
```

---

## 🚨 Manejo de Errores

### Escenarios de Error Comunes

```typescript
// Combinación de errores que pueden ocurrir:

// 1. Trabajador no ofrece servicio
POST /api/v1/appointments
{ trabajador_id: 10, servicio_id: 3 }
→ 400: "Trabajador 10 no ofrece servicio 3"

// 2. Conflicto de horario
POST /api/v1/appointments
{ trabajador_id: 10, hora_inicio: "14:30", ... }
→ 409: "Trabajador 10 ya tiene cita de 14:00 a 15:00"

// 3. Horario fuera del turno del trabajador
POST /api/v1/appointments
{ trabajador_id: 10, hora_inicio: "22:00", ... } // Después de su cierre
→ 422: "Horario fuera del turno del trabajador"

// 4. Sin disponibilidad (auto-asignación)
POST /api/v1/appointments
{ trabajador_id: null, hora_inicio: "15:00" }
→ 503: "No hay trabajadores disponibles para ese horario"

// 5. Cliente no existe
POST /api/v1/appointments
{ cliente_id: 9999 }
→ 404: "Cliente no encontrado"
```

### Manejo Robusto

```typescript
private handleAppointmentError(error: any): string {
  const detail = error.error?.detail || 'Error desconocido';
  const errorCode = error.error?.error_code;

  switch (errorCode) {
    case 'WORKER_INVALID_SERVICE':
      return `El especialista no ofrece este servicio`;
    
    case 'SCHEDULE_CONFLICT':
      return `Horario no disponible - el especialista tiene otra cita`;
    
    case 'WORKER_NOT_FOUND':
      return `El especialista seleccionado no existe`;
    
    case 'CLIENT_NOT_FOUND':
      return `Cliente no encontrado en el sistema`;
    
    case 'NO_AVAILABILITY':
      return `No hay disponibilidad para esa fecha y hora`;
    
    case 'INVALID_TIME_RANGE':
      return `Horario inválido - revisa las horas`;
    
    default:
      return detail;
  }
}
```

---

## 📚 Casos de Uso Completos

### Caso 1: Cliente Reserva con Profesional Específico

```
ESCENARIO: Cliente quiere manicura con la manicurista "María"

1. Usuario abre página de reserva
2. Selecciona: Servicio = "Manicura" (ID: 5)
3. Selecciona: Fecha = 2026-04-20
4. Sistema carga especialistas que hacen manicura
5. Usuario ve: "María", "Sofía", "Laura"
6. Usuario selecciona: María
7. Sistema llama: GET /availability/slots?servicio_id=5&target_date=2026-04-20&trabajador_id=7 (María)
8. Respuesta: [ { hora_inicio: "09:00", hora_fin: "09:30", worker: María }, ... ]
9. Usuario selecciona: "09:00 - 09:30"
10. Usuario hace click: "Confirmar"
11. POST /appointments
    {
      cliente_id: 42,
      servicio_id: 5,
      trabajador_id: 7,      ← María específicamente
      hora_inicio: "2026-04-20T09:00:00",
      nota: "Me gusta esmaltado mate"
    }
12. Backend valida y crea
13. Usuario ve confirmación: "Manicura confirmada con María el 20/04 a las 09:00"
```

### Caso 2: Auto-asignación - Sistema Elige

```
ESCENARIO: Cliente quiere depilación, no le importa quién

1. Usuario abre página de reserva
2. Selecciona: Servicio = "Depilación" (ID: 8)
3. Selecciona: Fecha = 2026-04-21
4. Usuario marca: ☑ "Auto-asignar profesional disponible"
5. Sistema llama: GET /availability/slots?servicio_id=8&target_date=2026-04-21
   (SIN trabajador_id → devuelve slots de TODOS los depiladores)
6. Respuesta:
   [
     { hora_inicio: "10:00", worker_id: 5, worker_name: "Carla" },
     { hora_inicio: "10:30", worker_id: 9, worker_name: "Verónica" },
     { hora_inicio: "14:00", worker_id: 5, worker_name: "Carla" },
   ]
7. Usuario selecciona: "10:00"
8. POST /appointments
    {
      cliente_id: 42,
      servicio_id: 8,
      trabajador_id: 5,      ← Se autoseleccionó Carla del slot
      hora_inicio: "2026-04-21T10:00:00"
    }
9. Cita confirmada con Carla
```

### Caso 3: Trabajador Ve Sus Citas

```
ESCENARIO: María (trabajador) abre su calendario laboral

1. María hace login (rol: WORKER)
2. Sistema detecta su perfil: trabajador_id = 7
3. Frontend llama: GET /appointments?trabajador_id=7&status=accepted
4. Backend retorna: Todas las citas asignadas a María
   [
     { id: 101, cliente: Juan, servicio: Corte, fecha: 2026-04-14 14:00 },
     { id: 102, cliente: Rosa, servicio: Tinte, fecha: 2026-04-14 15:30 },
     { id: 103, cliente: Pedro, servicio: Barba, fecha: 2026-04-15 09:00 },
   ]
5. María ve su calendario personalizado
6. María puede:
   - Accept/Decline citas (pending)
   - Ver notas del cliente
   - Marcar como completada
```

### Caso 4: Dueño Asigna Citas a Trabajador (Admin)

```
ESCENARIO: Dueño manualmente asigna citas desde tab "Equipo"

1. Dueño está en tab "Equipo" del negocio
2. Ve lista de trabajadores: María, Sofía, Laura
3. Ve citas sin asignar: { cliente: Carlos, servicio: Masaje, ...}
4. Dueño arrastra cita a "María"
5. Frontend POST /appointments con:
   {
     cliente_id: 80,
     servicio_id: 3,
     trabajador_id: 7,      ← Asignación manual del dueño
     hora_inicio: "2026-04-14T16:00:00"
   }
6. Cita se asigna a María
7. María recibe notificación de nueva cita
```

---

## 🔗 Conexión entre Componentes

```
┌──────────────────────────┐
│ ReservationPage          │
│ (Cliente hace reserva)   │
└────────────┬─────────────┘
             │
             ├─→ WorkerService.getEstablishmentWorkers()
             │   [Lista de profesionales]
             │
             ├─→ AppointmentService.getAvailableSlots(
             │     servicio_id, date, [trabajador_id]
             │   )
             │   [Horarios disponibles por trabajador]
             │
             └─→ AppointmentService.createAppointment()
                 [Crear cita con trabajador específico]

┌──────────────────────────┐
│ WorkerCalendarPage       │
│ (Trabajador ve su cal.)  │
└────────────┬─────────────┘
             │
             ├─→ WorkerService.getMyWorkerProfile()
             │   [Datos del trabajador logueado]
             │
             └─→ AppointmentService.getWorkerAppointments(
                   trabajador_id
                 )
                 [Citas asignadas a este trabajador]

┌──────────────────────────────┐
│ BusinessManagementPage       │
│ (Dueño administra negocio)   │
└────────────┬─────────────────┘
             │
             ├─→ WorkerService.getWorkers()
             │   [Todos los trabajadores]
             │
             ├─→ AppointmentService.getBusinessAppointments(
             │     establishment_id, [trabajador_id]
             │   )
             │   [Todas las citas o filtradas por trabajador]
             │
             └─→ AppointmentService.createAppointment()
                 [Asignar cita a un trabajador]
```

---

## 📝 Checklist de Implementación

- [ ] Servicio `AppointmentService` con método `getAvailableSlots(servicioId, date, trabajadorId?)`
- [ ] Servicio `AppointmentService` con método `createAppointment()` que envíe `trabajador_id`
- [ ] Servicio `WorkerService` con método `getEstablishmentWorkers()`
- [ ] Componente de reserva muestra lista de trabajadores
- [ ] Componente de reserva permite seleccionar trabajador O auto-asignar
- [ ] Componente de reserva carga slots específicos del trabajador
- [ ] Componente de calendario de trabajador filtra por `trabajador_id`
- [ ] Manejo de errores para "Trabajador no ofrece servicio"
- [ ] Manejo de errores para "Conflicto de horario"
- [ ] Manejo de errores para "Sin disponibilidad"
- [ ] Testing: Crear cita con trabajador específico
- [ ] Testing: Crear cita con auto-asignación (trabajador_id = null)
- [ ] Testing: Trabajador ve solo sus citas
- [ ] Documentación de API actualizada en frontend

---

## 🎓 Resumen de Cambios Principales

| Antes | Ahora | Impacto |
|-------|-------|---------|
| 1 calendario por negocio | 1 calendario por trabajador | Múltiples citas simultáneas posibles |
| Asignación automática | Manual O auto | Mayor control del cliente |
| `trabajador_id` opcional | `trabajador_id` requerido | Cada cita tied a especialista |
| Slots: solo negocio | Slots: por trabajador | Consultas más específicas |
| N/A | `GET /availability/slots?trabajador_id=X` | Nuevo endpoint clave |

---

**Última actualización:** 2026-04-14  
**Autor:** GitBook automation  
**Estado:** Operativo ✅
