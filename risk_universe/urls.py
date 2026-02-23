from django.urls import path
from .views import (
    get_orphan_risks, link_risks_to_process, create_and_link_risk,
    suggest_fields_api, recommendation_action_api, get_recommendations_api,
    get_control_recommendations_api, calculate_risk_preview_api
)

app_name = 'risk_universe'

urlpatterns = [
    path('api/orphans/', get_orphan_risks, name='get_orphan_risks'),
    path('api/link-risks/', link_risks_to_process, name='link_risks_to_process'),
    path('api/create-and-link/', create_and_link_risk, name='create_and_link_risk'),
    path('api/suggest-fields/', suggest_fields_api, name='suggest_fields'),
    path('api/recommendations/action/', recommendation_action_api, name='recommendation_action'),
    path('api/risks/<int:risk_id>/recommendations/', get_recommendations_api, name='get_recommendations'),
    path('api/risks/<int:risk_id>/control-recommendations/', get_control_recommendations_api, name='get_control_recommendations'),
    path('api/calculate-preview/', calculate_risk_preview_api, name='calculate_preview'),
]
