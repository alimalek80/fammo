"""
Quick integration test for OpenAI backend.

This test verifies that the OpenAI engine can be instantiated and
that get_engine() returns the correct engine when AI_BACKEND="openai".

Note: This does NOT call the real OpenAI API to avoid costs and rate limits.
For real API testing, use manual testing or set up proper mocking.
"""

import os
import sys

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'famo.settings')

import django
django.setup()

from ai_core.engine import get_engine
from ai_core.openai_backend import OpenAIEngine
from ai_core.interfaces import PetProfile


def test_engine_instantiation():
    """Test that OpenAI engine can be instantiated."""
    print("✓ Testing OpenAI engine instantiation...")
    
    engine = OpenAIEngine()
    assert engine is not None, "Engine should not be None"
    assert hasattr(engine, 'predict'), "Engine should have predict method"
    assert hasattr(engine, 'model'), "Engine should have model attribute"
    
    print(f"  - Model: {engine.model}")
    print("✓ OpenAI engine instantiation successful")


def test_get_engine_returns_openai():
    """Test that get_engine() returns OpenAIEngine when AI_BACKEND='openai'."""
    print("\n✓ Testing get_engine() factory...")
    
    from django.conf import settings
    
    # Check or set AI_BACKEND
    backend = getattr(settings, 'AI_BACKEND', 'openai')
    print(f"  - AI_BACKEND setting: {backend}")
    
    engine = get_engine()
    assert engine is not None, "get_engine() should not return None"
    assert isinstance(engine, OpenAIEngine), f"Expected OpenAIEngine, got {type(engine)}"
    
    print(f"  - Engine type: {type(engine).__name__}")
    print("✓ get_engine() factory successful")


def test_prompt_building():
    """Test that _build_prompt generates valid prompt."""
    print("\n✓ Testing prompt building...")
    
    engine = OpenAIEngine()
    
    # Create a simple pet profile
    pet = PetProfile(
        species="dog",
        breed="Golden Retriever",
        breed_size_category="large",
        age_years=3.5,
        life_stage="adult",
        weight_kg=29.0,
        body_condition_score=4,
        sex="male",
        neutered=True,
        activity_level="moderate",
        health_goal="weight_loss",
    )
    
    prompt = engine._build_prompt(pet)
    
    assert len(prompt) > 100, "Prompt should be substantial"
    assert "Golden Retriever" in prompt, "Prompt should contain breed"
    assert "3.5 years" in prompt, "Prompt should contain age"
    assert "29.0 kg" in prompt, "Prompt should contain weight"
    assert "weight_loss" in prompt, "Prompt should contain health goal"
    assert "diet_style" in prompt.lower(), "Prompt should mention diet_style output"
    assert "risks" in prompt.lower(), "Prompt should mention risks"
    
    print(f"  - Prompt length: {len(prompt)} characters")
    print(f"  - Contains required fields: ✓")
    print("✓ Prompt building successful")


if __name__ == "__main__":
    print("=" * 70)
    print("OpenAI Backend Integration Test")
    print("=" * 70)
    
    try:
        test_engine_instantiation()
        test_get_engine_returns_openai()
        test_prompt_building()
        
        print("\n" + "=" * 70)
        print("✅ All tests passed!")
        print("=" * 70)
        print("\n📝 Note: These tests verify structure only.")
        print("   To test real OpenAI API calls, use the nutrition endpoint:")
        print("   POST /api/v1/ai/nutrition/ with a valid pet profile JSON")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
