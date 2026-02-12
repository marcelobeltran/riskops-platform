# Arquitectura del Sistema: RiskOps Platform

## 1. Módulos y Apps (Estructura Django)
Respetando el principio de segregación, pero manteniendo simplicidad para el MVP:

- **`core`**:
    - Base models (`TimeStampedModel`), Mixins de auditoría.
    - Custom Admin Sites/Dashboard views.
- **`risk_universe`** (Domain):
    - `Process`, `RiskCategory`, `Risk`.
    - Lógica de cálculo de matrices.
- **`controls`** (Library):
    - `Control`, `ControlAssessment`.
- **`monitoring`** (Operational):
    - `KRI`, `RiskEvent`, `ActionPlan`.

## 2. Decisiones de Arquitectura
- **Template Engine**: Django Templates (DTL). Uso de `admin/base.html` extendido para páginas custom (Dashboard, Matriz).
- **CSS**: Uso del CSS del admin de Django + un pequeño `custom_admin.css` para la matriz de calor y semáforos, evitando introducir frameworks pesados de frontend.
- **Chart Library**: (Opcional) Chart.js simple vía CDN si se requiere gráfico, pero priorizaremos HTML/CSS Grids para la matriz y tablas para el resto.

## 3. Auditoría y Trazabilidad (Compliance)
- **Librería**: `django-simple-history`.
- **Configuración**: Registrar todos los modelos críticos (`Risk`, `Control`, `KRI`, `ActionPlan`).
- **Visualización**: El botón "History" en el admin permite ver quién cambió qué, valor anterior y nuevo, y fecha.

## 4. Seguridad
- **Authentication**: `django.contrib.auth`.
- **Authorization**:
    - **Risk Managers**: Full CRUD.
    - **Process Owners**: Read-only o Edit limitado (a definir en settings).
    - **Auditors**: Read-only + View History.
- **Data Protection**:
    - Evitar exponer IDs secuenciales en URLs públicas (aunque en Admin es standard).
    - CSRF Protection activado por defecto.
