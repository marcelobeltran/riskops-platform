from django import template
from risk_universe.models import Process, Risk
from monitoring.models import KRI, ActionPlan
from django.db.models import Count, Q

register = template.Library()

@register.inclusion_tag('admin/dashboard_stats.html')
def get_dashboard_summary():
    # 1. Critical Processes
    critical_processes = Process.objects.filter(criticality__in=['high', 'medium']).count()
    
    all_risks = Risk.objects.all()
    sorted_risks = sorted(all_risks, key=lambda r: r.inherent_risk_level_obj.order if r.inherent_risk_level_obj else 0, reverse=True)[:10]
    
    # 3. KRIs
    kris_red = 0
    kris_amber = 0
    all_kris = KRI.objects.all()
    for k in all_kris:
        if k.current_value is None: continue
        if k.current_value > k.threshold_red: # Assuming > is bad
            kris_red += 1
        elif k.current_value > k.threshold_yellow:
            kris_amber += 1
            
    # 4. Action Plans
    plans_overdue = ActionPlan.objects.filter(status='overdue').count()
    plans_open = ActionPlan.objects.filter(status__in=['pending', 'in_progress']).count()

    # 5. Risk Distribution Chart Data
    risk_counts = {
        'Bajo': len([r for r in all_risks if r.residual_display == 'Bajo']),
        'Medio_Bajo': len([r for r in all_risks if r.residual_display == 'Medio Bajo']),
        'Medio': len([r for r in all_risks if r.residual_display == 'Medio']),
        'Medio_Alto': len([r for r in all_risks if r.residual_display == 'Medio Alto']),
        'Alto': len([r for r in all_risks if r.residual_display == 'Alto']),
    }

    # 6. Mini Matrix Data (Inherent)
    mini_matrix = {}
    for p in range(5, 0, -1):
        mini_matrix[p] = {}
        for i in range(1, 6):
            count = len([r for r in all_risks if (r.inherent_probability.level if r.inherent_probability else 1) == p and r.inherent_impact_level == i])
            # Level based on Excel formula
            score = p * i
            if i == 5 and p == 1: lvl = "Medio Alto"
            elif score <= 2.99: lvl = "Bajo"
            elif score <= 4.99: lvl = "Medio Bajo"
            elif score <= 9.99: lvl = "Medio"
            elif score <= 14.99: lvl = "Medio Alto"
            else: lvl = "Alto"
            mini_matrix[p][i] = {'count': count, 'level': lvl}

    return {
        'critical_processes': critical_processes,
        'top_risks': sorted_risks,
        'kris_red': kris_red,
        'kris_amber': kris_amber,
        'plans_overdue': plans_overdue,
        'plans_open': plans_open,
        'risk_counts': risk_counts,
        'mini_matrix': mini_matrix,
        'rows': range(5, 0, -1),
        'cols': range(1, 6),
    }

@register.filter
def get_item(dictionary, key):
    """Template filter to get an item from a dictionary by key."""
    return dictionary.get(key)
