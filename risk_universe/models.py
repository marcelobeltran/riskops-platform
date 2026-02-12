from django.db import models
from django.db.models import Sum
from django.core.validators import MinValueValidator, MaxValueValidator
from simple_history.models import HistoricalRecords
from core.models import TimeStampedModel
from methodology.models import ProbabilityScale, ImpactScale, RiskLevel, RiskMatrixRule

class Process(TimeStampedModel):
    CRITICALITY_CHOICES = [
        ('high', 'Alta'),
        ('medium', 'Media'),
        ('low', 'Baja'),
    ]

    name = models.CharField(max_length=200, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    owner = models.CharField(max_length=100, verbose_name="Dueño del Proceso")
    criticality = models.CharField(
        max_length=10, 
        choices=CRITICALITY_CHOICES, 
        default='medium',
        verbose_name="Criticidad"
    )
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Proceso"
        verbose_name_plural = "Procesos"

    def __str__(self):
        return self.name

class RiskCategory(TimeStampedModel):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Categoría de Riesgo"
        verbose_name_plural = "Categorías de Riesgo"

    def __str__(self):
        return self.name

class Risk(TimeStampedModel):
    STATUS_CHOICES = [
        ('identified', 'Identificado'),
        ('evaluated', 'En Evaluación'),
        ('treated', 'Tratado'),
        ('accepted', 'Aceptado'),
        ('closed', 'Cerrado'),
    ]

    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name='risks', verbose_name="Proceso")
    category = models.ForeignKey(RiskCategory, on_delete=models.SET_NULL, null=True, related_name='risks', verbose_name="Categoría")
    code = models.CharField(max_length=20, unique=True, default='R-NEW', verbose_name="Código")
    title = models.CharField(max_length=200, verbose_name="Título del Riesgo")
    description = models.TextField(verbose_name="Descripción Detallada")
    
    # Inherent Risk

    # Evaluación Inherente (Configurable)
    inherent_probability = models.ForeignKey(
        ProbabilityScale, 
        on_delete=models.PROTECT,
        related_name='inherent_risks',
        null=True, blank=True,
        verbose_name="Probabilidad Inherente"
    )
    # For Impact, we might ideally select an ImpactScale for a specific dimension (e.g. Financial),
    # or just a generic Level if the user aggregates them manually. 
    # Based on the doc, they evaluate impact on 5 dimensions and take the *highest*.
    # For MVP simplicity while supporting the logic: user selects the calculated level 1-5 
    # OR we let them pick the level directly. Let's use a simple 1-5 integer field that references the scale level 
    # but we can enforce it matches a valid ImpactScale level.
    # actually, better to link to an ImpactScale if we want to show the description.
    # But there are 5 dimensions. The doc says "quedando como resultado... aquel que tenga la valoración más alta".
    # So we store the *RESULTING* impact level (1-5).
    inherent_impact_level = models.PositiveIntegerField(
        verbose_name="Nivel Impacto Inherente (1-5)",
        default=1,
        choices=[(i, str(i)) for i in range(1, 6)]
    )

    # Evaluación Residual
    residual_probability = models.ForeignKey(
        ProbabilityScale,
        on_delete=models.PROTECT,
        related_name='residual_risks',
        null=True, blank=True,
        verbose_name="Probabilidad Residual"
    )
    residual_impact_level = models.PositiveIntegerField(
        verbose_name="Nivel Impacto Residual (1-5)",
        null=True, blank=True,
        choices=[(i, str(i)) for i in range(1, 6)]
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='identified', verbose_name="Estado")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Riesgo"
        verbose_name_plural = "Riesgos"
        ordering = ['-created']

    def __str__(self):
        return f"{self.code} - {self.title}"

    @property
    def inherent_risk_level_obj(self):
        """Calculates the Risk Level object based on the Matrix."""
        if not self.inherent_probability or not self.inherent_impact_level:
            return None
        try:
            rule = RiskMatrixRule.objects.get(
                probability_level=self.inherent_probability.level,
                impact_level=self.inherent_impact_level
            )
            return rule.risk_level
        except RiskMatrixRule.DoesNotExist:
            return None

    @property
    def residual_risk_level_obj(self):
        if not self.residual_probability or not self.residual_impact_level:
            return None
        try:
            rule = RiskMatrixRule.objects.get(
                probability_level=self.residual_probability.level,
                impact_level=self.residual_impact_level
            )
            return rule.risk_level
        except RiskMatrixRule.DoesNotExist:
            return None

    @property
    def inherent_display(self):
        lvl = self.inherent_risk_level_obj
        if lvl:
            return f"{lvl.name}"
        return "N/A"

    @property
    def residual_display(self):
        lvl = self.residual_risk_level_obj
        if lvl:
            return f"{lvl.name}"
        return "N/A"
