from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from risk_universe.models import Risk

@staff_member_required
def heatmap_view(request):
    mode = request.GET.get('mode', 'inherent') # 'inherent' or 'residual'
    
    # 5x5 Matrix: rows are Probability (1-5), cols are Impact (1-5)
    matrix = {}
    for p in range(5, 0, -1): # Prob 5 down to 1
        matrix[p] = {}
        for i in range(1, 6): # Impact 1 to 5
            matrix[p][i] = {
                'count': 0,
                'risks': [],
                'level': ''
            }
            # Excel formula logic
            score = p * i
            if i == 5 and p == 1:
                lvl = "Medio Alto"
            elif score <= 2.99:
                lvl = "Bajo"
            elif score <= 4.99:
                lvl = "Medio Bajo"
            elif score <= 9.99:
                lvl = "Medio"
            elif score <= 14.99:
                lvl = "Medio Alto"
            else:
                lvl = "Alto"
            matrix[p][i]['level'] = lvl

    risks = Risk.objects.all()
    for risk in risks:
        if mode == 'residual':
            prob = risk.residual_probability.level if risk.residual_probability else (risk.inherent_probability.level if risk.inherent_probability else 1)
            imp = risk.residual_impact_level
        else:
            prob = risk.inherent_probability.level if risk.inherent_probability else 1
            imp = risk.inherent_impact_level
            
        if prob in matrix and imp in matrix[prob]:
            matrix[prob][imp]['count'] += 1
            matrix[prob][imp]['risks'].append(risk)

    context = {
        'matrix': matrix,
        'mode': mode,
        'impact_range': range(1, 6),
        'probability_range': range(5, 0, -1),
        'risks': risks,
    }
    return render(request, 'risk_universe/heatmap.html', context)
