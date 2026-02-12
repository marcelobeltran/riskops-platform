from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class ImpactDimension(models.Model):
    """
    Dimensions of impact defined in the methodology (e.g., Monetario, Clientes, Reputacional).
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

class ImpactScale(models.Model):
    """
    Definitions for each level of impact within a specific dimension.
    e.g. Level 1 (Bajo) for 'Monetario' means 'Up to 0.01% revenue'.
    """
    dimension = models.ForeignKey(ImpactDimension, on_delete=models.CASCADE, related_name='scales')
    level = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    name = models.CharField(max_length=50) # e.g. "Bajo", "Medio Bajo"
    description = models.TextField() # The specific criteria for this level/dimension
    
    class Meta:
        ordering = ['dimension', 'level']
        unique_together = ['dimension', 'level']

    def __str__(self):
        return f"{self.dimension} - L{self.level} ({self.name})"

class ProbabilityScale(models.Model):
    """
    Definitions for Probability levels.
    """
    level = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], unique=True)
    name = models.CharField(max_length=50) # e.g. "Muy poco probable"
    description = models.TextField() # e.g. "No existen antecedentes..."
    occurrence_criteria = models.TextField(blank=True, help_text="Specific criteria like '% of cases' or 'times per year'")

    class Meta:
        ordering = ['level']

    def __str__(self):
        return f"L{self.level} - {self.name}"

class RiskLevel(models.Model):
    """
    The resulting risk classification (e.g. Bajo, Medio, Alto, Crítico).
    """
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20, help_text="Hex code or name (e.g. #FF0000, red)")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

class RiskMatrixRule(models.Model):
    """
    Configures the heatmap: Probability Level + Impact Level = Risk Level.
    """
    probability_level = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    impact_level = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    risk_level = models.ForeignKey(RiskLevel, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['probability_level', 'impact_level']
        verbose_name = "Matrix Configuration Rule"

    def __str__(self):
        return f"P{self.probability_level} x I{self.impact_level} = {self.risk_level}"
