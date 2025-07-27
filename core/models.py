from django.db import models

# Create your models here.

class HeroSection(models.Model):
    """Model to store the content for the homepage hero section."""
    heading = models.CharField(max_length=200, help_text="The main title, e.g., 'Healthy Meals, Happy Pets!'")
    subheading = models.TextField(help_text="The paragraph text below the main title.")
    button_text = models.CharField(max_length=50, help_text="The text for the call-to-action button.")
    button_url = models.CharField(max_length=200, help_text="The URL the button links to. Can be a full URL or a Django URL name like '/pets/create/'.")
    
    # For the background image, a good size is 1920x1080 pixels, optimized for the web (e.g., as a .webp or compressed .jpg).
    background_image = models.ImageField(upload_to='hero_backgrounds/', help_text="Background image. Recommended size: 1920x1080px.")
    
    is_active = models.BooleanField(default=True, help_text="Only one hero section can be active at a time.")

    def __str__(self):
        return f"Homepage Hero Section - {self.heading}"

    def save(self, *args, **kwargs):
        # Ensure only one instance is active
        if self.is_active:
            HeroSection.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Homepage Hero Section"
        verbose_name_plural = "Homepage Hero Sections"
