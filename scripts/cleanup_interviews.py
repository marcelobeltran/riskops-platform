import os
import django
import sys
from django.utils import timezone
from django.db.models import Count

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from knowledge.models import InterviewSession

def cleanup_duplicates():
    print("Starting cleanup of duplicate interview sessions...")
    
    # Define fields that identify a duplicate
    # title, date, interviewer, interviewee, process
    duplicates = InterviewSession.objects.filter(is_deleted=False).values(
        'title', 'date', 'interviewer', 'interviewee', 'process'
    ).annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    total_archived = 0
    
    for group in duplicates:
        # Get all sessions in this group ordered by updated_at (newest first)
        sessions = InterviewSession.objects.filter(
            title=group['title'],
            date=group['date'],
            interviewer=group['interviewer'],
            interviewee=group['interviewee'],
            process=group['process'],
            is_deleted=False
        )
        
        sessions = sessions.order_by('-updated_at', '-created_at')
        
        # Keep the first one, archive the rest
        keep = sessions[0]
        to_archive = sessions[1:]
        
        for s in to_archive:
            s.is_deleted = True
            s.deleted_at = timezone.now()
            s.title = f"{s.title} (archivada por duplicidad)"
            s.save()
            total_archived += 1
            print(f"Archived duplicate: {s.title} (ID: {s.id})")
            
    print(f"Cleanup finished. Total sessions archived: {total_archived}")

if __name__ == "__main__":
    cleanup_duplicates()
