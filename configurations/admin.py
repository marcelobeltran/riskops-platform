from django.contrib import admin
from .models import ConfigList, ConfigListItem
from core.admin_utils import StandardAdminMixin

class ConfigListItemInline(admin.TabularInline):
    model = ConfigListItem
    extra = 1
    fields = ('technical_name', 'label', 'order', 'is_active')

@admin.register(ConfigList)
class ConfigListAdmin(StandardAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'technical_name', 'created')
    search_fields = ('name', 'technical_name')
    inlines = [ConfigListItemInline]

@admin.register(ConfigListItem)
class ConfigListItemAdmin(StandardAdminMixin, admin.ModelAdmin):
    list_display = ('label', 'config_list', 'technical_name', 'order', 'is_active')
    list_filter = ('config_list',) # is_active handled by StandardStatusFilter in mixin
    list_editable = ('order', 'is_active')
    search_fields = ('label', 'technical_name', 'config_list__name')
    ordering = ('config_list', 'order', 'label')
