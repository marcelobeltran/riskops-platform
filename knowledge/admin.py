from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import NormativeDocument, DocumentChunk, InterviewSession

class DocumentChunkInline(admin.TabularInline):
    model = DocumentChunk
    extra = 0
    readonly_fields = ('chunk_index', 'text_content', 'vector_id')
    can_delete = False
    show_change_link = True

@admin.register(NormativeDocument)
class NormativeDocumentAdmin(SimpleHistoryAdmin):
    list_display = ('title', 'document_type', 'created', 'is_processed')
    list_filter = ('document_type', 'is_processed')
    search_fields = ('title', 'description')
    
    inlines = [DocumentChunkInline]
    
    actions = ['process_documents']

    def process_documents(self, request, queryset):
        from .services import KnowledgeService
        service = KnowledgeService()
        count = 0
        for doc in queryset:
            if service.process_document(doc.id):
                count += 1
        self.message_user(request, f"{count} documentos procesados correctamente (Text Chunking).")
    process_documents.short_description = "Procesar con IA (Extraer Texto)"

@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('document', 'chunk_index', 'short_content')
    list_filter = ('document',)
    search_fields = ('text_content',)

    def short_content(self, obj):
        return obj.text_content[:100] + "..." if obj.text_content else ""
    short_content.short_description = "Contenido"

@admin.register(InterviewSession)
class InterviewSessionAdmin(SimpleHistoryAdmin):
    list_display = ('title', 'date', 'interviewer', 'interviewee', 'is_transcribed')
    list_filter = ('date', 'is_transcribed')
    search_fields = ('title', 'transcript', 'interviewer', 'interviewee')
    
    actions = ['transcribe_audio']

    def transcribe_audio(self, request, queryset):
        from .services import KnowledgeService
        service = KnowledgeService()
        count = 0
        for session in queryset:
            if service.transcribe_interview(session.id):
                count += 1
        self.message_user(request, f"{count} entrevistas transcritas correctamente.")
    transcribe_audio.short_description = "Transcribir con Whisper (IA)"
