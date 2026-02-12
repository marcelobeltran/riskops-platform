from django.db import models
from simple_history.models import HistoricalRecords
from core.models import TimeStampedModel
from risk_universe.models import Risk
from controls.models import Control

class KRI(TimeStampedModel):
    name = models.CharField(max_length=200, verbose_name="Nombre del Indicador")
    description = models.TextField(verbose_name="Descripción/Fórmula")
    risk = models.ForeignKey(Risk, on_delete=models.CASCADE, related_name='kris', verbose_name="Riesgo Asociado")
    
    threshold_green = models.FloatField(verbose_name="Umbral Verde (<=)")
    threshold_yellow = models.FloatField(verbose_name="Umbral Amarillo (<=)")
    threshold_red = models.FloatField(verbose_name="Umbral Rojo (>)")
    
    current_value = models.FloatField(null=True, blank=True, verbose_name="Valor Actual")
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = "KRI"
        verbose_name_plural = "KRIs"

    def __str__(self):
        return self.name

class RiskEvent(TimeStampedModel):
    TYPE_CHOICES = [
        ('incident', 'Incidente (Sin Pérdida)'),
        ('loss', 'Evento de Pérdida'),
        ('near_miss', 'Near Miss'),
    ]

    risk = models.ForeignKey(Risk, on_delete=models.CASCADE, related_name='events', verbose_name="Riesgo Materializado")
    event_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Tipo de Evento")
    date_occurrence = models.DateField(verbose_name="Fecha de Ocurrencia")
    date_discovery = models.DateField(verbose_name="Fecha de Descubrimiento")
    
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Monto Pérdida")
    description = models.TextField(verbose_name="Descripción del Evento")
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Evento/Incidente"
        verbose_name_plural = "Eventos e Incidentes"

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.date_occurrence}"

class ActionPlan(TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_progress', 'En Progreso'),
        ('verified', 'Verificado'),
        ('closed', 'Cerrado'),
        ('overdue', 'Vencido'),
    ]

    description = models.TextField(verbose_name="Descripción de la Acción")
    responsible = models.CharField(max_length=100, verbose_name="Responsable")
    due_date = models.DateField(verbose_name="Fecha Vencimiento")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Estado")
    
    # Linked to Risk OR Control (or both)
    risk = models.ForeignKey(Risk, on_delete=models.CASCADE, null=True, blank=True, related_name='action_plans', verbose_name="Riesgo")
    control = models.ForeignKey(Control, on_delete=models.CASCADE, null=True, blank=True, related_name='action_plans', verbose_name="Control")

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Plan de Acción"
        verbose_name_plural = "Planes de Acción"

    def __str__(self):
        return f"Plan: {self.description[:50]}..."
