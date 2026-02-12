from django.db import models
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
    file = models.FileField(upload_to='normative_docs/', verbose_name="Archivo PDF")
    description = models.TextField(blank=True, verbose_name="Descripción / Alcance")
    
    # Processing Status
    is_processed = models.BooleanField(default=False, verbose_name="Procesado por IA")
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
    title = models.CharField(max_length=255, verbose_name="Título de la Entrevista")
    date = models.DateField(verbose_name="Fecha de la Entrevista")
    interviewer = models.CharField(max_length=100, verbose_name="Entrevistador")
    interviewee = models.CharField(max_length=100, verbose_name="Entrevistado")
    
    audio_file = models.FileField(upload_to='interviews/audio/', verbose_name="Archivo de Audio")
    transcript = models.TextField(blank=True, verbose_name="Transcripción (Auto)")
    
    is_transcribed = models.BooleanField(default=False, verbose_name="Transcrito")
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Sesión de Entrevista"
        verbose_name_plural = "Sesiones de Entrevistas"

    def __str__(self):
        return f"{self.title} - {self.date}"

