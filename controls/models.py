from django.db import models
from simple_history.models import HistoricalRecords
from core.models import TimeStampedModel
from risk_universe.models import Risk

class Control(TimeStampedModel):
    # Oportunidad (35%)
    OPP_PREVENTIVE = 35
    OPP_DETECTIVE = 20
    OPP_NONE = 0
    OPPORTUNITY_CHOICES = [
        (OPP_PREVENTIVE, 'Preventivo (35%)'),
        (OPP_DETECTIVE, 'Detectivo (20%)'),
        (OPP_NONE, 'Sin Control (0%)'),
    ]

    # Alcance (20%)
    SCOPE_TOTAL = 20
    SCOPE_PARTIAL = 5
    SCOPE_NONE = 0
    SCOPE_CHOICES = [
        (SCOPE_TOTAL, 'Total - 100% Operaciones (20%)'),
        (SCOPE_PARTIAL, 'Parcial / Muestral (5%)'),
        (SCOPE_NONE, 'Sin Control (0%)'),
    ]

    # Tipo (20%)
    TYPE_AUTO = 20
    TYPE_SEMIAUTO = 15
    TYPE_MANUAL = 5
    TYPE_NONE = 0
    TYPE_CHOICES = [
        (TYPE_AUTO, 'Automático (20%)'),
        (TYPE_SEMIAUTO, 'Semiautomático (15%)'),
        (TYPE_MANUAL, 'Manual (5%)'),
        (TYPE_NONE, 'Sin Control (0%)'),
    ]

    # Segregación (15%)
    SEG_YES = 15
    SEG_NO = 0
    SEGREGATION_CHOICES = [
        (SEG_YES, 'Sí - Funciones separadas (15%)'),
        (SEG_NO, 'No - Misma función ejecuta y controla (0%)'),
    ]

    # Formalización (10%)
    FORM_YES = 10
    FORM_NO = 5
    FORM_NONE = 0
    FORMALIZATION_CHOICES = [
        (FORM_YES, 'Formalizado en documento (10%)'),
        (FORM_NO, 'No Formalizado / Informal (5%)'),
        (FORM_NONE, 'Sin Control (0%)'),
    ]

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    # New Weighted Fields
    weight_opportunity = models.IntegerField(choices=OPPORTUNITY_CHOICES, default=OPP_NONE, verbose_name="Oportunidad (35%)")
    weight_scope = models.IntegerField(choices=SCOPE_CHOICES, default=SCOPE_NONE, verbose_name="Alcance (20%)")
    weight_type = models.IntegerField(choices=TYPE_CHOICES, default=TYPE_NONE, verbose_name="Tipo (20%)")
    weight_segregation = models.IntegerField(choices=SEGREGATION_CHOICES, default=SEG_NO, verbose_name="Segregación (15%)")
    weight_formalization = models.IntegerField(choices=FORMALIZATION_CHOICES, default=FORM_NONE, verbose_name="Formalización (10%)")

    # Relationships
    risks = models.ManyToManyField('risk_universe.Risk', related_name='controls', blank=True)
    
    history = HistoricalRecords()

    class Meta:
        ordering = ['code']
        verbose_name = "Control"
        verbose_name_plural = "Controles"

    def __str__(self):
        return f"{self.code} - {self.name} ({self.effectiveness_score}%)"

    @property
    def effectiveness_score(self):
        """Calculates total effectiveness based on weights."""
        return (
            self.weight_opportunity +
            self.weight_scope +
            self.weight_type +
            self.weight_segregation +
            self.weight_formalization
        )

class ControlAssessment(TimeStampedModel):
    RESULT_CHOICES = [
        ('effective', 'Efectivo'),
        ('ineffective', 'Inefectivo'),
        ('needs_improvement', 'Necesita Mejora'),
    ]

    control = models.ForeignKey(Control, on_delete=models.CASCADE, related_name='assessments')
    assessor = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    date = models.DateField()
    
    # Assessments can now compare calculated theoretical effectiveness vs observed
    design_effectiveness = models.CharField(max_length=20, choices=[('Effective', 'Effective'), ('Ineffective', 'Ineffective')])
    operational_effectiveness = models.CharField(max_length=20, choices=[('Effective', 'Effective'), ('Ineffective', 'Ineffective')])
    
    observations = models.TextField(blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Evaluación de Control"
        verbose_name_plural = "Evaluaciones de Control"
        ordering = ['-date']

    def __str__(self):
        return f"Eval {self.control.code} - {self.date}"
