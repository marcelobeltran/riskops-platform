# Modelo de Dominio: RiskOps Platform

## 1. Glosario RO (Riesgo Operacional)
- **Riesgo Inherente**: Riesgo puro sin considerar controles.
- **Riesgo Residual**: Nivel de riesgo tras aplicar mitigantes.
- **Control Mitigante**: Acción que reduce P (Probabilidad) o I (Impacto).
- **Apetito de Riesgo**: Nivel de riesgo que la organización acepta perseguir.
- **Evento de Pérdida**: Impacto financiero materializado.
- **KRI**: Indicador métrico de exposición al riesgo.

## 2. Entidades

### Estructurales
- **Process**: Unidad de negocio/operativa.
    - *Estados*: Activo, Inactivo.
- **RiskCategory**: Taxonomía (e.g., RRHH, Fraude, Ciber).

### Evaluación de Riesgo
- **Risk**: La unidad de riesgo.
    - *Atributos*: Probabilidad (1-5), Impacto (1-5), Nivel (Calculado).
    - *Estados*: Identificado, En Evaluación, Tratado, Aceptado, Cerrado.
- **Control**: Mecanismo de defensa.
    - *Tipos*: Preventivo, Detectivo, Correctivo.
    - *Estados*: Borrador, Activo, Obsoleto.
- **RiskControl**: Relación M2M calificando cuánto mitiga el control a ese riesgo específico (% mitigación o re-evaluación).

### Monitoreo
- **KRI**: Indicador.
    - *Estados*: Verde (Dentro de umbral), Ámbar (Alerta), Rojo (Violación).
- **Incident/Event**: Materialización.
    - *Estados*: Abierto, En Investigación, Cerrado.
- **ActionPlan**: Respuesta.
    - *Estados*: Pendiente, En Progreso, En Verificación, Cerrado, Vencido.

## 3. Flujos Principales

### A. Ciclo de Vida del Riesgo
1. **Identificación**: Creación de Riesgo en estado 'Identificado'.
2. **Evaluación Inherente**: Asignar P e I -> Cálculo de Nivel.
3. **Tratamiento**:
    - Asignar Controles existentes.
    - O Crear Planes de Acción (si el control no existe).
4. **Evaluación Residual**: Recálculo basado en efectividad de controles.
5. **Aceptación/Monitoreo**: Pase a estado 'Tratado'/'Aceptado'.

### B. Gestión de Incidentes
1. Reporte de Incidente (Abierto).
2. Vinculación a Riesgo (si existe) o creación de nuevo Riesgo.
3. Análisis de Causa Raíz.
4. Definición de Plan de Acción (si aplica).
5. Cierre.
