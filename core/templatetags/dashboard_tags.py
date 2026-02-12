from django import template
from risk_universe.models import Process, Risk
from monitoring.models import KRI, ActionPlan
from django.db.models import Count, Q

register = template.Library()

@register.inclusion_tag('admin/dashboard_stats.html')
def get_dashboard_summary():
    # 1. Critical Processes
    critical_processes = Process.objects.filter(criticality__in=['high', 'medium']).count()
    
    # 2. Top 10 Risks (Residual Level)
    # We can't order by property easily in DB without annotation. 
    # For MVP, we'll fetch all and sort in python or assume inherent is close enough for DB sorting if field persisted.
    # But I defined residual_probability/impact as fields.
    # Let's annotate valid residual levels.
    # Logic: If residual values exist, use them, else Use inherent.
    # For MVP simplicity, I'll filter where residual is set OR just show top Inherent for now if residual is null?
    # Better: Use python sorting for the top 10 since database size is small for MVP.
    
    all_risks = Risk.objects.all()
    # Mocking calculation for sorting
    sorted_risks = sorted(all_risks, key=lambda r: r.residual_risk_level_obj.order if r.residual_risk_level_obj else 0, reverse=True)[:10]
    
    # 3. KRIs
    kris_red = 0
    kris_amber = 0
    # Need to iterate to check threshold logic defined in Admin/Model logic.
    # For MVP efficiently:
    all_kris = KRI.objects.all()
    kris_red_list = []
    kris_amber_list = []
    
    for k in all_kris:
        if k.current_value is None: continue
        if k.current_value > k.threshold_red: # Assuming > is bad
            kris_red += 1
            kris_red_list.append(k)
        elif k.current_value > k.threshold_yellow:
            kris_amber += 1
            kris_amber_list.append(k)
            
    # 4. Action Plans
    plans_overdue = ActionPlan.objects.filter(status='overdue').count()
    plans_open = ActionPlan.objects.filter(status__in=['pending', 'in_progress']).count()

    return {
        'critical_processes': critical_processes,
        'top_risks': sorted_risks,
        'kris_red': kris_red,
        'kris_amber': kris_amber,
        'plans_overdue': plans_overdue,
        'plans_open': plans_open,
    }
