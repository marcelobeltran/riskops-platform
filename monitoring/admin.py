from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from django.utils.html import format_html
from .models import KRI, RiskEvent, ActionPlan

@admin.register(KRI)
class KRIAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'risk', 'current_value', 'status_traffic_light')
    list_filter = ('risk__process', 'risk')
    search_fields = ('name', 'description')

    def status_traffic_light(self, obj):
        if obj.current_value is None:
            return "N/A"
        
        # Logic: Red if > threshold_red? Or logic depends on KRI direction (Ascending/Descending).
        # Assumption: Higher is worse logic for Red > Threshold.
        # But user didn't specify direction. Assuming standard: Red > Red Threshold.
        
        color = 'gray'
        if obj.current_value > obj.threshold_red:
            color = 'red'
        elif obj.current_value > obj.threshold_yellow:
            color = 'orange' # Amber
        elif obj.current_value <= obj.threshold_green:
            color = 'green'
        
        return format_html(
            '<span style="display:inline-block; width:15px; height:15px; border-radius:50%; background-color:{};"></span>',
            color
        )
    status_traffic_light.short_description = "Estado"

@admin.register(RiskEvent)
class RiskEventAdmin(SimpleHistoryAdmin):
    list_display = ('event_type', 'date_occurrence', 'amount', 'risk')
    list_filter = ('event_type', 'date_occurrence')
    search_fields = ('description', 'risk__title')

@admin.register(ActionPlan)
class ActionPlanAdmin(SimpleHistoryAdmin):
    list_display = ('description_short', 'responsible', 'due_date', 'status', 'risk')
    list_filter = ('status', 'responsible', 'due_date')
    search_fields = ('description', 'responsible')

    def description_short(self, obj):
        return obj.description[:50]
