from django.http import JsonResponse
from django.apps import apps
from django.contrib.auth.decorators import user_passes_test
import json

@user_passes_test(lambda u: u.is_staff)
def get_archived_items_api(request):
    """
    Generic API to fetch archived/deleted items for a specific model.
    Query params: app_label, model_name, query (optional)
    """
    app_label = request.GET.get('app_label')
    model_name = request.GET.get('model_name')
    query = request.GET.get('q', '').lower()
    
    if not app_label or not model_name:
        return JsonResponse({'status': 'error', 'message': 'Missing app_label or model_name'}, status=400)
    
    try:
        model = apps.get_model(app_label, model_name)
        model_fields = [f.name for f in model._meta.get_fields()]
        
        # Determine filter field
        filter_field = None
        if 'is_active' in model_fields:
            filter_kwargs = {'is_active': False}
        elif 'is_deleted' in model_fields:
            filter_kwargs = {'is_deleted': True}
        else:
            return JsonResponse({'items': []})
            
        queryset = model.objects.filter(**filter_kwargs)
        
        # Simple search logic
        if query:
            # Try to search in common fields
            search_fields = [f for f in ['name', 'title', 'code', 'description'] if f in model_fields]
            if search_fields:
                from django.db.models import Q
                q_obj = Q()
                for field in search_fields:
                    q_obj |= Q(**{f"{field}__icontains": query})
                queryset = queryset.filter(q_obj)
        
        # Limit results for the modal
        queryset = queryset.order_by('-id')[:50]
        
        items = []
        for obj in queryset:
            # Determine display name
            display_name = str(obj)
            # Remove any legacy (ARCHIVADO) from string representation if it exists
            display_name = display_name.replace('(ARCHIVADO)', '').replace('(ARCHIVADA)', '').strip()
            
            items.append({
                'id': obj.id,
                'name': display_name,
                'code': getattr(obj, 'code', f"ID: {obj.id}")
            })
            
        return JsonResponse({'items': items})
        
    except LookupError:
        return JsonResponse({'status': 'error', 'message': 'Model not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@user_passes_test(lambda u: u.is_staff)
def reactivate_item_api(request):
    """
    Generic API to reactivate specific items.
    POST data: app_label, model_name, ids (list)
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)
        
    try:
        data = json.loads(request.body)
        app_label = data.get('app_label')
        model_name = data.get('model_name')
        ids = data.get('ids', [])
        
        if not app_label or not model_name or not ids:
            return JsonResponse({'status': 'error', 'message': 'Missing parameters'}, status=400)
            
        model = apps.get_model(app_label, model_name)
        model_fields = [f.name for f in model._meta.get_fields()]
        
        queryset = model.objects.filter(id__in=ids)
        count = 0
        
        if 'is_active' in model_fields:
            count = queryset.update(is_active=True)
        elif 'is_deleted' in model_fields:
            count = queryset.update(is_deleted=False)
            
        return JsonResponse({'status': 'success', 'count': count})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
