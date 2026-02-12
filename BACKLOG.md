# Backlog - RiskOps Platform MVP Iteration 0

Este documento actúa como sustituto del Backlog de GitHub Issues para la Iteración 0.

## User Stories

### Gestión de Procesos y Riesgos
1. **[US-01] Gestión de Procesos**: Como Analista de Riesgo, quiero registrar Procesos con sus dueños y criticidad, para mapear el universo de riesgo.
    - *Criterio de Aceptación*: CRUD de Procesos disponible en Admin. Campos: Nombre, Descripción, Dueño, Criticidad.
2. **[US-02] Catálogo de Riesgos**: Como Analista, quiero registrar Riesgos asociándolos a Procesos, para tener un inventario.
    - *Criterio de Aceptación*: Modelo Riesgo vinculado a Proceso. Campos: Título, Descripción, Tipo.
3. **[US-03] Evaluación Inherente**: Como Analista, quiero calificar la Probabilidad e Impacto (1-5) de un riesgo, para calcular su nivel inherente.
    - *Criterio de Aceptación*: Campos Probabilidad/Impacto en Riesgo. Propiedad calculada o método `nivel_riesgo`.

### Controles y Mitigación
4. **[US-04] Inventario de Controles**: Como Arquitecto de Control, quiero documentar controles detallando quién, cómo y cuándo se ejecutan.
    - *Criterio de Aceptación*: CRUD Controles. Propiedades: Tipo (Prev/Det), Periodicidad, Automatización.
5. **[US-05] Asociación Riesgo-Control**: Como Analista, quiero vincular controles a riesgos, para documentar la mitigación.
    - *Criterio de Aceptación*: Relación Many-to-Many entre Riesgo y Control.

### Monitoreo (KRIs y Eventos)
6. **[US-06] Definición de KRIs**: Como Gestor, quiero definir indicadores (KRIs) con umbrales (Verde/Amarillo/Rojo).
    - *Criterio de Aceptación*: CRUD KRI. Campos umbrales numéricos.
7. **[US-07] Registro de Eventos/Incidentes**: Como Usuario, quiero reportar eventos de pérdida o incidentes, vinculándolos a riesgos materializados.
    - *Criterio de Aceptación*: CRUD Eventos. Fecha, Monto, Descripción, Riesgo Relacionado.

### Gobernanza
8. **[US-08] Planes de Acción**: Como Auditor, quiero crear planes de acción para riesgos altos o fallos de control.
    - *Criterio de Aceptación*: CRUD Planes. Fecha vencimiento, Responsable, Estado.
9. **[US-09] Auditoría de Cambios**: Como Auditor, quiero ver quién modificó un riesgo o control y cuándo.
    - *Criterio de Aceptación*: Historial de cambios visible en el Admin (usando `django-simple-history` o logging básico).

## Tasks Técnicas (Iteración 0)
- [ ] Configurar proyecto Django y App `risk_management`.
- [ ] Definir Modelos (Process, Risk, Control, KRI, Event, ActionPlan).
- [ ] Configurar Admin (filtros, búsquedas, inlines).
- [ ] Crear migraciones iniciales.
- [ ] Smoke Tests (verificar creación de objetos y cálculos simples).
