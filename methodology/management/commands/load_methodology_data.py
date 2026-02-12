from django.core.management.base import BaseCommand
from methodology.models import ImpactDimension, ImpactScale, ProbabilityScale, RiskLevel, RiskMatrixRule

class Command(BaseCommand):
    help = 'Load standard methodology data (Impacts, Probabilities, Matrix)'

    def handle(self, *args, **options):
        # 1. Impact Dimensions
        dimensions = [
            ('Monetario', 'Impacto financiero directo'),
            ('Clientes', 'Afectación a clientes'),
            ('Reputacional', 'Impacto en imagen pública'),
            ('Normativo', 'Sanciones o incumplimientos'),
            ('Procesos', 'Afectación a la continuidad de negocio')
        ]
        
        dims_obj = {}
        for i, (name, desc) in enumerate(dimensions, 1):
            obj, created = ImpactDimension.objects.get_or_create(
                name=name, 
                defaults={'description': desc, 'order': i}
            )
            dims_obj[name] = obj
            self.stdout.write(f"Dimension: {name}")

        # 2. Impact Scales (Simplified for initial load, can be expanded)
        # Using generic descriptions from doc, mapped to each dimension briefly
        impact_levels = [
            (1, 'Bajo', 'Hasta 0.01% ingreso / No afecta clientes / No relevante'),
            (2, 'Medio Bajo', 'Hasta 0.03% / Grupo reducido / Conocimiento interno'),
            (3, 'Medio', 'Hasta 0.06% / 5k-25k clientes / Medios no masivos'),
            (4, 'Medio Alto', 'Hasta 0.09% / Crítico para clientes / Redes sociales'),
            (5, 'Alto', '> 0.09% / Masivo (>25k) / Prensa nacional')
        ]

        for dim_name, dim_obj in dims_obj.items():
            for level, label, desc in impact_levels:
                ImpactScale.objects.get_or_create(
                    dimension=dim_obj,
                    level=level,
                    defaults={'name': label, 'description': desc}
                )
        self.stdout.write(f"Impact Scales loaded for all dimensions.")

        # 3. Probability Scales
        probs = [
            (1, 'Muy poco probable', '1 vez cada 10 años'),
            (2, 'Poco Probable', '1 vez cada 3 años'),
            (3, 'Ocasional', '1 vez al año (<2% casos)'),
            (4, 'Frecuente', 'Trimestral (2-10% casos)'),
            (5, 'Muy frecuente', 'Mensual (>10% casos)')
        ]
        for level, label, crit in probs:
            ProbabilityScale.objects.get_or_create(
                level=level,
                defaults={'name': label, 'description': label, 'occurrence_criteria': crit}
            )
        self.stdout.write(f"Probability Scales loaded.")

        # 4. Risk Levels (Colors)
        # Bajo (Green), Medio Bajo (YellowGreen), Medio (Yellow), Medio Alto (Orange), Alto (Red), Crítico (DarkRed)
        risk_levels = [
             (1, 'Bajo', '#28a745'),       # Green
             (2, 'Medio Bajo', '#aadd22'), # Light Green
             (3, 'Medio', '#ffc107'),      # Yellow
             (4, 'Medio Alto', '#fd7e14'), # Orange
             (5, 'Alto', '#dc3545'),       # Red
        ]
        
        levels_obj = {}
        for order, (lvl_val, label, color) in enumerate(risk_levels, 1):
             obj, _ = RiskLevel.objects.get_or_create(name=label, defaults={'color': color, 'order': lvl_val})
             levels_obj[lvl_val] = obj

        # 5. Matrix Rules (5x5)
        # Logic approximation based on doc matrix
        # P x I
        matrix_map = {
             # Prob 1
             (1,1): 1, (1,2): 1, (1,3): 1, (1,4): 2, (1,5): 4, 
             # Prob 2
             (2,1): 1, (2,2): 2, (2,3): 2, (2,4): 3, (2,5): 4,
             # Prob 3
             (3,1): 2, (3,2): 2, (3,3): 3, (3,4): 4, (3,5): 5,
             # Prob 4
             (4,1): 2, (4,2): 3, (4,3): 4, (4,4): 5, (4,5): 5,
             # Prob 5
             (5,1): 2, (5,2): 3, (5,3): 5, (5,4): 5, (5,5): 5,
        }

        for (prob, imp), risk_val in matrix_map.items():
            RiskMatrixRule.objects.get_or_create(
                 probability_level=prob,
                 impact_level=imp,
                 defaults={'risk_level': levels_obj[risk_val]}
            )
        self.stdout.write(f"Matrix Rules loaded.")
