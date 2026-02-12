from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Process, RiskCategory, Risk

@admin.register(Process)
class ProcessAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'owner', 'criticality', 'created')
    list_filter = ('criticality', 'owner')
    search_fields = ('name', 'owner', 'description')

@admin.register(RiskCategory)
class RiskCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

from import_export.admin import ImportExportModelAdmin

@admin.register(Risk)
class RiskAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
    list_display = ('code', 'title', 'process', 'inherent_display', 'residual_display', 'status', 'controls_count')
    list_filter = ('process', 'status', 'category')
    search_fields = ('title', 'description', 'code')
    
    fieldsets = (
        ('Identificación', {
            'fields': ('code', 'process', 'category', 'title', 'description')
        }),
        ('Evaluación Inherente', {
            'fields': ('inherent_probability', 'inherent_impact_level')
        }),
        ('Evaluación Residual', {
            'fields': ('residual_probability', 'residual_impact_level')
        }),
        ('Estado', {
            'fields': ('status',)
        }),
    )

    def controls_count(self, obj):
        return obj.controls.count()
    controls_count.short_description = 'Controles'

    # New methods for inherent and residual display
    def inherent_display(self, obj):
        prob = obj.inherent_probability.name if obj.inherent_probability else "-"
        return f"{prob} / {obj.get_inherent_impact_level_display()}"
    inherent_display.short_description = "Nivel Inherente"

    def residual_display(self, obj):
        prob = obj.residual_probability.name if obj.residual_probability else "-"
        return f"{prob} / {obj.get_residual_impact_level_display()}"
    residual_display.short_description = "Nivel Residual"
