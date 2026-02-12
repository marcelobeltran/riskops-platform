from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from risk_universe.models import Process, Risk, RiskCategory
from controls.models import Control, ControlAssessment
from monitoring.models import KRI, RiskEvent, ActionPlan
from knowledge.models import NormativeDocument, DocumentChunk, InterviewSession

class Command(BaseCommand):
    help = 'Setup default RiskOps roles and permissions'

    def handle(self, *args, **options):
        # Define Roles
        roles = {
            'Risk Analyst': {
                'models': [
                    Process, Risk, RiskCategory, Control, ControlAssessment, 
                    KRI, RiskEvent, ActionPlan, 
                    NormativeDocument, InterviewSession
                ],
                'perms': ['view', 'add', 'change'] # No delete by default
            },
            'Risk Supervisor': {
                'models': [
                    Process, Risk, RiskCategory, Control, ControlAssessment, 
                    KRI, RiskEvent, ActionPlan, 
                    NormativeDocument, InterviewSession
                ],
                'perms': ['view', 'add', 'change', 'delete']
            },
            'System Admin': {
                'models': [
                    Process, Risk, RiskCategory, Control, ControlAssessment, 
                    KRI, RiskEvent, ActionPlan, 
                    NormativeDocument, InterviewSession
                ],
                'perms': ['view', 'add', 'change', 'delete']
            }
        }

        for role_name, config in roles.items():
            group, created = Group.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(f'Created group: {role_name}')
            else:
                self.stdout.write(f'Updated group: {role_name}')
            
            # clear existing to reset state if running multiple times
            group.permissions.clear()

            for model in config['models']:
                content_type = ContentType.objects.get_for_model(model)
                for perm_code in config['perms']:
                    codename = f'{perm_code}_{model._meta.model_name}'
                    try:
                        perm = Permission.objects.get(content_type=content_type, codename=codename)
                        group.permissions.add(perm)
                    except Permission.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'Permission not found: {codename}'))
            
            self.stdout.write(self.style.SUCCESS(f'Permissions assigned to {role_name}'))
