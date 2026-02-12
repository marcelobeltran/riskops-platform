from django.urls import path
from . import views

app_name = 'knowledge'

urlpatterns = [
    path('assistant/', views.ai_assistant_view, name='assistant'),
    path('assistant/query/', views.ai_query_api, name='query_api'),
]
