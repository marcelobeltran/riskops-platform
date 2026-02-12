from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from core.views import heatmap_view

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=True)),
    path('admin/', admin.site.urls),
    path('risk-matrix/', heatmap_view, name='risk_heatmap'),
    path('knowledge/', include('knowledge.urls')),
]
