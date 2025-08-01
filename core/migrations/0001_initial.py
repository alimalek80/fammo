# Generated by Django 5.2.4 on 2025-07-21 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HeroSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(help_text="The main title, e.g., 'Healthy Meals, Happy Pets!'", max_length=200)),
                ('subheading', models.TextField(help_text='The paragraph text below the main title.')),
                ('button_text', models.CharField(help_text='The text for the call-to-action button.', max_length=50)),
                ('button_url', models.CharField(help_text="The URL the button links to. Can be a full URL or a Django URL name like '/pets/create/'.", max_length=200)),
                ('background_image', models.ImageField(help_text='Background image. Recommended size: 1920x1080px.', upload_to='hero_backgrounds/')),
                ('is_active', models.BooleanField(default=True, help_text='Only one hero section can be active at a time.')),
            ],
            options={
                'verbose_name': 'Homepage Hero Section',
                'verbose_name_plural': 'Homepage Hero Sections',
            },
        ),
    ]
