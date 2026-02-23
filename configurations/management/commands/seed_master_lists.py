import unicodedata
import re
from django.core.management.base import BaseCommand
from django.db import transaction
from configurations.models import ConfigList, ConfigListItem

class Command(BaseCommand):
    help = 'Seeds master lists (Basilea, Risks, Factors) with exact labels and order.'

    def handle(self, *args, **options):
        data = [
            {
                'tech_name': 'tipos_perdida_basilea',
                'label': 'Tipos de Pérdida Basilea',
                'items': [
                    "Daños A Activos Materiales",
                    "Ejecución Entrega Y Gestión De Procesos",
                    "Fraude Externo",
                    "Fraude Interno",
                    "Incidencias En El Negocio Y Fallas En Los Sistemas",
                    "Relaciones Laborales Y Seguridad En El Puesto De Trabajo",
                    "Clientes, productos y prácticas empresariales"
                ]
            },
            {
                'tech_name': 'riesgos_de_perdida',
                'label': 'Riesgos de Pérdida',
                'items': [
                    "Cobros con déficit",
                    "Costos adicionales del proceso",
                    "Costos financieros",
                    "Daños a los activos físicos",
                    "Fuga de Clientes",
                    "Indemnizaciones pagadas a clientes o Terceros",
                    "Indemnizaciones Pagadas a los trabajadores",
                    "Multas y Sanciones",
                    "Negocios no realizados",
                    "Otros Incobrables",
                    "Pagos en exceso"
                ]
            },
            {
                'tech_name': 'factor_de_riesgo',
                'label': 'Factor de riesgo',
                'items': [
                    "Errores en introducción, mantención o carga de datos",
                    "Falla en minería de datos",
                    "Falla en proteger la información",
                    "Fallas críticas del sistema",
                    "Fallas eléctricas",
                    "Fallas en los procesos del proveedor",
                    "Fallas en los procesos operativos",
                    "Fallas en los servicios públicos",
                    "Falsificación",
                    "Falta de aseguramiento",
                    "Falta de conocimiento del negocio",
                    "Falta de información para detectar, investigar y asignar responsabilidades en caso de eventos de seguridad",
                    "Falta de infraestructura y elementos de apoyo",
                    "Falta de personal capacitado",
                    "Falta de personal clave para la empresa",
                    "Falta de seguridad física en las instalaciones",
                    "Fuga de Datos",
                    "Habilidades inadecuadas",
                    "Huelgas",
                    "Hurtos y Robos",
                    "Imposibilidad de restauración inmediata de servicios básicos",
                    "Incapacidad para manejar la carga",
                    "Incapacidad para reclutar personal de TI",
                    "Incobrabilidad de comisiones",
                    "Incumplimiento con contratos de licencias de software",
                    "Incumplimiento de contrato",
                    "Incumplimiento de plazos o responsabilidades",
                    "Incumplimiento de políticas, normas, leyes o regulaciones",
                    "Indisponibilidad de plataforma o sistemas tecnológicos",
                    "Indisponibilidad de servicios prestados por proveedores",
                    "Indisponibilidad de un edificio o conjunto de edificios",
                    "Indisponibilidad de una aplicación / servicio TI crítico para la ejecución del proceso",
                    "Indisponibilidad del suministro de efectivo",
                    "Indisponibilidad masiva de aplicaciones/ servicios TI / comunicaciones",
                    "Indisponibilidad o destrucción de una Sucursal o Conjunto de Sucursales",
                    "Indisponibilidad parcial o pérdida del personal clave",
                    "Inexactitud de informes externos",
                    "Intrusión de software malicioso",
                    "Lavado de dinero",
                    "Litigios relacionados a prestaciones de servicios de terceros",
                    "Mala administración de parches",
                    "Nivel de Servicio Bajo",
                    "Obsolescencia tecnológica",
                    "Operaciones no Autorizadas",
                    "Operaciones no reveladas",
                    "Pérdida de documentos",
                    "Pérdida de recursos clave de TI",
                    "Pérdidas de confidencialidad de la información sensible (exposición)",
                    "Plan de pruebas deficiente",
                    "Prácticas comerciales o de mercado improcedentes",
                    "Problemas de configuración",
                    "Quiebra de proveedores",
                    "Registro incorrecto de clientes",
                    "Responsabilidades solidarias en incumplimiento de subcontratistas con su personal",
                    "Retrasos importantes",
                    "Revelación de datos sensibles",
                    "Robo (Centro de procesamiento de datos)",
                    "Sanciones ambientales",
                    "Soporte inadecuado",
                    "Suplantación de Identidad",
                    "Terrorismo, vandalismo, etc.",
                    "Transacciones financieras sin fondos",
                    "Uso inadecuado de información confidencial",
                    "Valoración errónea"
                ]
            }
        ]

        def slugify(value):
            value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
            value = re.sub(r'[^\w\s-]', '', value).strip().lower()
            return re.sub(r'[-\s]+', '_', value)

        with transaction.atomic():
            # Delete OLD lists names to avoid confusion (from previous attempts/legacy)
            old_names = ['basilea_loss_type', 'loss_risk_type', 'risk_factor']
            deleted_count, _ = ConfigList.objects.filter(technical_name__in=old_names).delete()
            if deleted_count:
                self.stdout.write(self.style.SUCCESS(f'Eliminadas {deleted_count} listas antiguas redundantes.'))

            for list_info in data:
                clist, created = ConfigList.objects.update_or_create(
                    technical_name=list_info['tech_name'],
                    defaults={'name': list_info['label']}
                )
                if created:
                    self.stdout.write(f"Creada lista: {list_info['label']}")
                else:
                    self.stdout.write(f"Actualizada lista: {list_info['label']}")

                # Update or clean items
                # To maintain order, we delete and recreate or re-order
                ConfigListItem.objects.filter(config_list=clist).delete()

                for idx, item_label in enumerate(list_info['items']):
                    ConfigListItem.objects.create(
                        config_list=clist,
                        technical_name=f"{list_info['tech_name']}_{slugify(item_label)}",
                        label=item_label,
                        order=(idx + 1) * 10,
                        is_active=True
                    )
                self.stdout.write(self.style.SUCCESS(f"Sembrados {len(list_info['items'])} ítems en {list_info['label']}."))

        self.stdout.write(self.style.SUCCESS('¡Seeding completado exitosamente!'))
