from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from risk_universe.models import Risk

@staff_member_required
def heatmap_view(request):
    # Get filters
    mode = request.GET.get('mode', 'inherent') # or 'residual'
    
    # 5x5 Matrix
    # We need to group risks by (prob, impact)
    matrix = {}
    for p in range(5, 0, -1): # row (Impact) 5 down to 1
        matrix[p] = {}
        for i in range(1, 6): # col (Prob) 1 to 5
            matrix[p][i] = []

    risks = Risk.objects.all()
    for risk in risks:
        prob = 1
        imp = 1
        
        if mode == 'residual':
            # Use residual if available, otherwise 1 (or handle as excluded)
            if risk.residual_probability and risk.residual_impact_level:
                prob = risk.residual_probability.level
                imp = risk.residual_impact_level
        else:
             if risk.inherent_probability and risk.inherent_impact_level:
                prob = risk.inherent_probability.level
                imp = risk.inherent_impact_level
            
        # Matrix indexing: imp is row (1-5), prob is col (1-5)
        # Check if valid range
        if imp in matrix and prob in matrix[imp]:
            matrix[imp][prob].append(risk)

    context = {
        'matrix': matrix,
        'mode': mode,
        'cols': range(1, 6),
        'rows': range(5, 0, -1),
    }
    return render(request, 'core/heatmap.html', context)
