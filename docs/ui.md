# Especificación de Interfaz de Usuario (UI/UX) - MVP

**Estrategia UI**: "Admin-Enhanced". Usaremos el framework de administración de Django (`django-admin`) como base, extendiéndolo con templates personalizados (`admin/base_site.html`, `admin/index.html`) solo para las vistas de Dashboard y Reportes que el admin nativo no soporta bien.

## 1. Navegación (Sitemap)
- **Home (Dashboard)**: Vista principal personalizada.
- **Risk Universe**:
    - Procesos (Lista/Detalle)
    - Riesgos (Lista/Detalle)
    - Categorías
- **Library of Controls**:
    - Controles (Lista/Detalle)
    - Evaluaciones de Control
- **Monitoring**:
    - KRIs (Tablero y Lista)
    - Eventos/Incidentes
    - Planes de Acción
- **Administration**: Usuarios, Grupos, Auditoría.

## 2. Layout & Mockups en Texto

### Pantalla 1: Dashboard Principal (/admin/)
**Objetivo**: Visión general del estado de salud de riesgo.
**Componentes**:
1.  **Header**: Stats Cards de alto nivel.
    -   `[ Procs. Críticos: 12 ]` | `[ Riesgos Altos (Res): 5 ]` | `[ Planes Vencidos: 3 ]`
2.  **Sección Central**:
    -   **Top 10 Riesgos (Residual)**: Tabla simple. {ID, Título, Proceso, Nivel Residual}.
    -   **KRI Watchlist**: Lista de KRIs en estado ROJO o ÁMBAR. {KRI, Valor, Tendencia}.
3.  **Sidebar/Footer**: Accesos directos a "Reportar Incidente".

### Pantalla 2: Matriz de Riesgo (/risk-matrix/)
**Objetivo**: Visualizar la distribución de riesgos.
**Componentes**:
-   **Toggle**: [ Ver Inherente ] | [ Ver Residual ]
-   **Grid 5x5**:
    -   Eje Y: Impacto (Insignificante -> Catastrófico)
    -   Eje X: Probabilidad (Raro -> Casi Seguro)
    -   Celdas: Contadores cliqueables (e.g., "3 riesgos"). Al hacer clic, muestra la lista de esos riesgos.
    -   Colores: Fondo de celdas según severidad (Verde, Amarillo, Naranja, Rojo).

### Pantalla 3: Ficha del Riesgo (Vista Detalle Admin)
**Objetivo**: Gestión 360 de un riesgo.
**Componentes**:
-   **Fieldset "Definición"**: Título, Descripción, Categoría, Proceso.
-   **Fieldset "Evaluación Inherente"**: Probabilidad, Impacto, Score (Readonly).
-   **Inline "Controles y Mitigación"**: Lista de controles asociados. Columna extra para evaluar "Efectividad en este riesgo".
-   **Fieldset "Evaluación Residual"**: Probabilidad Residual, Impacto Residual (Calculados o manuales).
-   **Inline "Planes de Acción"**: Tareas abiertas para este riesgo.
-   **Inline "Historial"**: (via `django-simple-history`) Lista de cambios.

### Pantalla 4: Ficha del Proceso
**Objetivo**: Contexto del negocio.
**Componentes**:
-   **Info**: Dueño, Criticidad.
-   **Inline "Riesgos Asociados"**: Lista de riesgos que pertenecen a este proceso.
-   **Inline "Incidentes Recientes"**: Últimos eventos vinculados a este proceso.

## 3. Componentes Visuales
-   **Semáforos (Traffic Lights)**: Círculos CSS simples (Verde/Amarillo/Rojo) para KRIs y Niveles de Riesgo.
-   **Barras de Progreso**: Para el avance de Planes de Acción.
-   **Badges**: Etiquetas para estados (e.g., `[Abierto]` en azul, `[Cerrado]` en gris).
