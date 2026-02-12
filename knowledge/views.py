from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from .services import KnowledgeService
import json

@staff_member_required
def ai_assistant_view(request):
    return render(request, 'knowledge/assistant.html')

@staff_member_required
def ai_query_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        query = data.get('query', '')
        
        if not query:
            return JsonResponse({'error': 'No query provided'}, status=400)
            
        service = KnowledgeService()
        
        # 1. Ask Assistant (Full RAG)
        answer = service.ask_assistant(query)
            
        return JsonResponse({
            'response': answer
        })
        
    return JsonResponse({'error': 'Invalid method'}, status=405)
