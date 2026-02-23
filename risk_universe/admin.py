from django.contrib import admin
from django import forms
from simple_history.admin import SimpleHistoryAdmin
from .models import Process, RiskCategory, Risk, RiskControlLink, RiskOwner
from controls.models import Control
from monitoring.models import Incident, LossEvent
from core.admin_utils import StandardAdminMixin, StandardStatusFilter

class IncidentInline(admin.TabularInline):
    model = Incident
    extra = 0
    readonly_fields = ('date_occurrence', 'description', 'detected_by')
    can_delete = False

class LossEventInline(admin.TabularInline):
    model = LossEvent
    extra = 0
    readonly_fields = ('date_occurrence', 'description', 'gross_loss', 'net_loss')
    can_delete = False

class RiskInline(admin.TabularInline):
    model = Risk
    extra = 0

    # Mantén las columnas que quieres ver en la tabla
    fields = ('code', 'title', 'inherent_display', 'residual_display', 'status')

    # 👇 Esto es lo clave: nada editable en la tabla
    readonly_fields = ('code', 'title', 'inherent_display', 'residual_display', 'status')

    can_delete = True
    verbose_name = "riesgo"
    verbose_name_plural = "Riesgos vinculados"
    show_change_link = True  # Mantiene el link interno de Django (lo usamos como lápiz)

    def has_delete_permission(self, request, obj=None):
        return True

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Etiqueta del checkbox de delete (aunque lo esconderemos con JS)
        if 'DELETE' in formset.form.base_fields:
            formset.form.base_fields['DELETE'].label = "Desvincular"
            formset.form.base_fields['DELETE'].help_text = "Quitar de este proceso (no borra el riesgo)"
        return formset


# ProcessForm removed as its logic is now partially in the popup select flow.

# ProcessStatusFilter replaced by StandardStatusFilter

