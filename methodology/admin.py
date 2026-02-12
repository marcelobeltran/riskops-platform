from django.contrib import admin
from .models import ImpactDimension, ImpactScale, ProbabilityScale, RiskLevel, RiskMatrixRule

@admin.register(ImpactDimension)
class ImpactDimensionAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')

@admin.register(ImpactScale)
class ImpactScaleAdmin(admin.ModelAdmin):
    list_display = ('dimension', 'level', 'name', 'short_description')
    list_filter = ('dimension', 'level')
    ordering = ('dimension', 'level')

    def short_description(self, obj):
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description

@admin.register(ProbabilityScale)
class ProbabilityScaleAdmin(admin.ModelAdmin):
    list_display = ('level', 'name', 'occurrence_criteria')
    ordering = ('level',)

@admin.register(RiskLevel)
class RiskLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'order')

@admin.register(RiskMatrixRule)
class RiskMatrixRuleAdmin(admin.ModelAdmin):
    list_display = ('probability_level', 'impact_level', 'risk_level')
    list_filter = ('risk_level',)
    ordering = ('-probability_level', '-impact_level')
