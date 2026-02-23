from django.db import models
from django.utils import timezone
import uuid
from core.models import TimeStampedModel
from simple_history.models import HistoricalRecords

class NormativeDocument(TimeStampedModel):
    DOCUMENT_TYPE_CHOICES = [
        ('law', 'Ley / Regulación'),
        ('policy', 'Política Interna'),
        ('manual', 'Manual de Procedimiento'),
        ('other', 'Otro'),
    ]

    title = models.CharField(max_length=255, verbose_name="Título del Documento")
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='policy', verbose_name="Tipo")
    jurisdiction = models.CharField(max_length=100, default='Chile', verbose_name="Jurisdicción")
    version = models.CharField(max_length=50, blank=True, verbose_name="Versión")
    file = models.FileField(upload_to='normative_docs/', verbose_name="Archivo PDF")
    description = models.TextField(blank=True, verbose_name="Descripción / Alcance")
    
    # Processing Status
    is_processed = models.BooleanField(default=False, verbose_name="Procesado por IA")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    processed_at = models.DateTimeField(null=True, blank=True)
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Documento Normativo"
        verbose_name_plural = "Documentos Normativos"

    def __str__(self):
        return self.title

class DocumentChunk(TimeStampedModel):
    """
    Stores the broken down text chunks of the document and their vector IDs.
    This links the SQL DB to the Vector DB (Chroma).
    """
    document = models.ForeignKey(NormativeDocument, on_delete=models.CASCADE, related_name='chunks')
    chunk_index = models.PositiveIntegerField()
    text_content = models.TextField()
    parent_text = models.TextField(blank=True, null=True, help_text="Contexto del padre (Sección o Título)")
    section_title = models.CharField(max_length=255, blank=True, null=True)
    
    # We store the ID used in ChromaDB to easily find/update/delete
    vector_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Fragmento de Documento"
        verbose_name_plural = "Fragmentos de Documentos"
        ordering = ['chunk_index']

    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"

class InterviewSession(TimeStampedModel):
    """
    Stores audio recordings and transcripts of risk assessment interviews.
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Borrador'),
        ('COMPLETED', 'Completado'),
    ]

    title = models.CharField(max_length=255, verbose_name="Título de la Entrevista")
    date = models.DateField(verbose_name="Fecha de la Entrevista")
    interviewer = models.CharField(max_length=100, verbose_name="Entrevistador")
    interviewee = models.CharField(max_length=100, verbose_name="Entrevistado")
    
    process = models.ForeignKey('risk_universe.Process', on_delete=models.SET_NULL, null=True, blank=True, related_name='interviews', verbose_name="Proceso Relacionado")
    identified_risk = models.ForeignKey('risk_universe.Risk', on_delete=models.SET_NULL, null=True, blank=True, related_name='interviews', verbose_name="Riesgo Identificado")
    
    audio_file = models.FileField(upload_to='interviews/audio/', null=True, blank=True, verbose_name="Archivo de Audio")
    transcript = models.TextField(blank=True, verbose_name="Transcripción (Auto)")
    
    # New Fields for Demo Persistence
    momento_a_json = models.JSONField(default=dict, blank=True, verbose_name="Momento A (Hipótesis/Preguntas)")
    momento_b_json = models.JSONField(default=dict, blank=True, verbose_name="Momento B (Hallazgos/Contexto)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT', verbose_name="Estado")
    
    is_transcribed = models.BooleanField(default=False, verbose_name="Transcrito")
    
    # Combined Context (PR3)
    combined_sessions = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='combined_into', verbose_name="Entrevistas Combinadas")
    
    # New Fields for Idempotency and Soft Delete
    session_uuid = models.UUIDField(default=uuid.uuid4, db_index=True, editable=False, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_deleted = models.BooleanField(default=False, verbose_name="Archivado")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Archivado")

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Sesión de Entrevista"
        verbose_name_plural = "Sesiones de Entrevistas"

    def __str__(self):
        return f"{self.title} - {self.date}"

class InterviewFinding(models.Model):
    """
    Stores individual findings extracted from an interview session.
    """
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='findings')
    
    idx = models.IntegerField(default=0, verbose_name="Índice Hallazgo")
    confianza = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, verbose_name="Confianza IA")
    
    # Editable fields by the analyst
    title = models.CharField(max_length=255, verbose_name="Título del Riesgo")
    description = models.TextField(verbose_name="Descripción (Causa/Evento/Impacto)")
    risk_factor = models.CharField(max_length=255, blank=True, verbose_name="Factor de Riesgo Sugerido")
    specific_risk_factor = models.CharField(max_length=255, blank=True, verbose_name="Factor Específico")
    
    # Store the associated controls and evidence as JSON for simplicity in this demo stage
    suggested_controls = models.JSONField(default=list, verbose_name="Controles Sugeridos")
    evidence_rag = models.JSONField(default=list, verbose_name="Evidencia RAG Asociada")
    
    # Audit Trail / Snapshot
    analysis_snapshot = models.JSONField(null=True, blank=True, help_text="Copia completa del JSON del engine en el momento de aceptación")
    
    is_accepted = models.BooleanField(default=False, verbose_name="Aceptado")
    selected = models.BooleanField(default=False, verbose_name="Seleccionado/Registrado")
    created_risk = models.ForeignKey('risk_universe.Risk', on_delete=models.SET_NULL, null=True, blank=True, related_name='derived_findings')

    class Meta:
        verbose_name = "Hallazgo de Entrevista"
        verbose_name_plural = "Hallazgos de Entrevistas"

    def __str__(self):
        return f"Hallazgo: {self.title} (Sesión: {self.session.id})"

