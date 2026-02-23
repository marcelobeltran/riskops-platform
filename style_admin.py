import re
import os

filepath = r"c:\Users\Marcelo Beltran\Documents\IDEA\GIT\AuditorOperacional\riskops-platform-1\risk_universe\admin.py"

if not os.path.exists(filepath):
    print(f"Error: {filepath} no existe.")
    exit(1)

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

new_method = """    def controls_table_panel(self, obj):
        from django.utils.safestring import mark_safe
        from .models import RiskControlLink
        
        if not obj.pk:
            return mark_safe('<div style="padding:10px; color:#666;">[Guarde el riesgo para vincular controles]</div>')

        links = obj.control_links.all().select_related('control')
        
        # CSS para estandarizar el estilo al de "Riesgos vinculados"
        html = '''
        <style>
            #riskcontrollink_set-group, #control_links-group, .field-controls_table_panel > label { display: none !important; }
            .field-controls_table_panel { padding: 0 !important; border: none !important; }
            .field-controls_table_panel .readonly { padding: 0 !important; width: 100% !important; }
            
            .custom-ctrl-container { margin-top: 10px; border: 1px solid #ddd; border-top: none; }
            
            /* Cabecera Tipo Título de Sección */
            .custom-ctrl-header { 
                background: #103e50; color: white; padding: 10px 15px; 
                display: flex; align-items: center; gap: 10px;
                font-size: 13px; font-weight: bold; border-radius: 4px 4px 0 0;
            }
            
            .custom-ctrl-table { width: 100%; border-collapse: collapse; background: white; }
            
            /* Encabezados de Columna (Gris claro, All Caps) */
            .custom-ctrl-table thead th { 
                background: #f8f8f8; color: #666; padding: 8px 12px; 
                text-align: left; font-size: 11px; font-weight: bold;
                text-transform: uppercase; border-bottom: 1px solid #eee;
            }
            
            .custom-ctrl-table td { padding: 12px; border-bottom: 1px solid #eee; font-size: 13px; vertical-align: middle; }
            
            /* Iconos de Acción Estandarizados */
            .btn-action-std { text-decoration: none !important; font-size: 18px; margin: 0 10px; cursor: pointer; display: inline-block; transition: transform 0.1s; }
            .btn-action-std:hover { transform: scale(1.1); }
            .btn-edit-std { color: #f39c12 !important; } /* Naranja */
            .btn-delete-std { color: #e74c3c !important; } /* Rosado/Coral */
            
            /* Links Inferiores */
            .ctrl-bottom-links { display: flex; gap: 30px; padding: 10px 15px; background: #fff; }
            .ctrl-link-btn { 
                text-decoration: none !important; color: #103e50 !important; 
                font-size: 13px; display: inline-flex; align-items: center; gap: 6px; 
                cursor: pointer; font-weight: 500;
            }
            .ctrl-plus { color: #28a745; font-weight: bold; font-size: 18px; }
        </style>
        
        <div class="custom-ctrl-container">
            <div class="custom-ctrl-header">
                <span>🛡️ CONTROLES VINCULADOS</span>
            </div>
            <table class="custom-ctrl-table">
                <thead>
                    <tr>
                        <th style="width: 120px;">ID</th>
                        <th>NOMBRE DEL CONTROL</th>
                        <th style="width: 100px; text-align: center;">EFEC.</th>
                        <th style="width: 150px; text-align: center;">ACCIONES</th>
                    </tr>
                </thead>
                <tbody>
        '''
        
        if not links:
            html += '<tr><td colspan="4" style="text-align:center; color:#999; padding:30px; background:#fafafa;">No hay controles vinculados a este riesgo.</td></tr>'
        else:
            for link in links:
                ctrl = link.control
                edit_url = f"/admin/controls/control/{ctrl.id}/change/?_popup=1"
                delete_url = f"/admin/risk_universe/riskcontrollink/{link.id}/delete/?_popup=1"
                
                efec_display = "-"
                if hasattr(ctrl, 'get_efectividad_display'):
                    efec_display = ctrl.get_efectividad_display()
                elif hasattr(ctrl, 'efectividad'):
                    efec_display = ctrl.efectividad
                
                html += f'''
                    <tr id="row-link-{link.id}">
                        <td style="color:#666;">{ctrl.code}</td>
                        <td style="font-weight: 500;">{ctrl.name}</td>
                        <td style="text-align: center;">{efec_display}</td>
                        <td style="text-align: center;">
                            <a href="{edit_url}" class="btn-action-std btn-edit-std" title="Modificar" onclick="return showAddAnotherPopup(this);">✏️</a>
                            <a href="{delete_url}" class="btn-action-std btn-delete-std" title="Desvincular" onclick="return showAddAnotherPopup(this);">❌</a>
                        </td>
                    </tr>
                '''
        
        html += f'''
                </tbody>
            </table>
            <div class="ctrl-bottom-links">
                <a href="/admin/controls/control/add/?_popup=1" class="ctrl-link-btn" onclick="return showAddAnotherPopup(this);">
                    <span class="ctrl-plus">+</span> Agregar Nuevo Control
                </a>
                <a href="/admin/risk_universe/riskcontrollink/add/?risk={obj.id}&_popup=1" class="ctrl-link-btn" onclick="return showAddAnotherPopup(this);">
                    <span class="ctrl-plus">+</span> Vincular Control existente
                </a>
            </div>
        </div>
        
        <script>
            (function() {
                const wrapRefresh = (fnName) => {
                    const original = window[fnName];
                    window[fnName] = function(...args) {
                        if (original) original.apply(this, args);
                        location.reload(); 
                    };
                };
                wrapRefresh('dismissAddAnotherPopup');
                wrapRefresh('dismissRelatedLookupPopup');
                wrapRefresh('dismissChangeRelatedObjectPopup');
                wrapRefresh('dismissDeleteRelatedObjectPopup');
            })();
        </script>
        '''
        return mark_safe(html)
    controls_table_panel.short_description = ""
"""

# Surgical replacement
pattern = r"    def controls_table_panel\(self, obj\):.*?controls_table_panel\.short_description = \"\"\"?"
new_content = re.sub(pattern, new_method.strip('\n'), content, flags=re.DOTALL)

if new_content == content:
    print("Error: No se encontró el método para reemplazar.")
else:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Éxito: admin.py actualizado con el nuevo estilo standard.")
