from django.core.management.base import BaseCommand
from blog.models import BlogPost

class Command(BaseCommand):
    help = 'Preview and fix stale /blog/ links in post markdown content'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Apply fixes (default is dry-run)',
        )

    def handle(self, *args, **options):
        apply = options['apply']
        posts = BlogPost.objects.filter(content__contains='](/blog/')
        if not posts.exists():
            self.stdout.write('No stale /blog/ links found in content.')
            return
        self.stdout.write(f'Found {posts.count()} post(s) with stale links:')
        for post in posts:
            self.stdout.write(f'  [{post.id}] {post.title}')
            if apply:
                post.content = post.content.replace('](/blog/', '](/en/blog/')
                post.save(update_fields=['content'])
                self.stdout.write('    → Fixed.')
            else:
                self.stdout.write('    → Dry run. Use --apply to fix.')
        if not apply:
            self.stdout.write('\nRun with --apply to apply all fixes.')
