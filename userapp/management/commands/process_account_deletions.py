from django.core.management.base import BaseCommand
from userapp.models import AccountDeletionRequest, CustomUser
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Process account deletion requests that are ready for deletion'

    def handle(self, *args, **options):
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS('[START] Processing Account Deletions'))
        self.stdout.write("="*60 + "\n")
        
        # Get all approved requests ready for deletion
        ready_for_deletion = AccountDeletionRequest.objects.filter(
            status='approved',
            scheduled_deletion_date__lte=timezone.now()
        )
        
        deleted_count = 0
        failed_count = 0
        
        for deletion_request in ready_for_deletion:
            user = deletion_request.user
            email = user.email
            
            try:
                self.stdout.write(f"Processing deletion for: {email}")
                
                # Delete all user data
                from pet.models import Pet
                from vets.models import Clinic
                from aihub.models import AIRecommendation, AIHealthReport
                
                # Count what's being deleted
                pets_count = Pet.objects.filter(user=user).count()
                clinics_count = Clinic.objects.filter(owner=user).count()
                
                # Delete pets (cascade will delete related data)
                Pet.objects.filter(user=user).delete()
                
                # Delete clinics (cascade will delete related data)
                Clinic.objects.filter(owner=user).delete()
                
                # Delete AI data
                AIRecommendation.objects.filter(pet__user=user).delete()
                AIHealthReport.objects.filter(pet__user=user).delete()
                
                # Mark deletion request as completed
                deletion_request.status = 'completed'
                deletion_request.completed_at = timezone.now()
                deletion_request.save()
                
                # Send final email before deleting user
                try:
                    send_mail(
                        'Your Fammo Account Has Been Deleted',
                        f'''Your Fammo account has been permanently deleted as requested.

Email: {email}
Deleted: {timezone.now().strftime('%B %d, %Y at %H:%M')}

What was deleted:
- Your account and profile
- {pets_count} pet profile(s)
- {clinics_count} clinic(s)
- All AI recommendations and health reports
- All uploaded media

If this was done in error, please contact us immediately at support@fammo.ai

Thank you for using Fammo.
                        ''',
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=True,
                    )
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  Failed to send email: {str(e)}"))
                
                # Finally, delete the user (this will cascade delete profile and deletion request)
                user.delete()
                
                self.stdout.write(self.style.SUCCESS(
                    f"  ✓ Deleted: {email} ({pets_count} pets, {clinics_count} clinics)"
                ))
                deleted_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ✗ Failed to delete {email}: {str(e)}"))
                failed_count += 1
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS(f"Successfully deleted: {deleted_count} accounts"))
        if failed_count > 0:
            self.stdout.write(self.style.ERROR(f"Failed deletions: {failed_count}"))
        self.stdout.write("="*60 + "\n")
