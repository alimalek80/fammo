from django.apps import AppConfig


class AiCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_core'
    verbose_name = 'AI Core'
    
    def ready(self):
        """
        Initialize AI Core app when Django starts.
        
        This method is called once Django has loaded all apps.
        Use it for:
        - Registering signal handlers
        - Initializing caches
        - Validating configuration
        """
        pass
