from django.contrib import admin
from django.utils.translation import gettext_lazy as _

class StandardStatusFilter(admin.SimpleListFilter):
    title = 'Estado'
    parameter_name = 'status_standard'

    def lookups(self, request, model_admin):
        return (
            ('all', 'Todos'),
            ('active', 'Activo'),
            ('archived', 'Archivado'),
        )

    def queryset(self, request, queryset):
        val = self.value()
        
        model_fields = [f.name for f in queryset.model._meta.get_fields()]
        
        active_field = None
        if 'is_active' in model_fields:
            active_field = 'is_active'
            active_val = True
            archived_val = False
        elif 'is_deleted' in model_fields:
            active_field = 'is_deleted'
            active_val = False
            archived_val = True
            
        if not active_field:
            return queryset

        if val == 'active':
            return queryset.filter(**{active_field: active_val})
        if val == 'archived':
            return queryset.filter(**{active_field: archived_val})
        if val == 'all':
            return queryset
        
        # Default: Active (as per user preference for focused views)
        if val is None:
            return queryset.filter(**{active_field: active_val})
            
        return queryset

class StandardAdminMixin:
    """
    Mixin to apply global PR1 styles and logic to ModelAdmin classes.
    """
    # We use get_actions to inject dynamically
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        
        # Add archive/reactivate if model supports it
        model_fields = [f.name for f in self.model._meta.get_fields()]
        if 'is_active' in model_fields or 'is_deleted' in model_fields:
            if 'archive' not in actions:
                actions['archive'] = (
                    self.__class__.archive,
                    'archive',
                    'Archivar'
                )
            if 'reactivate' not in actions:
                actions['reactivate'] = (
                    self.__class__.reactivate,
                    'reactivate',
                    'Reactivar'
                )
        return actions

    def changelist_view(self, request, extra_context=None):
        """Inject app_label and model_name for JS use."""
        extra_context = extra_context or {}
        extra_context['app_label'] = self.model._meta.app_label
        extra_context['model_name'] = self.model._meta.model_name
        return super().changelist_view(request, extra_context=extra_context)

    def get_list_filter(self, request):
        base_filters = list(super().get_list_filter(request))
        
        # Add StandardStatusFilter if model supports it
        model_fields = [f.name for f in self.model._meta.get_fields()]
        if 'is_active' in model_fields or 'is_deleted' in model_fields:
            if StandardStatusFilter not in base_filters:
                # Insert at the beginning
                base_filters.insert(0, StandardStatusFilter)
        
        return tuple(base_filters)

    def archive(self, request, queryset):
        model_fields = [f.name for f in self.model._meta.get_fields()]
        count = 0
        if 'is_active' in model_fields:
            count = queryset.update(is_active=False)
        elif 'is_deleted' in model_fields:
            count = queryset.update(is_deleted=True)
        
        if count:
            self.message_user(request, f"{count} ítems archivados.")
    archive.short_description = "Archivar"

    def reactivate(self, request, queryset):
        model_fields = [f.name for f in self.model._meta.get_fields()]
        count = 0
        if 'is_active' in model_fields:
            count = queryset.update(is_active=True)
        elif 'is_deleted' in model_fields:
            count = queryset.update(is_deleted=False)
            
        if count:
            self.message_user(request, f"{count} ítems reactivados.")
    reactivate.short_description = "Reactivar"

    class Media:
        css = {
            'all': ('core/admin/css/admin_standard.css',)
        }
        js = ('core/admin/js/admin_standard.js',)
