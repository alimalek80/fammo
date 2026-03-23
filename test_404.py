"""
Test script to view the custom 404 page.

To test the 404 page:
1. Run the Django development server: python manage.py runserver
2. Visit any non-existent URL like: http://127.0.0.1:8000/this-does-not-exist
3. Or temporarily add this to your urls.py:
   from django.views.defaults import page_not_found
   path('test-404/', lambda request: page_not_found(request, Exception('Test 404'))),
"""

print("""
╔══════════════════════════════════════════════════════════╗
║              FAMMO 404 Page Test Guide                  ║
╚══════════════════════════════════════════════════════════╝

To test your beautiful new 404 error page:

✨ Method 1: Visit any non-existent URL
   → http://127.0.0.1:8000/this-page-does-not-exist
   → http://127.0.0.1:8000/random-url
   
✨ Method 2: Add a test route (temporary)
   Add this to famo/urls.py in urlpatterns:
   
   from django.http import Http404
   path('test-404/', lambda r: (_ for _ in ()).throw(Http404())),

✨ Method 3: Production testing
   Set DEBUG = False in settings.py (don't forget to set it back!)
   
🎨 Features of your new 404 page:
   ✓ Beautiful gradient 404 number with paw animation
   ✓ Integrated search bar for quick navigation
   ✓ Quick access cards to Home, Blog, and Pets
   ✓ Contact support section
   ✓ Go back button
   ✓ Fully responsive design
   ✓ Smooth animations and transitions
   ✓ Matches FAMMO's indigo/purple color scheme

📝 Note: Make sure your server is running:
   python manage.py runserver
""")
