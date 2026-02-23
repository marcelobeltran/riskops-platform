from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from .services import KnowledgeService
from .models import InterviewSession, InterviewFinding
from .risk_advisor import RiskAdvisor
from .agents.orchestrator import RiskAnalystOrchestrator
from .agents.interview_orchestrator import InterviewIntelligenceOrchestrator
from risk_universe.models import Risk, Process, RiskCategory
from controls.models import Control
import uuid
import json


@staff_member_required
def ai_assistant_view(request):
    return render(request, 'knowledge/assistant.html')

@staff_member_required
def ai_query_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        query = data.get('query', '')
        
        if not query:
            return JsonResponse({'error': 'No query provided'}, status=400)
            
        # 1. Ask Assistant (Full RAG via Orchestrator)
        try:
            print(f"DEBUG: Processing query: {query}")
            orchestrator = RiskAnalystOrchestrator()
            
            # We can implement session handling later, for now prompt per turn
            session_id = f"user_{request.user.id}_session"
            
            answer = orchestrator.process_turn(query, session_id)
            print(f"DEBUG: Answer generated successfully")
                
            return JsonResponse({
                'response': answer
            })
        except Exception as e:
            print(f"DEBUG ERROR: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)
        
@staff_member_required
def risk_interview_wizard(request):
    return render(request, 'knowledge/risk_wizard.html')

@staff_member_required
def analyze_interview_api(request):
    """Backward compatible endpoint."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            transcript = data.get('transcript', '')
            
            if not transcript:
                return JsonResponse({'error': 'No content provided'}, status=400)
                
            advisor = RiskAdvisor()
            risks = advisor.analyze_interview_for_risks(transcript)
            
            # For each risk, we could also suggest mitigations immediately
            for risk in risks:
                if isinstance(risk, dict) and 'description' in risk and 'category' in risk:
                    risk['suggested_controls'] = advisor.suggest_mitigations(risk['description'], risk['category'])
                
            return JsonResponse({
                'risks': risks
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Invalid method'}, status=405)

@staff_member_required
def pre_analyze_interview_api(request):
    """MOMENTO A: PRE-ANÁLISIS GUIADO."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            transcript = data.get('transcript', '')
            context = data.get('context', {})
            
            orchestrator = InterviewIntelligenceOrchestrator()
            result = orchestrator.run_pre_analysis(transcript, context)
            
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)

