from django.test import TestCase, Client
from django.contrib.auth.models import User
from risk_universe.models import Process, Risk
from django.urls import reverse

class DashboardTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@test.com', 'password')
        self.client = Client()
        self.client.login(username='admin', password='password')
        
        self.process = Process.objects.create(name="Proc 1", owner="Me", criticality='high')
        self.risk = Risk.objects.create(
            process=self.process, 
            title="Risk 1", 
            description="Desc", 
            inherent_probability=5, 
            inherent_impact=5
        )

    def test_admin_index_dashboard(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "RiskOps Dashboard")
        self.assertContains(response, "Procesos Críticos")
        self.assertContains(response, "Risk 1") # Top 10

    def test_heatmap_view(self):
        response = self.client.get(reverse('heatmap'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Matriz de Calor de Riesgos")
        self.assertContains(response, "Risk 1") # Should show up in the matrix
