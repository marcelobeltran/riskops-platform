from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Control, ControlAssessment

from import_export.admin import ImportExportModelAdmin
from .models import Control, ControlAssessment

class ControlAssessmentInline(admin.TabularInline):
    model = ControlAssessment
    extra = 0

@admin.register(Control)
class ControlAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
    list_display = ('code', 'name', 'effectiveness_score', 'weight_opportunity', 'weight_scope')
    list_filter = ('weight_opportunity', 'weight_scope', 'weight_type')
    search_fields = ('code', 'name', 'description')
    filter_horizontal = ('risks',)
    inlines = [ControlAssessmentInline]
    
    fieldsets = (
        ('Identificación', {
            'fields': ('code', 'name', 'description')
        }),
        ('Evaluación de Diseño (Ponderación)', {
            'fields': (
                'weight_opportunity', 
                'weight_scope', 
                'weight_type', 
                'weight_segregation', 
                'weight_formalization'
            ),
            'description': 'La efectividad total se calcula automáticamente sumando estos valores.'
        }),
        ('Riesgos Asociados', {
            'fields': ('risks',)
        }),
    )

@admin.register(ControlAssessment)
class ControlAssessmentAdmin(SimpleHistoryAdmin):
    list_display = ('control', 'date', 'design_effectiveness', 'operational_effectiveness', 'assessor')
    list_filter = ('design_effectiveness', 'operational_effectiveness', 'date')
    search_fields = ('control__name', 'observations')
