from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Risk, Process
from methodology.models import ProbabilityScale
from configurations.models import ConfigList, ConfigListItem, FieldRecommendation, ControlRecommendation
import json

def get_orphan_risks(request):
    """Returns a list of risks that don't have a process assigned."""
    orphans = Risk.objects.filter(process__isnull=True).values('id', 'code', 'title')
    return JsonResponse(list(orphans), safe=False)

@csrf_exempt
def link_risks_to_process(request):
    """Links a list of risk IDs to a specific process ID or unlinks if process_id is null."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            process_id = data.get('process_id')
            risk_ids = data.get('risk_ids', [])
            
            process = None
            if process_id:
                process = get_object_or_404(Process, id=process_id)
            
            # Update risks process field (can be None)
            Risk.objects.filter(id__in=risk_ids).update(process=process)
            
            msg = f'{len(risk_ids)} riesgos vinculados.' if process else f'{len(risk_ids)} riesgos desvinculados.'
            return JsonResponse({'status': 'success', 'message': msg})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Solo POST'}, status=405)
@csrf_exempt
def create_and_link_risk(request):
    """Creates a new risk and links it to a specific process ID."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            process_id = data.get('process_id')
            title = data.get('title')
            
            if not title:
                return JsonResponse({'status': 'error', 'message': 'Título requerido.'}, status=400)
                
            process = get_object_or_404(Process, id=process_id)
            
            # Create the risk
            new_risk = Risk.objects.create(
                title=title,
                process=process,
                status='identified' # Default status matching choices
            )
            
            return JsonResponse({
                'status': 'success', 
                'message': f'Riesgo creado y vinculado.',
                'id': new_risk.id,
                'code': new_risk.code
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Solo POST'}, status=405)
@csrf_exempt
def suggest_fields_api(request):
    """
    Contract-stable endpoint for field suggestions. 
    Uses factor_riesgo_especifico as primary source.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Solo POST'}, status=405)
        
    try:
        data = json.loads(request.body)
        risk_id = data.get('risk_id')
        risk = get_object_or_404(Risk, id=risk_id)
        
        # Source text for suggestion logic
        source_text = risk.factor_riesgo_especifico.lower() if risk.factor_riesgo_especifico else ""
        
        # Simple MOCK rule-based logic (to be replaced by LLM)
        suggestions = []
        
        # 1. Basilea
        basilea_list = ConfigList.objects.get(technical_name='tipos_perdida_basilea')
        if 'fraude' in source_text:
            val = basilea_list.items.filter(technical_name='tipos_perdida_basilea_fraude_interno').first()
        elif 'sistema' in source_text or 'tecnologia' in source_text:
            val = basilea_list.items.filter(technical_name='tipos_perdida_basilea_incidencias_en_el_negocio_y_fallas_en_los_sistemas').first()
        else:
            val = basilea_list.items.filter(technical_name='tipos_perdida_basilea_ejecucion_entrega_y_gestion_de_procesos').first()
        
        if val:
            suggestions.append({'field': 'basilea_loss_type', 'value_id': val.id, 'label': val.label})

        # 2. Risk Factor
        factor_list = ConfigList.objects.get(technical_name='factor_de_riesgo')
        if 'persona' in source_text or 'empleado' in source_text:
            val = factor_list.items.filter(technical_name='factor_de_riesgo_falta_de_personal_capacitado').first()
        elif 'tecnologia' in source_text or 'sistema' in source_text:
            val = factor_list.items.filter(technical_name='factor_de_riesgo_obsolescencia_tecnologica').first()
        else:
            val = factor_list.items.filter(technical_name='factor_de_riesgo_fallas_en_los_procesos_operativos').first()
            
        if val:
            suggestions.append({'field': 'risk_factor', 'value_id': val.id, 'label': val.label})

        # 3. Loss Risk Type
        loss_list = ConfigList.objects.get(technical_name='riesgos_de_perdida')
        if 'multa' in source_text or 'sancion' in source_text:
            val = loss_list.items.filter(technical_name='riesgos_de_perdida_multas_y_sanciones').first()
        else:
            val = loss_list.items.filter(technical_name='riesgos_de_perdida_costos_adicionales_del_proceso').first()

        if val:
            suggestions.append({'field': 'loss_risk_type', 'value_id': val.id, 'label': val.label})

        # Save Field Recommendations as RECOMMENDED (not pending)
        for sug in suggestions:
            FieldRecommendation.objects.update_or_create(
                risk=risk,
                field_name=sug['field'],
                defaults={
                    'recommended_value_id': sug['value_id'],
                    'status': 'recommended'
                }
            )

        # 4. Suggested Controls (Mock for now, linking to existing controls or creating them as recos)
        # In a real scenario, LLM would suggest codes or search DB.
        from controls.models import Control
        suggested_controls = Control.objects.all()[:2] # Dummy suggestion
        for ctrl in suggested_controls:
            ControlRecommendation.objects.update_or_create(
                risk=risk,
                control=ctrl,
                defaults={'status': 'recommended'}
            )

        return JsonResponse({
            'status': 'success',
            'suggestions': suggestions,
            'control_suggestions': [{'id': c.id, 'code': c.code, 'name': c.name} for c in suggested_controls]
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
def recommendation_action_api(request):
    """Handles accepting or overriding a recommendation."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Solo POST'}, status=405)
        
    try:
        data = json.loads(request.body)
        risk_id = data.get('risk_id')
        field_name = data.get('field_name')
        control_id = data.get('control_id')
        action = data.get('action') # 'accept' or 'dismiss' or 'override'
        
        if field_name:
            reco = get_object_or_404(FieldRecommendation, risk_id=risk_id, field_name=field_name)
            if action == 'accept':
                reco.status = 'accepted'
                setattr(reco.risk, field_name, reco.recommended_value)
                reco.risk.save()
            elif action == 'dismiss':
                reco.status = 'dismissed'
            elif action == 'override':
                reco.status = 'overridden'
            reco.save()
        elif control_id:
            reco = get_object_or_404(ControlRecommendation, risk_id=risk_id, control_id=control_id)
            if action == 'accept':
                reco.status = 'accepted'
                # Link the control to the risk
                reco.risk.controls.add(reco.control)
                # If first control, maybe set as principal? 
                # User says: "Aceptar crea vínculo real (o asigna principal)"
                if not reco.risk.control_principal:
                    reco.risk.control_principal = reco.control
                    reco.risk.save()
            elif action == 'dismiss':
                reco.status = 'dismissed'
            elif action == 'override':
                reco.status = 'overridden'
            reco.save()
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def get_recommendations_api(request, risk_id):
    """Returns all field recommendations for a given risk."""
    recos = FieldRecommendation.objects.filter(risk_id=risk_id).values(
        'field_name', 'recommended_value_id', 'recommended_value__label', 'status'
    )
    return JsonResponse(list(recos), safe=False)

def get_control_recommendations_api(request, risk_id):
    """Returns all control recommendations for a given risk."""
    recos = ControlRecommendation.objects.filter(risk_id=risk_id).values(
        'control_id', 'control__code', 'control__name', 'status'
    )
    return JsonResponse(list(recos), safe=False)

@csrf_exempt
def calculate_risk_preview_api(request):
    """Calculates risk levels based on input without saving."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Solo POST'}, status=405)
    
    try:
        data = json.loads(request.body)
        print(f"DEBUG API CALC RECIEVED: {data}") # Explicit Logging
        
        def safe_int_impact(val, text_val, field_name="unknown"):
            # 1. Try direct integer parse
            try:
                if val is not None:
                    return int(float(str(val).strip()))
            except:
                pass
            
            # 2. Try text mapping (Robust Fallback)
            if text_val:
                s = str(text_val).lower().strip()
                if "medio alto" in s: return 4
                if "medio bajo" in s: return 2
                if "alto" in s: return 5
                if "medio" in s: return 3
                if "bajo" in s: return 1
            
            print(f"  [WARN] Impact {field_name} failed to parse val='{val}' text='{text_val}' -> Defaulting to 1")
            return 1

        # 1. Inherent Impact
        impact_monetary = safe_int_impact(data.get('impact_monetary'), data.get('impact_monetary_text'), "monetary")
        impact_clients = safe_int_impact(data.get('impact_clients'), data.get('impact_clients_text'), "clients")
        impact_reputational = safe_int_impact(data.get('impact_reputational'), data.get('impact_reputational_text'), "reputational")
        impact_regulatory = safe_int_impact(data.get('impact_regulatory'), data.get('impact_regulatory_text'), "regulatory")
        impact_processes = safe_int_impact(data.get('impact_processes'), data.get('impact_processes_text'), "processes")
        
        impact_inherent = max(impact_monetary, impact_clients, impact_reputational, impact_regulatory, impact_processes)
        print(f"  Inherent Impact Level: {impact_inherent} (Max of {impact_monetary},{impact_clients},{impact_reputational},{impact_regulatory},{impact_processes})")
        
        # 2. Probability
        prob_str = str(data.get('inherent_probability_text', ''))
        import re
        match = re.search(r'\d+', prob_str)
        if match:
             prob_val = int(match.group())
        else:
             # Try raw value if specifically sent
             prob_val = safe_int(data.get('inherent_probability_val'), "prob_raw")
             if prob_val > 5: prob_val = 1 # IDs vs Levels

        print(f"  Probability Value: {prob_val} (from '{prob_str}')")
        
        score_inherent = impact_inherent * prob_val
        print(f"  Inherent Score: {score_inherent}")
        print(f"DEBUG API CALC: Impact={impact_inherent}, Prob={prob_val}, Score={score_inherent}")
        
        # Inherent Risk Name
        if score_inherent >= 20: 
            ri_name = "Alto"
        elif impact_inherent == 5 and prob_val == 1:
            ri_name = "Medio Alto"
        elif score_inherent <= 3: 
            ri_name = "Bajo"
        elif score_inherent <= 4: # Changed from 5 to 4
            ri_name = "Medio Bajo"
        elif score_inherent <= 10: 
            ri_name = "Medio"
        elif score_inherent <= 19: 
            ri_name = "Medio Alto"
        else: 
            ri_name = "Alto"
        
        # 3. Entorno
        entorno_raw = data.get('best_control_environment_text', '1')
        print(f"  Entorno Raw: '{entorno_raw}'")
        match_ent = re.search(r'\d+', str(entorno_raw))
        if match_ent:
             entorno_val = int(match_ent.group())
        else:
             entorno_val = 1
            
        score_residual = score_inherent / entorno_val
        print(f"  Residual Score: {score_residual} (Inherent {score_inherent} / Entorno {entorno_val})")
        
        # Residual Risk Name
        if entorno_val == 1:
            rr_name = ri_name
        else:
            if score_residual <= 3: rr_name = "Bajo"
            elif score_residual <= 4: rr_name = "Medio Bajo" # Changed from 5 to 4
            elif score_residual <= 10: rr_name = "Medio"
            elif score_residual <= 19: rr_name = "Medio Alto"
            else: rr_name = "Alto"
            
        # 4. Requiere Indicador & Plan
        # Methodology: Anything High or Medio Alto requires a plan. 
        # For indicators: High Inherent AND (High or Medium Residual)
        ri_high = ri_name in ["Medio Alto", "Alto"]
        rr_medium_plus = rr_name in ["Medio", "Medio Alto", "Alto"]
        
        req_kri = ri_high and rr_medium_plus
        req_plan = rr_name in ["Medio", "Medio Alto", "Alto"] 
        
        print(f"  [PLAN-DEBUG] RR={rr_name}, req_plan={req_plan}")
        print(f"  [KRI-DEBUG] RI={ri_name}, RR={rr_name}, req_kri={req_kri}")

        return JsonResponse({
            'status': 'success',
            'inherent_impact_level': impact_inherent,
            'inherent_risk_name': ri_name,
            'residual_impact_level': impact_inherent,
            'residual_risk_name': rr_name,
            'requiere_indicador': req_kri,
            'requiere_kri': req_kri,  # Explicit mapping
            'requiere_plan_accion': req_plan,
            'requiere_plan': req_plan   # Explicit mapping
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
