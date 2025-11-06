from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.sites.models import Site

try:
    from allauth.socialaccount.models import SocialApp
except Exception as e:
    SocialApp = None

try:
    from decouple import config
except Exception:
    # Fallback to environment if python-decouple is not available
    import os
    def config(key, default=None):
        return os.environ.get(key, default)


class Command(BaseCommand):
    help = "Create or update the Google SocialApp and attach it to the current SITE_ID."

    def add_arguments(self, parser):
        parser.add_argument('--client-id', dest='client_id', default=None,
                            help='Google OAuth client id (overrides GOOGLE_CLIENT_ID env)')
        parser.add_argument('--secret', dest='secret', default=None,
                            help='Google OAuth client secret (overrides GOOGLE_CLIENT_SECRET env)')
        parser.add_argument('--name', dest='name', default='Google',
                            help='Display name for the SocialApp (default: Google)')

    def handle(self, *args, **options):
        if SocialApp is None:
            raise CommandError('django-allauth is not installed or not importable.')

        site_id = getattr(settings, 'SITE_ID', None)
        if not site_id:
            raise CommandError('SITE_ID is not configured in settings.')

        client_id = options['client_id'] or config('GOOGLE_CLIENT_ID', default=None)
        secret = options['secret'] or config('GOOGLE_CLIENT_SECRET', default=None)

        if not client_id or not secret:
            raise CommandError(
                'Missing Google credentials. Provide --client-id/--secret or set '
                'GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your environment/.env.'
            )

        # Ensure Site exists
        site, _ = Site.objects.get_or_create(id=site_id, defaults={'domain': 'localhost', 'name': 'localhost'})

        app, created = SocialApp.objects.get_or_create(provider='google', defaults={
            'name': options['name'],
            'client_id': client_id,
            'secret': secret,
        })

        # Update credentials if changed
        changed = False
        if app.client_id != client_id:
            app.client_id = client_id
            changed = True
        if app.secret != secret:
            app.secret = secret
            changed = True
        if app.name != options['name']:
            app.name = options['name']
            changed = True
        if changed:
            app.save()

        # Attach to site if not already
        if site not in app.sites.all():
            app.sites.add(site)

        self.stdout.write(self.style.SUCCESS(
            f"Google SocialApp {'created' if created else 'updated'} and attached to Site(id={site_id}, domain={site.domain})."
        ))
