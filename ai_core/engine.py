"""
FAMMO AI Engine Factory

This module provides the central entry point for accessing FAMMO's nutrition AI engine.
The get_engine() function returns the configured AI backend based on Django settings.

DRF views should use this factory to obtain an engine instance:
    from ai_core.engine import get_engine
    
    engine = get_engine()
    output = engine.predict(pet_profile)

Supported Backends:
- "openai": Uses OpenAI GPT models with structured outputs (default)
- "proprietary": Uses FAMMO's trained ML models (XGBoost, Random Forest)

Configuration:
Set AI_BACKEND in Django settings.py:
    AI_BACKEND = "openai"  # or "proprietary"
"""

from django.conf import settings

from ai_core.interfaces import NutritionEngineInterface, PetProfile, ModelOutput

# Import the real implementations
from ai_core.openai_backend import OpenAIEngine
from ai_core.proprietary_backend import ProprietaryEngine


# Mapping of backend names to engine classes
_ENGINE_REGISTRY = {
    "openai": OpenAIEngine,
    "proprietary": ProprietaryEngine,
}


def get_engine() -> NutritionEngineInterface:
    """
    Factory function to get the configured AI engine instance.
    
    This is the single entry point that all FAMMO code should use to access
    the nutrition AI engine. The specific backend is controlled by the
    AI_BACKEND setting in Django settings.py.
    
    Returns:
        NutritionEngineInterface: An instance of the configured engine
            (OpenAIEngine or ProprietaryEngine).
    
    Raises:
        ValueError: If AI_BACKEND contains an invalid/unsupported value.
    
    Configuration:
        In settings.py, set:
            AI_BACKEND = "openai"  # Default, uses OpenAI GPT models
            # OR
            AI_BACKEND = "proprietary"  # Uses FAMMO's trained ML models
        
        If AI_BACKEND is not set, defaults to "openai".
    
    Usage in DRF Views:
        from ai_core.engine import get_engine
        from ai_core.interfaces import PetProfile
        
        def generate_meal_plan(request, pet_id):
            # Build pet profile from database
            pet_profile = PetProfile(...)
            
            # Get engine and generate prediction
            engine = get_engine()
            output = engine.predict(pet_profile)
            
            # Use output for response
            return Response({
                "calories_per_day": output.calories_per_day,
                "diet_style": output.diet_style,
                ...
            })
    
    Example:
        >>> engine = get_engine()
        >>> profile = PetProfile(species="dog", breed="Beagle", ...)
        >>> output = engine.predict(profile)
        >>> print(output.calories_per_day)
        850
    """
    # Get backend name from settings, default to "openai"
    backend_name = getattr(settings, "AI_BACKEND", "openai")
    
    # Normalize to lowercase for case-insensitive comparison
    backend_name = backend_name.lower().strip()
    
    # Look up engine class in registry
    engine_class = _ENGINE_REGISTRY.get(backend_name)
    
    if engine_class is None:
        # Invalid backend specified
        valid_backends = ", ".join(f'"{name}"' for name in _ENGINE_REGISTRY.keys())
        raise ValueError(
            f"Invalid AI_BACKEND setting: '{backend_name}'. "
            f"Must be one of: {valid_backends}. "
            f"Check your Django settings.py configuration."
        )
    
    # Instantiate and return the engine
    return engine_class()


def register_engine(name: str, engine_class: type[NutritionEngineInterface]) -> None:
    """
    Register a custom engine implementation.
    
    This allows third-party or experimental engines to be registered dynamically
    without modifying this file. Useful for A/B testing or plugin architectures.
    
    Args:
        name (str): Backend name to use in AI_BACKEND setting.
        engine_class (type[NutritionEngineInterface]): Engine class that implements
            the NutritionEngineInterface.
    
    Raises:
        TypeError: If engine_class does not inherit from NutritionEngineInterface.
        ValueError: If name is empty or conflicts with built-in backends.
    
    Example:
        from ai_core.engine import register_engine
        from ai_core.interfaces import NutritionEngineInterface
        
        class ExperimentalEngine(NutritionEngineInterface):
            def predict(self, pet):
                ...
        
        register_engine("experimental", ExperimentalEngine)
        
        # Now in settings.py:
        # AI_BACKEND = "experimental"
    """
    if not name or not isinstance(name, str):
        raise ValueError("Engine name must be a non-empty string")
    
    name = name.lower().strip()
    
    if not issubclass(engine_class, NutritionEngineInterface):
        raise TypeError(
            f"{engine_class.__name__} must inherit from NutritionEngineInterface"
        )
    
    # Warn if overriding built-in backend
    if name in ["openai", "proprietary"]:
        import warnings
        warnings.warn(
            f"Overriding built-in backend '{name}' with {engine_class.__name__}",
            UserWarning,
            stacklevel=2
        )
    
    _ENGINE_REGISTRY[name] = engine_class