@admin.register(Process)
class ProcessAdmin(StandardAdminMixin, SimpleHistoryAdmin):
    list_display = ('name', 'owner', 'analyst', 'criticality', 'is_active', 'created')
    list_filter = ('criticality', 'owner', 'analyst') # StandardStatusFilter added by mixin
    search_fields = ('name', 'owner', 'analyst', 'description')
    autocomplete_fields = ['owner']
    inlines = [RiskInline, IncidentInline, LossEventInline]
    actions = ['archive', 'reactivate'] # Actions inherited from StandardAdminMixin
    
    readonly_fields = ('created', 'ui_polish_injector')
    fieldsets = (
        ('Datos del Proceso', {
            'fields': ('ui_polish_injector', 'name', 'description', 'owner', 'analyst', 'criticality', 'is_active')
        }),
    )

    def get_queryset(self, request):
        # Return full queryset; the list filters will handle the restrictions
        # ensuring the "counts" are calculated over the full dataset.
        return super().get_queryset(request)

    def delete_model(self, request, obj):
        # Definitive delete as requested in PR1
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        # Definitive delete as requested in PR1
        queryset.delete()
        self.message_user(request, "Los procesos seleccionados han sido eliminados definitivamente.")

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

    def save_formset(self, request, form, formset, change):
        if formset.model == Risk:
            instances = formset.save(commit=False)
            # Handle "deleted" risks by unassigning them instead
            for obj in formset.deleted_objects:
                obj.process = None
                obj.save()
            # Save normal changes
            for instance in instances:
                instance.save()
            formset.save_m2m()
        else:
            formset.save()

    def debug_injector(self, obj):
        from django.utils.safestring import mark_safe
        return mark_safe('<script src="/static/risk_universe/js/risk_calc.js?v=23_FINAL"></script><div style="background:green; color:white; padding:5px;"><b>CALC ACTIVE v23</b></div>')

    def ui_polish_injector(self, obj):
        from django.utils.safestring import mark_safe
        return mark_safe(r"""
<style type="text/css">
/* Header azul */
#risk_set-group h2, .inline-group h2, .module h2 {
  background-color: #103e50 !important;
  color: #fff !important;
  margin: 0 !important;
  padding: 10px !important;
}

/* Tabla ordenada y estable */
#risk_set-group table { 
  width: 100% !important; 
  table-layout: fixed !important; 
  border-collapse: collapse !important;
}

/* DENSIDAD MEDIA (Selectores específicos para ganar a Django) */
#risk_set-group table thead th,
#risk_set-group table tbody td {
  padding-top: 10px !important;
  padding-bottom: 12px !important;
  line-height: 1.35 !important;
  vertical-align: middle !important;
}

/* Altura de fila media */
#risk_set-group table tr.form-row td {
  height: 50px !important;
}

/* Evitar espacios extra dentro de celdas */
#risk_set-group td .readonly,
#risk_set-group td p,
#risk_set-group td div {
  margin: 0 !important;
  padding: 0 !important;
}

/* Ocultar la columna "original" de Django */
.inline-group th.original,
.inline-group td.original,
.inline-group .original {
  display: none !important;
}

/* FIX columna fantasma: Django TabularInline usa <colgroup> */
#risk_set-group table colgroup col.original {
  width: 0 !important;
  visibility: collapse !important;
  display: none !important;
}

#risk_set-group table colgroup col.delete {
  width: 160px !important;
}

/* Asegurar que header y celdas usen los mismos anchos */
.inline-group th.column-code,        .inline-group td.field-code        { width: 110px !important; }
.inline-group th.column-title,       .inline-group td.field-title       { width: 420px !important; }
.inline-group th.column-inherent_display, .inline-group td.field-inherent_display { width: 140px !important; text-align: center !important; }
.inline-group th.column-residual_display, .inline-group td.field-residual_display { width: 140px !important; text-align: center !important; }
.inline-group th.column-status,      .inline-group td.field-status      { width: 160px !important; text-align: center !important; }

/* COLUMNA ACCIONES: que sea la última y SIN espacio fantasma */
.inline-group th.column-DELETE,
.inline-group td.delete {
  width: 160px !important;
  text-align: center !important;
  padding-right: 0 !important;
}

/* Texto normal (no uppercase forzado) */
.column-inherent_display, .column-residual_display, .column-status {
  text-transform: none !important;
  font-weight: normal;
}

/* Íconos acciones */
.action-icon {
  cursor: pointer;
  font-size: 18px;
  text-decoration: none !important;
  margin: 0 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* Quitar fondo/espacio gris del área inferior de add-row */
.inline-group .add-row {
  background: transparent !important;
  border: 0 !important;
  padding: 8px 0 0 0 !important;
  margin: 0 !important;
}

/* Por si el gris viene del fieldset tabular */
.inline-group fieldset {
  background: transparent !important;
}

/* Si aparece una línea/borde inferior extra */
.inline-group .add-row td,
.inline-group .add-row th {
  background: transparent !important;
}

/* Links inferiores en una sola línea (v17) */
#gest-links-wrap { 
  display: flex !important;
  gap: 40px !important;
  flex-wrap: nowrap !important;
  align-items: center !important;
  margin: 6px 0 0 0 !important;
  padding-left: 4px !important;
}

.gest-link-btn {
  text-decoration: none !important;
  color: #103e50 !important;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  white-space: nowrap !important;
}
.gest-plus { color: #28a745; font-weight: 700; font-size: 18px; }

/* Modales */
.gest-modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.6);
  z-index: 100001;
  display: flex; align-items: center; justify-content: center;
}
.gest-modal {
  background: #fff;
  padding: 22px;
  border-radius: 8px;
  width: 520px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
  font-family: sans-serif;
  border-top: 5px solid #103e50;
}
.gest-modal h3 { margin: 0 0 12px 0; color: #103e50; font-size: 1.25em; }
.gest-input {
  width: 100%;
  padding: 12px;
  margin: 10px 0 12px 0;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
  font-size: 14px;
}
.gest-btn-group { display: flex; justify-content: flex-end; gap: 10px; }
.gest-btn { padding: 10px 18px; border-radius: 4px; border: none; cursor: pointer; font-weight: 600; font-size: 14px; }
.gest-btn-cancel { background: #f4f4f4; color: #333; }
.gest-btn-ok { background: #103e50; color: #fff; }
.gest-error { color: #A4262C; font-size: 13px; margin: 8px 0; display: none; }

/* Lista huérfanos */
.gest-list { max-height: 260px; overflow-y: auto; border: 1px solid #eee; border-radius: 4px; margin: 10px 0 14px 0; }
.gest-list-item { padding: 10px; border-bottom: 1px solid #f2f2f2; display: flex; gap: 10px; align-items: center; cursor: pointer; }
.gest-list-item:hover { background: #f0f7fa; }
</style>

<script>
(function() {
  const TAG = "[RiskUI v17.2]";

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function getProcessIdFromUrl() {
    const parts = window.location.pathname.split('/').filter(Boolean);
    const idx = parts.indexOf('change');
    if (idx > 0) return parts[idx - 1];
    return parts[3] || null;
  }

  function findRiskInlineGroup() {
    const byId = document.querySelector('#risk_set-group');
    if (byId) return byId;

    const groups = document.querySelectorAll('.inline-group');
    for (const g of groups) {
      const h2 = g.querySelector('h2');
      if (h2 && h2.textContent.toLowerCase().includes('riesgos vinculados')) return g;
    }
    return document.querySelector('.inline-group');
  }

  function renameHeaders(inlineGroup) {
    // Renombrar por clase (estable y sin efectos colaterales)
    const thCode = inlineGroup.querySelector('th.column-code');
    if (thCode) thCode.textContent = "RIESGO ID";

    const thTitle = inlineGroup.querySelector('th.column-title');
    if (thTitle) thTitle.textContent = "NOMBRE RIESGO";

    const thInh = inlineGroup.querySelector('th.column-inherent_display');
    if (thInh) thInh.textContent = "inherent display";

    const thRes = inlineGroup.querySelector('th.column-residual_display');
    if (thRes) thRes.textContent = "residual display";

    const thStatus = inlineGroup.querySelector('th.column-status');
    if (thStatus) thStatus.textContent = "ESTADO";

    const thDel = inlineGroup.querySelector('th.column-DELETE');
    if (thDel) thDel.textContent = "MODIFICAR/ELIMINAR";
  }

  function forceDeleteHeaderByIndex(inlineGroup) {
    const headerRow = inlineGroup.querySelector('thead tr');
    const sampleRow = inlineGroup.querySelector('tbody tr.form-row');
    if (!headerRow || !sampleRow) return;

    const rowCells = Array.from(sampleRow.children);
    const delIdx = rowCells.findIndex(el => el.classList && el.classList.contains('delete'));
    if (delIdx < 0) return;

    const headCells = Array.from(headerRow.children);
    if (headCells[delIdx]) {
      headCells[delIdx].textContent = "MODIFICAR/ELIMINAR";
    }
  }

  function applyRowActions(inlineGroup) {
    inlineGroup.querySelectorAll('tbody tr.form-row').forEach(row => {
      if (row.dataset.riskuied === "1") return;

      // Celda de acciones (delete)
      const delCell = row.querySelector('td.delete');
      if (!delCell) return;

      const editLink = row.querySelector('.inlinechangelink');
      if (!editLink) return;

      row.dataset.riskuied = "1";

      // Ocultar checkbox si existe y forzar que NUNCA se use
      const cb = delCell.querySelector('input[type="checkbox"]');
      if (cb) {
        cb.style.display = 'none';
        cb.checked = false; // Asegurar que no esté marcado
      }

      // Limpiar celda y centrar
      delCell.textContent = '';
      delCell.style.width = '160px';
      delCell.style.textAlign = 'center';

      // Lápiz
      editLink.textContent = '✏️';
      editLink.className = 'action-icon';
      editLink.title = 'Modificar';

      // X
      const unlinkBtn = document.createElement('a');
      unlinkBtn.href = "#";
      unlinkBtn.textContent = '❌';
      unlinkBtn.className = 'action-icon';
      unlinkBtn.title = 'Desvincular';

      unlinkBtn.onclick = async (e) => {
        e.preventDefault();
        if (!confirm("¿Quitar este riesgo del proceso? Quedará como huérfano.")) return;

        // 1) Obtener el ID interno del risk desde el formset (name="risk_set-0-id")
        const hiddenIdInput = row.querySelector('input[name$="-id"]');
        let riskId = hiddenIdInput ? hiddenIdInput.value : null;

        // 2) Fallback: buscar cualquier input oculto que parezca un ID si el anterior falla
        if (!riskId) {
           const anyHidden = row.querySelector('input[type="hidden"]');
           if (anyHidden && anyHidden.value && !isNaN(anyHidden.value)) riskId = anyHidden.value;
        }

        if (!riskId) {
          console.error(TAG + " No se pudo encontrar el ID del riesgo en la fila:", row);
          alert("Error: No se pudo identificar el ID del riesgo. Revisa la consola.");
          return;
        }

        // 3) Llamada API: desvincular (enviando process_id: null)
        try {
          unlinkBtn.style.pointerEvents = 'none';
          unlinkBtn.style.opacity = '0.5';

          console.log(TAG + " Intentando desvincular riesgo ID:", riskId);

          const resp = await fetch('/risks/api/link-risks/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ process_id: null, risk_ids: [riskId] })
          });

          const data = await resp.json().catch(() => ({}));

          if (!resp.ok) {
            throw new Error(data.message || `HTTP ${resp.status}`);
          }

          console.log(TAG + " Desvinculación exitosa:", data);
          
          // Efecto visual y recarga
          row.style.transition = 'opacity 0.3s';
          row.style.opacity = '0';
          setTimeout(() => location.reload(), 300);

        } catch (err) {
          console.error(TAG + " Error en desvinculación:", err);
          alert("Error al desvincular: " + err.message + "\nRevisa la consola (F12) para más detalles.");
        } finally {
          unlinkBtn.style.pointerEvents = '';
          unlinkBtn.style.opacity = '';
        }
      };

      const wrap = document.createElement('div');
      wrap.style.display = 'inline-flex';
      wrap.style.alignItems = 'center';
      wrap.style.justifyContent = 'center';

      wrap.appendChild(editLink);
      wrap.appendChild(unlinkBtn);
      delCell.appendChild(wrap);
    });
  }

  function injectBottomLinks(inlineGroup) {
    const addRow = inlineGroup.querySelector('.add-row');
    if (!addRow) return;

    // Reemplaza el link nativo (“Agregar ... adicional”) por los tuyos
    if (addRow.dataset.riskuilinks === "1") return;
    addRow.dataset.riskuilinks = "1";
    addRow.innerHTML = '';

    const wrap = document.createElement('div');
    wrap.id = 'gest-links-wrap';

    const addNew = document.createElement('a');
    addNew.className = 'gest-link-btn';
    addNew.setAttribute('data-testid', 'link-agregar-nuevo-riesgo');
    addNew.innerHTML = '<span class="gest-plus">+</span> Agregar Nuevo riesgo';
    addNew.onclick = (e) => { e.preventDefault(); showNewModal(); };

    const addEx = document.createElement('a');
    addEx.className = 'gest-link-btn';
    addEx.setAttribute('data-testid', 'link-agregar-riesgo-existente');
    addEx.innerHTML = '<span class="gest-plus">+</span> Agregar Riesgo existente';
    addEx.onclick = (e) => { e.preventDefault(); showExistingModal(); };

    wrap.appendChild(addNew);
    wrap.appendChild(addEx);
    addRow.appendChild(wrap);
  }

  function showNewModal() {
    if (document.getElementById('gest-new-modal')) return;

    const overlay = document.createElement('div');
    overlay.className = 'gest-modal-overlay';
    overlay.id = 'gest-new-modal';

    overlay.innerHTML = `
      <div class="gest-modal" data-testid="modal-nuevo-riesgo">
        <h3>Agregar nuevo riesgo</h3>
        <div id="gest-new-err" class="gest-error"></div>

        <label style="font-size:13px; color:#666;">Nombre del riesgo</label>
        <input type="text" id="gest-new-name" class="gest-input" placeholder="Ej: Riesgo de liquidez...">

        <div class="gest-btn-group">
          <button class="gest-btn gest-btn-cancel" id="gest-new-cancel">Cancelar</button>
          <button class="gest-btn gest-btn-ok" id="gest-new-submit">Crear y agregar</button>
        </div>
      </div>
    `;
    document.body.appendChild(overlay);

    document.getElementById('gest-new-cancel').onclick = () => overlay.remove();

    const input = document.getElementById('gest-new-name');
    input.focus();

    document.getElementById('gest-new-submit').onclick = () => {
      const val = input.value.trim();
      const errDiv = document.getElementById('gest-new-err');
      if (!val) { errDiv.textContent = "El nombre es requerido."; errDiv.style.display = 'block'; return; }

      const btn = document.getElementById('gest-new-submit');
      btn.disabled = true; btn.textContent = 'Procesando...';

      const pid = getProcessIdFromUrl();
      fetch('/risks/api/create-and-link/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify({ process_id: pid, title: val })
      }).then(r => r.json()).then(data => {
        if (data.status === 'success') location.reload();
        errDiv.textContent = "Error: " + (data.message || "Fallo inesperado.");
        errDiv.style.display = 'block';
        btn.disabled = false; btn.textContent = 'Crear y agregar';
      }).catch(() => {
        errDiv.textContent = "Error de conexión.";
        errDiv.style.display = 'block';
        btn.disabled = false; btn.textContent = 'Crear y agregar';
      });
    };
  }

  function showExistingModal() {
    if (document.getElementById('gest-ex-modal')) return;

    const overlay = document.createElement('div');
    overlay.className = 'gest-modal-overlay';
    overlay.id = 'gest-ex-modal';

    overlay.innerHTML = `
      <div class="gest-modal" data-testid="modal-riesgo-existente">
        <h3>Agregar riesgo existente</h3>
        <div id="gest-ex-err" class="gest-error"></div>
        <p style="font-size:13px; color:#666; margin: 0 0 8px 0;">Seleccione un riesgo huérfano:</p>

        <div class="gest-list" id="gest-orphan-list">
          <div style="padding:15px; color:#999; text-align:center;">Cargando riesgos...</div>
        </div>

        <div class="gest-btn-group">
          <button class="gest-btn gest-btn-cancel" id="gest-ex-cancel">Cancelar</button>
          <button class="gest-btn gest-btn-ok" id="gest-ex-submit" disabled>Agregar</button>
        </div>
      </div>
    `;
    document.body.appendChild(overlay);

    document.getElementById('gest-ex-cancel').onclick = () => overlay.remove();

    let selectedId = null;
    const listDiv = document.getElementById('gest-orphan-list');
    const submitBtn = document.getElementById('gest-ex-submit');
    const errDiv = document.getElementById('gest-ex-err');

    fetch('/risks/api/orphans/')
      .then(r => r.json())
      .then(data => {
        if (!Array.isArray(data) || data.length === 0) {
          listDiv.innerHTML = '<div style="padding:18px; text-align:center; color:#666;">No hay riesgos huérfanos disponibles.</div>';
          return;
        }
        listDiv.innerHTML = '';
        data.forEach(risk => {
          const item = document.createElement('div');
          item.className = 'gest-list-item';
          item.innerHTML = `
            <input type="radio" name="orphanRadio" value="${risk.id}">
            <div style="font-size:14px;"><b>${risk.code || '---'}</b> - ${risk.title}</div>
          `;
          item.onclick = () => {
            item.querySelector('input').checked = true;
            selectedId = risk.id;
            submitBtn.disabled = false;
          };
          listDiv.appendChild(item);
        });
      })
      .catch(() => {
        listDiv.innerHTML = '<div style="padding:18px; color:#A4262C; text-align:center;">Error al cargar huérfanos.</div>';
      });

    submitBtn.onclick = () => {
      if (!selectedId) return;
      submitBtn.disabled = true; submitBtn.textContent = 'Vinculando...';

      const pid = getProcessIdFromUrl();
      fetch('/risks/api/link-risks/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify({ process_id: pid, risk_ids: [selectedId] })
      }).then(r => {
        if (r.ok) location.reload();
        throw new Error('link failed');
      }).catch(() => {
        errDiv.textContent = "Error al vincular.";
        errDiv.style.display = 'block';
        submitBtn.disabled = false; submitBtn.textContent = 'Agregar';
      });
    };
  }

  function applyAll() {
    const inlineGroup = findRiskInlineGroup();
    if (!inlineGroup) return;

    const inlineTable = inlineGroup.querySelector('table');
    if (inlineTable) inlineTable.setAttribute('data-testid', 'tabla-riesgos-vinculados');

    renameHeaders(inlineGroup);
    forceDeleteHeaderByIndex(inlineGroup);   // ✅ ESTA LÍNEA NUEVA
    applyRowActions(inlineGroup);
    injectBottomLinks(inlineGroup);
  }

  // Ejecutar varias veces por si Django Admin re-renderiza
  setTimeout(applyAll, 50);
  setTimeout(applyAll, 500);
  setInterval(applyAll, 1200);

  console.log(TAG + " loaded");
})();


</script>
        """)

    ui_polish_injector.short_description = "GestOperIA UI Polish (v16)"
    ui_polish_injector.allow_tags = True

    class Media:
        css = { 'all': ('core/admin/css/risk_recos.css',) }
        js = ('core/admin/js/risk_recommendations.js',)

