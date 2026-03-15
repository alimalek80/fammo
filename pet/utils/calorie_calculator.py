"""
Pet Calorie Calculator Utilities

This module provides functions to calculate daily calorie requirements for pets
based on their weight, activity level, and other factors.
"""


def calculate_rer(weight_kg):
    """
    Calculate Resting Energy Requirement (RER) for a pet.
    
    Formula: RER = 70 * (weight_kg ** 0.75)
    
    Args:
        weight_kg (float): Pet's weight in kilograms
        
    Returns:
        float: Resting Energy Requirement in calories
    """
    if not weight_kg or weight_kg <= 0:
        return None
    
    return round(70 * (float(weight_kg) ** 0.75), 2)


def get_activity_factor(pet_type_name, activity_name, neutered=None, goal="maintain", age_years=0):
    """
    Get the activity factor multiplier for calorie calculations.
    
    Args:
        pet_type_name (str): Pet type ("cat", "dog", etc.)
        activity_name (str): Activity level name from database
        neutered (bool): Whether the pet is neutered/spayed
        goal (str): Weight goal - "maintain", "lose", or "gain"
        age_years (int): Pet's age in years
        
    Returns:
        float: Activity factor multiplier
    """
    # Normalize inputs
    pet_type = pet_type_name.lower().strip() if pet_type_name else ""
    activity = activity_name.lower().strip() if activity_name else ""
    
    # For very young pets (under 1 year), use high activity factor
    if age_years == 0:
        return 2.0
    
    # Base activity factor mappings
    activity_factors = {
        'cat': {
            'a serial snoozer': 1.0,
            'somewhat active': 1.2,
            'active': 1.4,
            'very active': 1.6,
            'full of energy': 1.8,
        },
        'dog': {
            'a serial snoozer': 1.2,
            'somewhat active': 1.4,
            'active': 1.6,
            'very active': 1.8,
            'full of energy': 2.0,
        }
    }
    
    # Get base factor for pet type and activity
    base_factor = None
    if pet_type in activity_factors and activity in activity_factors[pet_type]:
        base_factor = activity_factors[pet_type][activity]
    else:
        # Fallback values when activity level is missing or unrecognized
        if pet_type == 'cat':
            base_factor = 1.2 if neutered else 1.4
        elif pet_type == 'dog':
            base_factor = 1.6 if neutered else 1.8
        else:
            # Default fallback for unknown pet types
            base_factor = 1.4
    
    # Apply goal modifiers
    goal_modifiers = {
        'cat': {
            'lose': 0.8,
            'gain': 1.2,
            'maintain': 1.0,
        },
        'dog': {
            'lose': 1.0,
            'gain': 1.7,
            'maintain': 1.0,
        }
    }
    
    goal_modifier = 1.0  # Default
    if pet_type in goal_modifiers and goal in goal_modifiers[pet_type]:
        goal_modifier = goal_modifiers[pet_type][goal]
    
    return round(base_factor * goal_modifier, 2)


def calculate_pet_daily_calories(pet_type_name, weight_kg, activity_name=None, neutered=None, goal="maintain", age_years=0):
    """
    Calculate total daily calorie requirements for a pet.
    
    Args:
        pet_type_name (str): Pet type ("cat", "dog", etc.)
        weight_kg (float): Pet's weight in kilograms
        activity_name (str): Activity level name from database
        neutered (bool): Whether the pet is neutered/spayed
        goal (str): Weight goal - "maintain", "lose", or "gain"
        age_years (int): Pet's age in years
        
    Returns:
        dict: Dictionary containing:
            - rer: Resting Energy Requirement
            - factor: Activity factor used
            - daily_calories: Total daily calorie requirement
        Returns None if required data is missing.
    """
    # Calculate RER
    rer = calculate_rer(weight_kg)
    if rer is None:
        return None
    
    # Get activity factor
    factor = get_activity_factor(pet_type_name, activity_name, neutered, goal, age_years)
    
    # Calculate total daily calories
    daily_calories = round(rer * factor)
    
    return {
        'rer': rer,
        'factor': factor,
        'daily_calories': daily_calories
    }