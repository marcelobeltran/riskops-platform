from django.db import models
from core.models import TimeStampedModel

class ConfigList(TimeStampedModel):
    technical_name = models.CharField(max_length=100, unique=True, verbose_name="Nombre Técnico")
    name = models.CharField(max_length=200, verbose_name="Nombre de la Lista")

    class Meta:
        verbose_name = "Lista Maestra"
        verbose_name_plural = "Listas Maestras"
        ordering = ['name']

    def __str__(self):
        return self.name

class ConfigListItem(TimeStampedModel):
    config_list = models.ForeignKey(ConfigList, on_delete=models.CASCADE, related_name='items', verbose_name="Lista")
    technical_name = models.CharField(max_length=100, verbose_name="Nombre Técnico")
    label = models.CharField(max_length=200, verbose_name="Etiqueta Visual")
    order = models.IntegerField(default=0, verbose_name="Orden")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Ítem de Lista"
        verbose_name_plural = "Ítems de Lista"
        unique_together = ('config_list', 'technical_name')
        ordering = ['config_list', 'order', 'label']

    def __str__(self):
        return self.label

class FieldRecommendation(TimeStampedModel):
    STATUS_CHOICES = (
        ('recommended', 'Recomendado'),
        ('accepted', 'Aceptado'),
        ('overridden', 'Manual/Anulado'),
        ('dismissed', 'Descartado'),
    )

    risk = models.ForeignKey('risk_universe.Risk', on_delete=models.CASCADE, related_name='recommendations')
    field_name = models.CharField(max_length=100, verbose_name="Campo")
    recommended_value = models.ForeignKey(ConfigListItem, on_delete=models.CASCADE, verbose_name="Valor Recomendado")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='recommended', verbose_name="Estado")

    class Meta:
        verbose_name = "Recomendación de Campo"
        verbose_name_plural = "Recomendaciones de Campos"
        unique_together = ('risk', 'field_name')

    def __str__(self):
        return f"Reco para {self.risk.title} ({self.field_name})"
class ControlRecommendation(TimeStampedModel):
    STATUS_CHOICES = (
        ('recommended', 'Recomendado'),
        ('accepted', 'Aceptado'),
        ('overridden', 'Manual/Anulado'),
        ('dismissed', 'Descartado'),
    )

    risk = models.ForeignKey('risk_universe.Risk', on_delete=models.CASCADE, related_name='control_recommendations')
    control = models.ForeignKey('controls.Control', on_delete=models.CASCADE, verbose_name="Control Recomendado")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='recommended', verbose_name="Estado")

    class Meta:
        verbose_name = "Recomendación de Control"
        verbose_name_plural = "Recomendaciones de Controles"
        unique_together = ('risk', 'control')

    def __str__(self):
        return f"Reco {self.control.code} para {self.risk.code}"