@admin.register(RiskCategory)
class RiskCategoryAdmin(StandardAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

from import_export.admin import ImportExportModelAdmin

# Duplicate ControlInline removed

from django.contrib.admin.widgets import AutocompleteSelectMultiple

class RiskForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=RiskCategory.objects.all(),
        label="Tipos de Pérdida Basilea",
        required=False
    )

    class Meta:
        model = Risk
        fields = '__all__'
        widgets = {
            'etapas_actividades': forms.Textarea(attrs={'rows': 2, 'style': 'width: 90%;'}),
            'factor_riesgo_especifico': forms.TextInput(attrs={'style': 'width: 90%;'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Standard init, no special m2m logic needed as Inline handles it.
        # We can still filter control_principal if we want, but since Inline 
        # is handled separately, filtering by 'instance.controls.all()' 
        # only works for ALREADY SAVED controls.
        if self.instance.pk:
            # logic removed as control_principal is removed from UI
            pass

    def clean(self):
        cleaned_data = super().clean()
        # Validation of principal vs applied is tricky in backend because 
        # applied controls are in the Inline (formset), not in this form's cleaned_data.
        # We will rely on:
        # 1. Frontend JS to limit choices
        # 2. A "soft" validation or post-save check if needed.
        # For now, let's trust the JS + queryset filtering on init.
        return cleaned_data

class ControlInlineForm(forms.ModelForm):
    # Explicit fields for editing Control attributes logic (if we want to expose them)
    # The user asked for "Lista simple", "Lapiz editar" and "X eliminar".
    # Standard TabularInline gives this.
    # We can expose the extra fields of RiskControlLink if they exist.
    
    class Meta:
        model = RiskControlLink
        fields = '__all__'

class ControlInline(admin.TabularInline):
    model = RiskControlLink
    form = ControlInlineForm
    extra = 1  # Forced extra row to ensure it shows up
    verbose_name = "Control Vinculado"
    verbose_name_plural = "🛡️ EVALUACIÓN DE CONTROLES VINCULADOS"
    
    # Enable Edit (Pencil) and Delete (X)
    show_change_link = True
    can_delete = True
    
    autocomplete_fields = ['control'] # Enable autocomplete for adding new controls
    
    # Columns matching image style (Read-only + Actions)
    fields = [
        'control', # Required for autocomplete_fields
        'control_id', 'control_name', 
        'get_oportunidad_control', 'get_alcance_control', 'get_hay_segregacion_funciones', 
        'get_tipo_control', 'get_formalizacion_control', 
        'get_efectividad_control_pct', 'get_entorno_control'
    ]
    
    readonly_fields = [
        'control_id', 'control_name', 
        'get_oportunidad_control', 'get_alcance_control', 'get_hay_segregacion_funciones', 
        'get_tipo_control', 'get_formalizacion_control', 
        'get_efectividad_control_pct', 'get_entorno_control'
    ]

    def control_id(self, obj):
        if obj.pk and obj.control:
            return obj.control.code
        return "-"
    control_id.short_description = "ID Control"

    def control_name(self, obj):
        if obj.pk and obj.control:
            return obj.control.name
        return "-"
    control_name.short_description = "Nombre Control"

    # Accessors for Control attributes (Read-only proxies)
    def oportunidad_control(self, obj):
        if obj.pk and obj.control:
            return obj.control.get_oportunidad_control_display()
        return "-"
    oportunidad_control.short_description = "Oportunidad"

    def alcance_control(self, obj):
        if obj.pk and obj.control:
            return obj.control.get_alcance_control_display()
        return "-"
    alcance_control.short_description = "Alcance"

    def hay_segregacion_funciones(self, obj):
        if obj.pk and obj.control:
            return obj.control.get_hay_segregacion_funciones_display()
        return "-"
    hay_segregacion_funciones.short_description = "Segregación"

    def tipo_control(self, obj):
        if obj.pk and obj.control:
            return obj.control.get_tipo_control_display()
        return "-"
    tipo_control.short_description = "Tipo"

    def formalizacion_control(self, obj):
        if obj.pk and obj.control:
            return obj.control.get_formalizacion_control_display()
        return "-"
    formalizacion_control.short_description = "Formalización"

    def efectividad_control_pct(self, obj):
        if obj.pk and obj.control:
            return obj.control.efectividad_control_pct
        return "-"
    efectividad_control_pct.short_description = "Efectividad"

    def entorno_control(self, obj):
        if obj.pk and obj.control:
            return obj.control.entorno_control
        return "-"
    entorno_control.short_description = "Entorno"

    # Property wrappers
    def get_oportunidad_control(self, obj):
        return obj.control.oportunidad_control if obj.pk and obj.control else "-"
    get_oportunidad_control.short_description = "Oportunidad"

    def get_alcance_control(self, obj):
        return obj.control.alcance_control if obj.pk and obj.control else "-"
    get_alcance_control.short_description = "Alcance"

    def get_hay_segregacion_funciones(self, obj):
        return obj.control.hay_segregacion_funciones if obj.pk and obj.control else "-"
    get_hay_segregacion_funciones.short_description = "Segregación"

    def get_tipo_control(self, obj):
        return obj.control.tipo_control if obj.pk and obj.control else "-"
    get_tipo_control.short_description = "Tipo"

    def get_formalizacion_control(self, obj):
        return obj.control.formalizacion_control if obj.pk and obj.control else "-"
    get_formalizacion_control.short_description = "Formalización"

    def get_efectividad_control_pct(self, obj):
        return obj.control.efectividad_control_pct if obj.pk and obj.control else "-"
    get_efectividad_control_pct.short_description = "Efectividad"

    def get_entorno_control(self, obj):
        return obj.control.entorno_control if obj.pk and obj.control else "-"
    get_entorno_control.short_description = "Entorno"

# Orphan Filter for Risks
class OrphanFilter(admin.SimpleListFilter):
    title = 'Huérfanos'
    parameter_name = 'is_orphan'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Sí (Sin Proceso)'),
            ('no', 'No (Vinculados)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(process__isnull=True)
        if self.value() == 'no':
            return queryset.filter(process__isnull=False)
        return queryset

@admin.register(RiskOwner)
class RiskOwnerAdmin(ImportExportModelAdmin, SimpleHistoryAdmin, StandardAdminMixin):
    list_display = ('name', 'email', 'area', 'is_active')
    search_fields = ('name', 'email', 'area')
    list_filter = ('area', StandardStatusFilter)

    def has_module_permission(self, request):
        return True
    
    def has_view_permission(self, request, obj=None):
        return True
    
    def has_add_permission(self, request):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True

@admin.register(Risk)
class RiskAdmin(StandardAdminMixin, SimpleHistoryAdmin, ImportExportModelAdmin):
    form = RiskForm
    list_display = ('title', 'is_active', 'created', 'process_display')
    
    def process_display(self, obj):
        from django.utils.safestring import mark_safe
        if not obj.process:
            return mark_safe('<span class="badge-orphan">HUÉRFANO ⚠️</span>')
        return obj.process
    process_display.short_description = "Proceso"
    process_display.admin_order_field = 'process'

    list_filter = (OrphanFilter, 'process') # StandardStatusFilter added by mixin
    search_fields = ('title', 'description', 'code', 'etapas_actividades')
    autocomplete_fields = ['process', 'category', 'basilea_loss_type', 'loss_risk_type', 'risk_factor', 'risk_owner']
    inlines = [ControlInline] # Restored
    
    readonly_fields = (
        'code', 'process', 'inherent_impact_level', 'inherent_risk_name', 
        'residual_impact_level', 'residual_risk_name',
        'requiere_indicador_status', 'requiere_plan_status',
        'controls_table_panel'
    )

    def requiere_indicador_status(self, obj):
        from django.utils.safestring import mark_safe
        if not obj.pk: return "Pendiente de guardado"
        status = "SÍ" if obj.requiere_indicador else "NO"
        color = "#d9534f" if obj.requiere_indicador else "#5cb85c"
        html = f'<div class="status-kri-box"><b style="color:{color};">{status}</b>'
        if obj.requiere_indicador:
            html += f' &nbsp; <a href="/admin/monitoring/kri/add/?risk={obj.id}" class="button btn-kri-add" style="margin-top:0; padding:2px 10px; background:#103e50; font-size:11px;">CREAR KRI</a>'
        html += '</div>'
        return mark_safe(html)
    requiere_indicador_status.short_description = "Requiere indicador"

    def requiere_plan_status(self, obj):
        from django.utils.safestring import mark_safe
        if not obj.pk: return "Pendiente de guardado"
        status = "SÍ" if obj.requiere_plan_accion else "NO"
        color = "#d9534f" if obj.requiere_plan_accion else "#5cb85c"
        html = f'<div class="status-plan-box"><b style="color:{color};">{status}</b>'
        if obj.requiere_plan_accion:
            html += f' &nbsp; <a href="/admin/monitoring/actionplan/add/?risk={obj.id}" class="button btn-plan-add" style="margin-top:0; padding:2px 10px; background:#103e50; font-size:11px;">CREAR PLAN</a>'
        html += '</div>'
        return mark_safe(html)
    requiere_plan_status.short_description = "Requiere plan de acción"

    def controls_table_panel(self, obj):
        from django.utils.safestring import mark_safe
        from .models import RiskControlLink
        
        if not obj.pk:
            return mark_safe('<div style="padding:10px; color:#666;">[Guarde el riesgo para vincular controles]</div>')

        links = obj.control_links.all().select_related('control')
        
        # CSS y JS Nuclear para alineación y eliminación de colon
        html = '''
        <style>
            /* 1. Kill Label and standard Django offsets */
            .field-controls_table_panel > label, 
            .field-controls_table_panel .flex-container > label { 
                display: none !important; 
            }
            
            .field-controls_table_panel { 
                border: none !important; 
                padding: 0 !important; 
                margin: 0 !important; 
            }
            
            .field-controls_table_panel .flex-container {
                padding: 0 !important;
                margin: 0 !important;
                display: block !important;
            }
            
            .field-controls_table_panel .readonly { 
                padding: 0 !important; 
                margin: 0 !important; 
                width: 100% !important; 
                display: block !important;
            }

            /* 2. Kill Colons and pseudo-elements */
            .field-controls_table_panel label::after,
            .field-controls_table_panel .readonly::before,
            .field-controls_table_panel .flex-container::before {
                content: none !important;
                display: none !important;
            }
            
            /* 3. Main Container 100% Width */
            .linked-controls { 
                width: 100% !important; 
                margin: 0 !important; 
                padding: 10px 0 !important;
                text-align: left; 
            }
            
            .linked-controls table {
                width: 100%;
                border-collapse: collapse;
                table-layout: fixed;
                background: white;
                margin: 0 !important;
            }

            .linked-controls thead th {
                color: #6b7280 !important;
                font-weight: 600;
                font-size: 12px;
                padding: 12px 14px;
                border-bottom: 1px solid #e6e6e6;
                text-align: left;
                background: #f8f8f8;
                text-transform: uppercase;
            }

            .linked-controls tbody td {
                color: #6b7280 !important;
                font-size: 14px;
                padding: 12px 14px;
                border-bottom: 1px solid #f0f0f0;
                vertical-align: middle;
            }

            .linked-controls tbody tr:nth-child(even) {
                background: #fafafa;
            }

            .linked-controls th.col-id, .linked-controls td.col-id { width: 160px; }
            .linked-controls th.col-efec, .linked-controls td.col-efec { width: 110px; text-align: center; }
            .linked-controls th.col-actions, .linked-controls td.col-actions { width: 140px; text-align: center; }
            
            .btn-action-std { text-decoration: none !important; font-size: 18px; margin: 0 10px; cursor: pointer; display: inline-block; }
            .btn-edit-std { color: #f39c12 !important; }
            .btn-delete-std { color: #e74c3c !important; }
            
            /* 4. Bottom Links in Grey */
            .ctrl-bottom-links { display: flex; gap: 30px; padding: 15px 0; background: transparent; }
            .ctrl-link-btn { 
                text-decoration: none !important; 
                color: #6b7280 !important; 
                font-size: 13px; 
                display: inline-flex; 
                align-items: center; 
                gap: 6px; 
                cursor: pointer; 
                font-weight: 400;
            }
            .ctrl-plus { color: #6b7280 !important; font-weight: bold; font-size: 18px; }
            .ctrl-link-btn:hover { opacity: 0.7; }
        </style>
        
        <div class="linked-controls">
            <table class="custom-ctrl-table">
                <thead>
                    <tr>
                        <th class="col-id">ID</th>
                        <th class="col-name">NOMBRE DEL CONTROL</th>
                        <th class="col-efec">EFEC.</th>
                        <th class="col-actions">ACCIONES</th>
                    </tr>
                </thead>
                <tbody>
        '''
        
        if not links:
            html += '<tr><td colspan="4" style="text-align:center; color:#999; padding:30px;">No hay controles vinculados a este riesgo.</td></tr>'
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
                        <td class="col-id">{ctrl.code}</td>
                        <td class="col-name" style="font-weight: 500;">{ctrl.name}</td>
                        <td class="col-efec">{efec_display}</td>
                        <td class="col-actions">
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
            (function() {{
                // Nuclear Cleanup for Colon and Alignment
                function nuclearCleanup() {{
                    const field = document.querySelector('.field-controls_table_panel');
                    if (!field) return;
                    
                    // Kill any orphan colon text nodes
                    const nodes = field.childNodes;
                    for (let n of nodes) {{
                        if (n.nodeType === 3 && n.textContent.includes(':')) {{
                            n.textContent = n.textContent.replace(':', '');
                        }}
                    }}
                    
                    // Search in label children if label is still there
                    const labels = field.querySelectorAll('label');
                    labels.forEach(l => {{
                        l.style.setProperty('display', 'none', 'important');
                        if (l.nextSibling && l.nextSibling.nodeType === 3 && l.nextSibling.textContent.includes(':')) {{
                             l.nextSibling.textContent = l.nextSibling.textContent.replace(':', '');
                        }}
                    }});

                    // Reset offsets
                    const ro = field.querySelector('.readonly');
                    if (ro) {{
                        ro.style.setProperty('padding-left', '0', 'important');
                        ro.style.setProperty('margin-left', '0', 'important');
                    }}
                }}
                
                nuclearCleanup();
                setTimeout(nuclearCleanup, 500);
                setTimeout(nuclearCleanup, 1500);

                const wrapRefresh = (fnName) => {{
                    const original = window[fnName];
                    window[fnName] = function(...args) {{
                        if (original) original.apply(this, args);
                        location.reload(); 
                    }};
                }};
                wrapRefresh('dismissAddAnotherPopup');
                wrapRefresh('dismissRelatedLookupPopup');
                wrapRefresh('dismissChangeRelatedObjectPopup');
                wrapRefresh('dismissDeleteRelatedObjectPopup');
            }})();
        </script>
        '''
        return mark_safe(html)
    controls_table_panel.short_description = ""



    fieldsets = (
        ('Identificación del Riesgo', {
            'fields': (
                ('code', 'status'), 
                'title', 
                'basilea_loss_type',
                'loss_risk_type',
                'risk_factor', 
                'factor_riesgo_especifico',
                'etapas_actividades',
                'process', 
                'category',
                ('responsible_analyst', 'risk_owner')
            )
        }),
        ('Evaluación de Impacto y Probabilidad', {
            'description': 'Seleccione las categorías para cada dimensión de impacto.',
            'fields': (
                ('impact_monetary', 'impact_clients'),
                ('impact_reputational', 'impact_regulatory'),
                'impact_processes',
                'inherent_probability'
            )
        }),
        ('Resultados de la Evaluación', {
            'fields': (
                ('inherent_impact_level', 'inherent_risk_name'),
                ('residual_impact_level', 'residual_risk_name'),
                ('requiere_indicador_status', 'requiere_plan_status')
            )
        }),
        ('Gestión de Controles', {
            'fields': ('controls_table_panel',)
        }),
    )

    class Media:
        js = (
            'risk_universe/js/risk_calc_v40_FINAL.js',
            'admin/js/risk_recommendations.js', 
            'controls/js/control_calc.js', 
        )
        css = {
            'all': (
                'admin/css/risk_custom.css', 
                'core/admin/css/risk_recos.css',
            )
        }


    # Removed custom add_view/change_view injecion in favor of standard Media class

    # Removed custom add_view/change_view injecion in favor of standard Media class
    # as user requested "standard inclusion".

    actions = ['delete_selected', 'unassign_from_process']

    def delete_selected(self, request, queryset):
        queryset.delete()
    delete_selected.short_description = "Eliminar riesgos seleccionados"

    def unassign_from_process(self, request, queryset):
        rows_updated = queryset.update(process=None)
        self.message_user(request, f"{rows_updated} riesgos han sido desvinculados de sus procesos.")
    unassign_from_process.short_description = "🔗 Desvincular del proceso"

    def has_delete_permission(self, request, obj=None):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True

    def has_view_permission(self, request, obj=None):
        return True
