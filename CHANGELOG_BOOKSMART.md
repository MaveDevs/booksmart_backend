# Bitácora de Cambios Backend - Booksmart
**Fecha:** 2026-04-09
**Objetivo:** Optimización de la arquitectura multi-perfil, enriquecimiento de datos en la API y mejoras en la lógica de seguridad y vinculación.

---

## 🛠️ Refactorización de Modelos y Relaciones (`app/models/`)

### 1. Sistema de Perfiles Flexibles
- **User -> Worker**: Se cambió la relación de **1:1 a 1:N** (eliminando `uselist=False`). Un usuario ahora puede tener múltiples perfiles de trabajador en diferentes negocios.
- **Worker**: Se eliminó la restricción de `unique=True` en el campo `email` para permitir la reutilización de correos en pruebas y re-vinculaciones sin bloqueos de base de datos.

### 2. Propiedades de Identidad (Resolución de Nombres)
- **Appointment**: Se añadieron propiedades calculadas (`cliente_nombre`, `trabajador_nombre`, `trabajador_apellido`, `servicio_nombre`) que resuelven dinámicamente el texto desde sus respectivas relaciones.
- **Review**: Se añadió la propiedad `usuario_nombre` para permitir mostrar el nombre del cliente en las reseñas sin consultas adicionales.

---

## 🏗️ Mejoras en Lógica de Negocio y CRUD (`app/crud/`)

### 1. Gestión de Trabajadores
- **Vinculación Inteligente**: Se ajustó `create_worker` para buscar usuarios existentes por correo y vincularlos por `usuario_id` en lugar de crear duplicados.
- **Seguridad**: Se corrigió el manejo de contraseñas para asegurar que, si se asigna una contraseña manual al trabajador, esta se hashee correctamente y no sea sobrescrita por valores por defecto.

### 2. Aislamiento de Datos y Seguridad (Multi-tenancy)
- **Corrección de Leakage Crítico**: Se resolvió un error donde los dueños veían citas y mensajes de todos sus negocios de forma simultánea. Se implementó un sistema de aislamiento estricto mediante `establishment_id`.
- **Citas (Eager Loading)**: Se implementó `joinedload` en `get_appointments` y `get_appointment` para traer la información del Cliente, Trabajador y Servicio en una sola consulta SQL, eliminando el problema de "N+1" y asegurando que los nombres lleguen a la API.
- **Filtros CRUD**: Se añadió soporte para filtrar citas por `establishment_id` realizando un JOIN forzado con la tabla de servicios en `crud_appointments`.

### 3. Búsqueda de Establecimientos
- **Estrategia Híbrida**: Se refactorizó la búsqueda de negocios para trabajadores usando un sistema de **ID + Email Fallback**. Esto garantiza que el trabajador vea su negocio incluso si la vinculación de ID es inconsistente.

---

## 🔌 API y Endpoints (`app/api/v1/`)

### 1. Endpoint de Citas
- Se actualizó el endpoint `/appointments/` para aceptar `establishment_id` como parámetro de consulta.
- **Validación de Propiedad**: Se implementó una verificación de autoría para Dueños: ahora el servidor valida que el negocio pertenezca al usuario antes de entregar los datos, garantizando privacidad entre perfiles.

### 2. Endpoint de Reseñas (Ratings)
- **Sincronización de Parámetros**: Se normalizó el filtrado por `establecimiento_id` para resolver la inconsistencia que impedía el aislamiento de ratings por negocio.

### 2. Esquemas de Respuesta (`app/schemas/`)
- **AppointmentResponse**: Enriquecido con todos los campos de identidad (nombres de personas y servicios).
- **ReviewResponse**: Enriquecido con el nombre del usuario.

---
*Este documento resume exclusivamente las intervenciones en la infraestructura del servidor realizadas durante el día.*
