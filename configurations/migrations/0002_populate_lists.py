from django.db import migrations

def populate_lists(apps, schema_editor):
    ConfigList = apps.get_model('configurations', 'ConfigList')
    ConfigListItem = apps.get_model('configurations', 'ConfigListItem')

    lists_data = {
        'basilea_loss_type': {
            'name': 'Tipos de Pérdida Basilea',
            'items': [
                ('fraude_interno', 'Fraude Interno'),
                ('fraude_externo', 'Fraude Externo'),
                ('practicas_laborales', 'Prácticas laborales y seguridad en el puesto de trabajo'),
                ('clientes_productos', 'Clientes, Productos y prácticas de negocio'),
                ('danos_activos', 'Daños en a los activos físicos'),
                ('interrupcion_negocio', 'Interrupción del negocio y fallos de sistema'),
                ('ejecucion_procesos', 'Ejecución, entrega y gestión de procesos'),
            ]
        },
        'loss_risk_type': {
            'name': 'Riesgos de Pérdida',
            'items': [
                ('apropiacion_activos', 'Apropiación indebida de activos'),
                ('multas_sanciones', 'Multas y/o sanciones'),
                ('indemnizaciones_trabajadores', 'Indemnizaciones pagadas a los Trabajadores'),
                ('danos_activos_fisicos', 'Daños a los activos físicos'),
                ('negocios_no_realizados', 'Negocios no realizados'),
                ('costos_adicionales', 'Costos adicionales del proceso'),
                ('pagos_exceso', 'Pagos en exceso'),
                ('cobros_deficit', 'Cobros con déficit'),
                ('costos_financieros', 'Costos Financieros'),
                ('fuga_clientes', 'Fuga de clientes'),
                ('indemnizaciones_clientes', 'Indemnizaciones pagadas a clientes o terceros'),
                ('incobrables', 'Otros incobrables'),
            ]
        },
        'risk_factor': {
            'name': 'Factor de Riesgo',
            'items': [
                ('personas', 'Personas'),
                ('procesos', 'Procesos'),
                ('tecnologia', 'Tecnología'),
                ('eventos_externos', 'Eventos Externos'),
                ('infraestructura', 'Infraestructura'),
            ]
        }
    }

    for tech_name, data in lists_data.items():
        config_list, _ = ConfigList.objects.get_or_create(
            technical_name=tech_name,
            defaults={'name': data['name']}
        )
        for i, (item_tech_name, item_label) in enumerate(data['items']):
            ConfigListItem.objects.get_or_create(
                config_list=config_list,
                technical_name=item_tech_name,
                defaults={
                    'label': item_label,
                    'order': i * 10,
                    'is_active': True
                }
            )

def reverse_populate_lists(apps, schema_editor):
    ConfigList = apps.get_model('configurations', 'ConfigList')
    ConfigList.objects.filter(technical_name__in=['basilea_loss_type', 'loss_risk_type', 'risk_factor']).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('configurations', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_lists, reverse_populate_lists),
    ]
