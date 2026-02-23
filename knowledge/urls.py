from django.urls import path
from . import views

app_name = 'knowledge'

urlpatterns = [
    path('assistant/', views.ai_assistant_view, name='assistant'),
    path('assistant/query/', views.ai_query_api, name='query_api'),
    path('risk-interview/', views.risk_interview_wizard, name='risk_interview'),
    path('analyze-interview/', views.analyze_interview_api, name='analyze_interview'),
    path('pre-analyze-interview/', views.pre_analyze_interview_api, name='pre_analyze_interview'),
    path('final-analyze-interview/', views.final_analyze_interview_api, name='final_analyze_interview'),
    path('risk-interview/data/', views.get_wizard_data_api, name='wizard_data'),
    path('save-interview/', views.save_interview_session_api, name='save_interview'),
    
    # Session-specific AI Actions
    path('interviews/<int:session_id>/ai/pre_analysis/', views.pre_analyze_interview_api, name='session_pre_analysis'),
    path('interviews/<int:session_id>/ai/final_analysis/', views.final_analyze_interview_api, name='session_final_analysis'),
    path('api/controles/calcular/', views.calculate_control_effectiveness_api, name='calculate_control_effectiveness'),
    path('api/interviews/apply_finding/', views.apply_finding_api, name='apply_finding'),
    path('api/interviews/list-previous/', views.list_previous_interviews_api, name='list_previous_interviews'),
]