@staff_member_required
def final_analyze_interview_api(request):
    """MOMENTO B: ANÁLISIS FINAL. Supports combined context (PR3)."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            transcript = data.get('transcript', '')
            context = data.get('context', {})
            session_ids = data.get('session_ids', []) # PR3
            
            if not transcript:
                return JsonResponse({'error': 'No content provided'}, status=400)
            
            # Combine transcripts if session_ids provided (PR3)
            combined_transcript = transcript
            if session_ids:
                past_sessions = InterviewSession.objects.filter(id__in=session_ids).order_by('date')
                for ps in past_sessions:
                    combined_transcript = f"--- Entrevista previa ({ps.date}): ---\n{ps.transcript}\n\n" + combined_transcript

            orchestrator = InterviewIntelligenceOrchestrator()
            result = orchestrator.run_final_analysis(combined_transcript, context)
            
            return JsonResponse(result)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)

@staff_member_required
def list_previous_interviews_api(request):
    """Lists past interviews for a given process and/or risk."""
    process_id = request.GET.get('process_id')
    risk_id = request.GET.get('risk_id')
    
    query = InterviewSession.objects.all()
    if risk_id:
        query = query.filter(identified_risk_id=risk_id)
    elif process_id:
        query = query.filter(process_id=process_id)
    else:
        return JsonResponse([], safe=False)
        
    interviews = query.filter(is_deleted=False).order_by('-date').values('id', 'title', 'date', 'interviewee')
    return JsonResponse(list(interviews), safe=False)

@staff_member_required
def get_wizard_data_api(request):
    """Returns processes and existing risks for the wizard dropdowns."""
    processes = list(Process.objects.values('id', 'name'))
    risks = list(Risk.objects.values('id', 'title', 'process_id'))
    return JsonResponse({
        'processes': processes,
        'risks': risks
    })

@staff_member_required
def save_interview_session_api(request):
    """
    Saves the full interview session details (Momento A + Momento B + Metadata).
    POST /api/interviews/save
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Check if session exists to update, or create new
            session_id = data.get('session_id')
            session_uuid = data.get('session_uuid')
            session = None
            
            if session_uuid:
                try:
                    session = InterviewSession.objects.get(session_uuid=session_uuid)
                except InterviewSession.DoesNotExist:
                    pass
            elif session_id:
                try:
                    session = InterviewSession.objects.get(id=session_id)
                except InterviewSession.DoesNotExist:
                    pass
            
            # Extract basic fields
            transcript = data.get('transcript', '') or data.get('raw_text', '')
            momento_a = data.get('momento_a', {})
            momento_b = data.get('momento_b', {})
            
            # Process & Risk links
            process_id = data.get('process_id')
            risk_id = data.get('risk_id')
            
            defaults = {
                'title': data.get('title', f"Entrevista {data.get('date', '')}"),
                'date': data.get('date') or '2025-01-01',
                'interviewer': data.get('owner_name') or data.get('interviewer', 'Desconocido'),
                'interviewee': data.get('analyst_name') or data.get('interviewee', 'Desconocido'),
                'transcript': transcript,
                'is_transcribed': True,
                'momento_a_json': momento_a,
                'momento_b_json': momento_b,
                'status': 'DRAFT'
            }
            
            if session_uuid and not session:
                defaults['session_uuid'] = session_uuid

            if process_id:
                defaults['process_id'] = process_id
            if risk_id:
                defaults['identified_risk_id'] = risk_id

            if session:
                for key, value in defaults.items():
                    setattr(session, key, value)
                session.save()
            else:
                session = InterviewSession.objects.create(**defaults)
            
            # Save combined sessions link (PR3)
            session_ids = data.get('combined_session_ids', [])
            if session_ids:
                session.combined_sessions.set(session_ids)
                
            return JsonResponse({
                'status': 'success', 
                'session_id': session.id,
                'session_uuid': str(session.session_uuid)
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)


@staff_member_required
def apply_finding_api(request):
    """
    Applies a specific finding to create/update a Risk and its Controls.
    POST /api/interviews/apply_finding
    payload: {session_id, finding_idx, risk_id?, apply_controls: true/false}
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            finding_idx = data.get('finding_idx')
            force_update = data.get('force', False) # Safety flag
            
            if not session_id:
                 return JsonResponse({'error': 'Session ID required'}, status=400)

            session = InterviewSession.objects.get(id=session_id)
            
            # Retrieve Finding Data from JSON
            momento_b = session.momento_b_json
            hallazgos = momento_b.get('hallazgos', [])
            
            if finding_idx is None or not (0 <= finding_idx < len(hallazgos)):
                return JsonResponse({'error': 'Invalid finding index'}, status=400)
                
            finding_data = hallazgos[finding_idx]
            
            # 1. Create/Update Risk
            risk_id = data.get('risk_id') or session.identified_risk_id
            risk_obj = None
            
            # Risk Owner Logic (PR-D)
            from risk_universe.models import RiskOwner
            owner_name = session.interviewee
            risk_owner = None
            if owner_name:
                risk_owner, _ = RiskOwner.objects.get_or_create(
                    name=owner_name,
                    defaults={'is_active': True}
                )
            
            # Fields to map
            f_title = finding_data.get('riesgo_titulo', 'Sin Título')
            f_desc = finding_data.get('riesgo_descripcion', '') # Plain text expected
            f_factor = finding_data.get('factor_riesgo', '')
            f_specific = finding_data.get('factor_riesgo_especifico', '')
            f_confianza = finding_data.get('confianza', 0.0)
            
            if risk_id:
                try:
                    risk_obj = Risk.objects.get(id=risk_id)
                    # Safety Rule: Only update if empty OR forced
                    if force_update or not risk_obj.title:
                        risk_obj.title = f_title
                    if force_update or not risk_obj.description:
                        risk_obj.description = f_desc
                    
                    # Always update factors if they are essentially "tags"
                    if hasattr(risk_obj, 'factor_riesgo'):
                        risk_obj.factor_riesgo = f_factor
                    if hasattr(risk_obj, 'factor_riesgo_especifico'):
                        risk_obj.factor_riesgo_especifico = f_specific
                    
                    if risk_owner and not risk_obj.risk_owner:
                        risk_obj.risk_owner = risk_owner

                    risk_obj.ai_context = f"Confianza AI: {f_confianza}"
                    risk_obj.save()
                    
                except Risk.DoesNotExist:
                    pass
            
            if not risk_obj:
                # Create New
                cat, _ = RiskCategory.objects.get_or_create(name='Ejecución, Entrega y Gestión de Procesos')
                risk_obj = Risk.objects.create(
                    process=session.process,
                    category=cat,
                    title=f_title,
                    description=f_desc,
                    factor_riesgo=f_factor,
                    factor_riesgo_especifico=f_specific,
                    risk_owner=risk_owner,
                    ai_context=f"Confianza AI: {f_confianza}",
                    status='identified'
                )
            
            # Link Risk to Session
            session.identified_risk = risk_obj
            session.save()
            
            # 2. Persist Finding Record (Audit)
            InterviewFinding.objects.create(
                session=session,
                idx=finding_idx,
                confianza=f_confianza,
                title=f_title,
                description=f_desc,
                risk_factor=f_factor,
                specific_risk_factor=f_specific,
                suggested_controls=finding_data.get('controles_sugeridos', []),
                evidence_rag=session.momento_b_json.get('evidencia_rag', []), # Link all evidence for context? or filter?
                selected=True,
                is_accepted=True,
                created_risk=risk_obj
            )
            
            # 3. Handle Controls via Recommendations
            if data.get('apply_controls', True):
                from configurations.models import ControlRecommendation
                controls_list = finding_data.get('controles_sugeridos', [])
                for c in controls_list:
                    c_name = c.get('control', '').strip()
                    if not c_name: continue
                    
                    ctrl = Control.objects.filter(name__iexact=c_name).first()
                    if not ctrl:
                        import uuid
                        ctrl = Control.objects.create(
                            code=f"CTRL-{uuid.uuid4().hex[:6].upper()}",
                            name=c_name,
                            description=f"Sustento: {c.get('sustento', '')}",
                            oportunidad_control=Control.OPP_PREVENTIVO
                        )
                    
                    # Instead of auto-adding to M2M, create RECOMMENDATION
                    # Wait, user said "Aceptar y Registrar" in Wizard. 
                    # Usually "Accept" in Wizard implies applying the whole finding.
                    # BUT user says: "El endpoint / lógica de 'suggest' no debe mutar el Risk."
                    # I will create RECOMMENDATIONS first, and if Wizard wants to auto-apply, it calls apply.
                    # To be safe and fulfill "No auto-aplicar", I'll create RECOs in RECOMMENDED status.
                    ControlRecommendation.objects.update_or_create(
                        risk=risk_obj,
                        control=ctrl,
                        defaults={'status': 'recommended'}
                    )
                    
                    # If user specifically wants to APPLY them now (from Wizard)
                    # I'll check a flag or just do it because Wizard "Accept" means "I want this risk identified with these things"
                    # Actually, let's follow the user's rule strictly: only "apply" (aceptar) muta.
                    # The Wizard "Aceptar" button is a macro-apply.
                    risk_obj.controls.add(ctrl)
                    if not risk_obj.control_principal:
                        risk_obj.control_principal = ctrl
                        risk_obj.save()

            return JsonResponse({
                'ok': True,
                'risk_id': risk_obj.id,
                'redirect_url': f"/admin/risk_universe/risk/{risk_obj.id}/change/"
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)


@staff_member_required
def calculate_control_effectiveness_api(request):
    """
    Calculates Control Effectiveness based on strict formulas.
    POST /api/controles/calcular
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            op = data.get('oportunidad_control', '')
            alc = data.get('alcance_control', '')
            seg = data.get('hay_segregacion_funciones', '')
            tipo = data.get('tipo_control', '')
            form = data.get('formalizacion_control', '')
            
            # Scores (Hardcoded for strict compliance vs relying on Model defaults)
            # Oportunidad (35%)
            s_op = 0.0
            if op == 'PREVENTIVO': s_op = 0.35
            elif op == 'DETECTIVO': s_op = 0.20
            elif op == 'SIN CONTROL' or op == 'SIN_CONTROL': s_op = 0.00
            
            # Alcance (20%)
            s_alc = 0.0
            if alc == 'TOTAL' or 'TOTAL' in alc: s_alc = 0.20
            elif alc == 'PARCIAL' or 'PARCIAL' in alc: s_alc = 0.05
            
            # Segregacion (15%)
            s_seg = 0.0
            if seg == 'SI': s_seg = 0.15
            
            # Tipo (20%)
            s_tipo = 0.0
            if 'AUTOMATICO' in tipo and 'SEMI' not in tipo: s_tipo = 0.20
            elif 'SEMIAUTOMATICO' in tipo: s_tipo = 0.15
            elif 'MANUAL' in tipo: s_tipo = 0.05
            
            # Formalizacion (10%)
            s_form = 0.0
            if form == 'FORMALIZADO': s_form = 0.10
            elif form == 'NO FORMALIZADO': s_form = 0.05
            # DESCONOCIDO/Empty -> 0.0
            
            # Strict Rule: SIN CONTROL = 0
            if op == 'SIN CONTROL' or op == 'SIN_CONTROL':
                total_score = 0.0
            else:
                total_score = s_op + s_alc + s_seg + s_tipo + s_form
            
            # Classification
            entorno = "5 OPTIMO"
            if total_score <= 0.40: entorno = "1 DEFICIENTE"
            elif total_score <= 0.60: entorno = "2 REGULAR"
            elif total_score <= 0.80: entorno = "3 SUFICIENTE"
            elif total_score <= 0.95: entorno = "4 BUENO"
            
            return JsonResponse({
                'efectividad_control': round(total_score, 2),
                'efectividad_control_pct': f"{int(total_score * 100)}%",
                'entorno_control': entorno,
                'detalle': {
                    'puntaje_oportunidad_control': s_op,
                    'puntaje_alcance_control': s_alc,
                    'puntaje_hay_segregacion_funciones': s_seg,
                    'puntaje_tipo_control': s_tipo,
                    'puntaje_formalizacion_control': s_form,
                    'suma': total_score
                }
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
            
    return JsonResponse({'error': 'Invalid method'}, status=405)
