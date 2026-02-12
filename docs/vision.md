# Visión del Producto: RiskOps Platform AI

## 1. Propósito y Valor
Plataforma inteligente de gestión de Riesgo Operacional que combina flujos de trabajo estructurados con asistencia de Inteligencia Artificial para potenciar el análisis y cumplimiento normativo.

## 2. Usuarios y Roles (Nuevo)
- **Admin de Sistema (Configurador)**:
    - Define escalas (Probabilidad/Impacto 1-5 vs 1-10).
    - Configura umbrales de KRIs y SLAs de planes.
    - Carga documentos normativos al RAG.
- **Supervisor / Jefatura**:
    - Visión global (Dashboard Agregado).
    - Aprueba riesgos evaluados.
    - Forecast y tendencias de riesgo.
- **Analista de Riesgo (Operativo)**:
    - Levanta y evalúa riesgos.
    - Realiza entrevistas (soporte IA).
    - Ejecuta controles.

## 3. Módulos Funcionales

### Core Risk (Existente - A refinar)
- Gestión de Procesos, Riesgos y Controles.
- **Mejora**: Escalas parametrizables (Dynamic Scales) en lugar de hardcoded.

### AI Governance & RAG (Nuevo)
- **Base de Conocimiento (RAG)**:
    - Ingesta de PDFs (Basilea III, PCI, Reglamentos).
    - Chat consultivo: "¿Qué controles pide la norma X para este proceso?".
- **Asistente de Entrevistas**:
    - Upload de audio de entrevistas.
    - **Speech-to-Text (Whisper)**: Transcripción automática.
    - **Auto-Tagging**: IA sugiere riesgos y controles detectados en el texto.
- **Recomendador**:
    - Sugerencia de descripciones de riesgo y planes de acción basados en históricos y normas.

### Reportabilidad
- **Excel Export**: Descarga masiva de matrices y catálogos.
- **Dashboard Gerencial**: Evolución histórica.

## 4. Alcance Iteración 1 (Próxima)
1.  **Refactor de Roles**: Separar permisos y vistas para Admin vs Supervisor vs Analista.
2.  **Configurabilidad**: Modelos para `RiskScale`, `ImpactType`.
3.  **Exportación**: Botón "Exportar a Excel" en Admin.
4.  **Cimientos AI**: Preparar modelo de datos para guardar "Entrevistas" y "Documentos Normativos".

## 5. Alcance Futuro (Iteración 2 - AI Deep Dive)
- Implementación de Vector DB (Chroma/PGVector).
- Integración con LLM (OpenAI/Anthropic).
- Procesamiento de Audio.
