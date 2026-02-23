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
    owner = models.ForeignKey(
        'RiskOwner',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='processes_owned',
        verbose_name="Dueño del Proceso"
    )
    analyst = models.CharField(max_length=100, blank=True, null=True, verbose_name="Analista Asignado")
    criticality = models.CharField(
        max_length=10, 
        choices=CRITICALITY_CHOICES, 
        default='medium',
        verbose_name="Criticidad"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
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

class RiskControlLink(TimeStampedModel):
    risk = models.ForeignKey('Risk', on_delete=models.CASCADE, related_name='control_links')
    control = models.ForeignKey('controls.Control', on_delete=models.CASCADE, related_name='risk_links')

    class Meta:
        verbose_name = "Vínculo de Control"
        verbose_name_plural = "Vínculos de Controles"
        unique_together = ('risk', 'control')

    def __str__(self):
        return f"{self.risk.code} - {self.control.code}"

class RiskOwner(TimeStampedModel):
    name = models.CharField(max_length=200, verbose_name="Nombre")
    email = models.EmailField(unique=True, null=True, blank=True, verbose_name="Email")
    area = models.CharField(max_length=150, blank=True, verbose_name="Área / Cargo")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Dueño de Riesgo"
        verbose_name_plural = "Catálogo de Dueños"

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

    process = models.ForeignKey(Process, on_delete=models.SET_NULL, null=True, blank=True, related_name='risks', verbose_name="Proceso")
    category = models.ForeignKey(RiskCategory, on_delete=models.SET_NULL, null=True, related_name='risks', verbose_name="Categoría")
    code = models.CharField(max_length=20, unique=True, blank=True, verbose_name="Código")
    title = models.CharField(max_length=200, verbose_name="Riesgos de Pérdida")
    description = models.TextField(verbose_name="Descripción Detallada")
    
    # Responsables
    responsible_analyst = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name='risks_as_analyst', 
        verbose_name="Analista Responsable"
    )
    risk_owner = models.ForeignKey(
        'RiskOwner', 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name='risks_as_owner', 
        verbose_name="Dueño del Riesgo"
    )
    
    # New Excel-aligned fields
    etapas_actividades = models.TextField(blank=True, verbose_name="Etapas o Actividades")
    # New Configurable List Fields (FKs)
    basilea_loss_type = models.ForeignKey(
        'configurations.ConfigListItem', 
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='risks_basilea',
        limit_choices_to={'config_list__technical_name': 'tipos_perdida_basilea'},
        verbose_name="Tipo de Pérdida Basilea (Lista)"
    )
    loss_risk_type = models.ForeignKey(
        'configurations.ConfigListItem', 
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='risks_loss_type',
        limit_choices_to={'config_list__technical_name': 'riesgos_de_perdida'},
        verbose_name="Riesgos de Pérdida (Lista)"
    )
    risk_factor = models.ForeignKey(
        'configurations.ConfigListItem', 
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='risks_factor',
        limit_choices_to={'config_list__technical_name': 'factor_de_riesgo'},
        verbose_name="Factor de Riesgo (Lista)"
    )

    factor_riesgo = models.CharField(max_length=200, blank=True, verbose_name="Factor de Riesgo (Legacy)")
    factor_riesgo_especifico = models.CharField(max_length=200, blank=True, verbose_name="Factor de Riesgo Específico")
    is_factor_riesgo_especifico_ai_suggested = models.BooleanField(default=False, verbose_name="Sugerido por IA")
    is_factor_riesgo_especifico_overridden = models.BooleanField(default=False, verbose_name="Editado manualmente")
    
    antecedent = models.TextField(blank=True, verbose_name="Antecedente de Riesgo")
    ai_context = models.TextField(blank=True, verbose_name="Contexto IA/Entrevista", help_text="Información capturada por la IA para sugerir este riesgo.")
    
    requiere_indicador = models.BooleanField(default=False, verbose_name="Requiere indicador")
    requiere_plan_accion = models.BooleanField(default=False, verbose_name="Requiere plan de acción")
    
    control_principal = models.ForeignKey(
        'controls.Control',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='principal_risks',
        verbose_name="Control Principal"
    )
    
    # Many to many via through model
    controls = models.ManyToManyField(
        'controls.Control', 
        through='RiskControlLink', 
        related_name='risks_linked', 
        blank=True, 
        verbose_name="Controles Vinculados"
    )
    
    # save method relocated and consolidated below
    
    # Inherent Risk Dimensions Categories
    IMPACT_CATEGORIES = [
        (1, 'Bajo'),
        (2, 'Medio Bajo'),
        (3, 'Medio'),
        (4, 'Medio Alto'),
        (5, 'Alto'),
    ]

    impact_monetary = models.PositiveIntegerField(
        verbose_name="Monetario",
        default=1, choices=IMPACT_CATEGORIES
    )
    impact_clients = models.PositiveIntegerField(
        verbose_name="Clientes",
        default=1, choices=IMPACT_CATEGORIES
    )
    impact_reputational = models.PositiveIntegerField(
        verbose_name="Reputacional",
        default=1, choices=IMPACT_CATEGORIES
    )
    impact_regulatory = models.PositiveIntegerField(
        verbose_name="Normativo",
        default=1, choices=IMPACT_CATEGORIES
    )
    impact_processes = models.PositiveIntegerField(
        verbose_name="Procesos",
        default=1, choices=IMPACT_CATEGORIES
    )

    # Evaluación Inherente
    inherent_probability = models.ForeignKey(
        ProbabilityScale, 
        on_delete=models.PROTECT,
        related_name='inherent_risks',
        null=True, blank=True,
        verbose_name="Probabilidad"
    )
    
    # Database fields for previously calculated properties to allow manual overrides
    inherent_impact_level = models.PositiveIntegerField(
        verbose_name="Nivel de Impacto Inherente (1-5)",
        default=1, choices=[(i, str(i)) for i in range(1, 6)]
    )
    inherent_risk_name = models.CharField(max_length=50, blank=True, verbose_name="Riesgo Inherente")
    # manual_inherent_override removed

    # Evaluación Residual
    residual_probability = models.ForeignKey(
        ProbabilityScale,
        on_delete=models.PROTECT,
        related_name='residual_risks',
        null=True, blank=True,
        verbose_name="Probabilidad Residual"
    )
    
    residual_impact_level = models.PositiveIntegerField(
        verbose_name="Nivel de Impacto Residual (1-5)",
        default=1, choices=[(i, str(i)) for i in range(1, 6)]
    )
    residual_risk_name = models.CharField(max_length=50, blank=True, verbose_name="Riesgo Residual")
    # manual_residual_override removed

    is_active = models.BooleanField(default=True, verbose_name="Activo")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='identified', verbose_name="Estado")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Riesgo"
        verbose_name_plural = "Riesgos"
        ordering = ['-created']

    def __str__(self):
        return f"{self.code} - {self.title}"

    def save(self, *args, **kwargs):
        # 1. Generate code
        if not self.code or self.code == 'R-NEW':
            try:
                last_risk = Risk.objects.filter(code__regex=r'^R-\d+').order_by('-code').first()
                if not last_risk: self.code = 'R-001'
                else:
                    import re
                    match = re.search(r'R-(\d+)', last_risk.code)
                    if match: self.code = f'R-{int(match.group(1)) + 1:03d}'
                    else: self.code = f'R-{Risk.objects.count() + 1:03d}'
            except: self.code = f'R-{Risk.objects.count() + 1:03d}'

        # 2. Impacto = MAX(...)
        self.inherent_impact_level = max(
            self.impact_monetary, self.impact_clients, self.impact_reputational,
            self.impact_regulatory, self.impact_processes
        )
        
        # 3. Probabilidad (Level)
        prob_val = self.inherent_probability.level if self.inherent_probability else 1
        
        # 4. Puntaje Inherente
        score_inherent = self.inherent_impact_level * prob_val
        
        # 5. Riesgo Inherente Name Logic
        if self.inherent_impact_level == 5 and prob_val == 1:
            self.inherent_risk_name = "Medio Alto"
        elif score_inherent <= 3: self.inherent_risk_name = "Bajo"
        elif score_inherent <= 4: self.inherent_risk_name = "Medio Bajo" # Changed from 5 to 4
        elif score_inherent <= 10: self.inherent_risk_name = "Medio"
        elif score_inherent <= 19: self.inherent_risk_name = "Medio Alto"
        else: self.inherent_risk_name = "Alto"

        # 6. Entorno Control (Best)
        entorno_val = self.best_control_environment_value
        
        # 7. Puntaje Residual
        score_residual = score_inherent / entorno_val
        
        # 8. Riesgo Residual Name Logic
        if entorno_val == 1:
            self.residual_risk_name = self.inherent_risk_name
        elif self.inherent_impact_level == 5 and prob_val == 1 and entorno_val == 3:
            self.residual_risk_name = "Medio Bajo"
        elif self.inherent_impact_level == 5 and prob_val == 1 and entorno_val == 2:
            self.residual_risk_name = "Medio"
        else:
            if score_residual <= 3: self.residual_risk_name = "Bajo"
            elif score_residual <= 4: self.residual_risk_name = "Medio Bajo" # Changed from 5 to 4
            elif score_residual <= 10: self.residual_risk_name = "Medio"
            elif score_residual <= 19: self.residual_risk_name = "Medio Alto"
            else: self.residual_risk_name = "Alto"

        # 9. Requiere Indicador & Plan
        # Radi = SI si (RI in {MA, A}) y (RR in {M, MA, A})
        ri_high = self.inherent_risk_name in ["Medio Alto", "Alto"]
        rr_medium_plus = self.residual_risk_name in ["Medio", "Medio Alto", "Alto"]
        self.requiere_indicador = ri_high and rr_medium_plus
        
        # Rap = SI si (RR in {M, MA, A}) # Changed to include Medio
        self.requiere_plan_accion = self.residual_risk_name in ["Medio", "Medio Alto", "Alto"]

        super().save(*args, **kwargs)

    @property
    def best_control_environment_value(self):
        """Gets the best environment value (max) from all linked controls. Defaults to 1."""
        if not self.pk: return 1
        all_controls = set()
        # We can't access controls.all() reliably before save if it's a new instance, 
        # but for existing ones we can.
        try:
            for c in self.controls.all(): all_controls.add(c)
        except: pass
        if not all_controls: return 1
        
        best = 1
        for c in all_controls:
            entorno_str = c.entorno_control # e.g. "3 SUFICIENTE"
            try:
                val = int(entorno_str.split()[0])
                if val > best: best = val
            except: pass
        return best

    @property
    def control_effectiveness_total(self):
        """Calculates the weighted average effectiveness of principal + all linked controls."""
        if not self.pk:
            return 0
        
        all_controls = set()
        if self.control_principal:
            all_controls.add(self.control_principal)
        
        for c in self.controls.all():
            all_controls.add(c)
            
        if not all_controls:
            return 0
            
        total = sum(c.efectividad_control for c in all_controls)
        return round(total / len(all_controls), 2)

    @property
    def inherent_display(self):
        return self.inherent_risk_name

    @property
    def residual_display(self):
        return self.residual_risk_name

    @property
    def inherent_risk_level_name(self):
        return self.inherent_risk_name

    @property
    def residual_risk_level_name(self):
        return self.residual_risk_name

    @property
    def inherent_risk_level_obj(self):
        """Retrieves the RiskLevel object matching the name from database field."""
        from methodology.models import RiskLevel
        try:
            return RiskLevel.objects.get(name__iexact=self.inherent_risk_name)
        except Exception:
            return None

    @property
    def residual_risk_level_obj(self):
        """Retrieves the RiskLevel object matching the name from database field."""
        from methodology.models import RiskLevel
        try:
            return RiskLevel.objects.get(name__iexact=self.residual_risk_name)
        except Exception:
            return None
