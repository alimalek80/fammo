# FAMMO AI Contracts Specification

**Version:** 1.0  
**Date:** December 1, 2025  
**Purpose:** Define the proprietary AI model contracts for FAMMO's pet nutrition and preventive health platform

---

## Overview

This document specifies the complete AI interface contracts for FAMMO's proprietary machine learning model. The model is designed to replace or augment OpenAI-based predictions with in-house, trained models that provide:

- **Caloric requirement estimation** based on pet profiles
- **Diet style recommendations** tailored to individual needs
- **Preventive health risk assessment** across multiple categories
- **Structured, reproducible outputs** for mobile and web consumption

The model focuses on **preventive health and nutrition** — not medical diagnosis. All predictions are educational recommendations that encourage consultation with veterinary professionals.

---

## 1.1 – PetProfileInput Schema

The `PetProfileInput` schema defines all fields that the proprietary AI model requires as input. This schema is derived from FAMMO's existing database models (`Pet`, `Profile`) and represents the minimum viable data for accurate predictions.

### Core Identity Fields

- **`species`**
  - **Type:** `string` (enum)
  - **Valid values:** `"dog"`, `"cat"`
  - **Explanation:** The pet's species. FAMMO v1 supports dogs and cats only.

- **`breed`**
  - **Type:** `string`
  - **Valid values:** Any recognized breed name (e.g., `"Golden Retriever"`, `"Siamese"`, `"Mixed Breed"`)
  - **Explanation:** The specific breed. Used to infer breed-specific risks (hip dysplasia in large dogs, kidney issues in certain cat breeds). If unknown, use `"Mixed Breed"` or `"Unknown"`.

- **`breed_size_category`**
  - **Type:** `string` (enum)
  - **Valid values:** `"small"`, `"medium"`, `"large"`, `"giant"` (dogs); `"small"`, `"medium"`, `"large"` (cats)
  - **Explanation:** Size classification derived from breed. Affects caloric needs and joint risk assessment.

### Age & Life Stage

- **`age_years`**
  - **Type:** `float`
  - **Valid range:** `0.0 – 25.0`
  - **Explanation:** Pet's age in years (e.g., `3.5` for 3 years 6 months). Calculated from `birth_date` in the database.

- **`life_stage`**
  - **Type:** `string` (enum)
  - **Valid values:** 
    - Dogs: `"puppy"` (0–1y), `"junior"` (1–2y), `"adult"` (2–7y), `"senior"` (7+y)
    - Cats: `"kitten"` (0–1y), `"junior"` (1–2y), `"adult"` (2–10y), `"senior"` (10+y)
  - **Explanation:** Life stage category. Influences caloric requirements, nutrient ratios, and age-related risks.

### Physical Attributes

- **`weight_kg`**
  - **Type:** `float`
  - **Valid range:** `0.5 – 100.0`
  - **Explanation:** Current weight in kilograms. Critical for calorie calculation and obesity risk assessment.

- **`body_condition_score`**
  - **Type:** `integer` (enum)
  - **Valid values:** `1` (emaciated), `2` (underweight), `3` (ideal), `4` (overweight), `5` (obese)
  - **Explanation:** Visual body condition score. Maps to FAMMO's `BodyType` model. Used for weight risk classification.

- **`sex`**
  - **Type:** `string` (enum)
  - **Valid values:** `"male"`, `"female"`
  - **Explanation:** Biological sex. Affects metabolic rate slightly.

- **`neutered`**
  - **Type:** `boolean`
  - **Valid values:** `true`, `false`
  - **Explanation:** Whether the pet is spayed/neutered. Neutered pets have ~20% lower caloric needs.

### Activity & Lifestyle

- **`activity_level`**
  - **Type:** `string` (enum)
  - **Valid values:** `"sedentary"`, `"low"`, `"moderate"`, `"high"`, `"very_high"`
  - **Explanation:** Daily activity intensity. Maps to FAMMO's `ActivityLevel` model. Directly affects caloric multiplier.

- **`living_environment`**
  - **Type:** `string` (enum)
  - **Valid values:** `"indoor"`, `"outdoor"`, `"mixed"`
  - **Explanation:** Primary living environment. Indoor-only cats have lower activity; outdoor dogs may need more calories.

### Health & Medical History

- **`existing_conditions`**
  - **Type:** `array of strings`
  - **Valid values:** List of condition identifiers (e.g., `["diabetes", "kidney_disease", "arthritis", "allergies", "obesity"]`)
  - **Explanation:** Pre-existing health conditions from FAMMO's `HealthIssue` model. Used for risk assessment and diet contraindications.

- **`food_allergies`**
  - **Type:** `array of strings`
  - **Valid values:** List of allergen identifiers (e.g., `["chicken", "beef", "dairy", "grains", "soy"]`)
  - **Explanation:** Known food allergies from FAMMO's `FoodAllergy` model. Affects diet style recommendation.

- **`medications`**
  - **Type:** `array of strings`
  - **Valid values:** Medication names or categories (e.g., `["insulin", "NSAID", "thyroid_medication"]`)
  - **Explanation:** Current medications. Some medications affect appetite or nutrient absorption.

### Current Diet Information

- **`current_food_type`**
  - **Type:** `string` (enum)
  - **Valid values:** `"dry"`, `"wet"`, `"raw"`, `"homemade"`, `"mixed"`
  - **Explanation:** Current primary food type. Maps to FAMMO's `FoodType` model.

- **`food_satisfaction`**
  - **Type:** `string` (enum)
  - **Valid values:** `"always_hungry"`, `"satisfied"`, `"picky"`, `"overeating"`
  - **Explanation:** Owner's assessment of pet's eating behavior. Maps to `FoodFeeling` model.

- **`treat_frequency`**
  - **Type:** `string` (enum)
  - **Valid values:** `"never"`, `"rarely"`, `"weekly"`, `"daily"`, `"multiple_daily"`
  - **Explanation:** Frequency of treats. Affects total caloric intake estimation.

### Goals & Preferences

- **`health_goal`**
  - **Type:** `string` (enum)
  - **Valid values:** `"weight_loss"`, `"weight_gain"`, `"maintenance"`, `"muscle_building"`, `"joint_support"`, `"digestive_health"`, `"skin_coat_health"`, `"senior_wellness"`
  - **Explanation:** Primary health goal set by the owner. Determines diet style and caloric adjustment.

- **`dietary_preference`**
  - **Type:** `string` (enum)
  - **Valid values:** `"no_preference"`, `"grain_free"`, `"high_protein"`, `"low_fat"`, `"limited_ingredient"`, `"raw"`, `"holistic"`
  - **Explanation:** Owner's dietary philosophy preference. Influences diet style recommendation.

### Geographic & Environmental Context

- **`climate_zone`**
  - **Type:** `string` (enum)
  - **Valid values:** `"cold"`, `"temperate"`, `"warm"`, `"hot"`
  - **Explanation:** Climate where the pet lives. Derived from user's location. Affects caloric needs (cold climates = higher needs).

- **`country`**
  - **Type:** `string` (ISO 3166-1 alpha-2)
  - **Valid values:** Two-letter country code (e.g., `"FI"`, `"US"`, `"TR"`)
  - **Explanation:** User's country. May influence regional dietary trends or ingredient availability in future versions.

---

### PetProfileInput JSON Example

```json
{
  "species": "dog",
  "breed": "Golden Retriever",
  "breed_size_category": "large",
  "age_years": 3.5,
  "life_stage": "adult",
  "weight_kg": 29.0,
  "body_condition_score": 4,
  "sex": "male",
  "neutered": true,
  "activity_level": "moderate",
  "living_environment": "mixed",
  "existing_conditions": ["hip_dysplasia", "food_sensitivity"],
  "food_allergies": ["chicken", "dairy"],
  "medications": [],
  "current_food_type": "dry",
  "food_satisfaction": "always_hungry",
  "treat_frequency": "daily",
  "health_goal": "weight_loss",
  "dietary_preference": "grain_free",
  "climate_zone": "temperate",
  "country": "FI"
}
```

**Example 2: Senior Cat**

```json
{
  "species": "cat",
  "breed": "Siamese",
  "breed_size_category": "medium",
  "age_years": 12.0,
  "life_stage": "senior",
  "weight_kg": 3.2,
  "body_condition_score": 2,
  "sex": "female",
  "neutered": true,
  "activity_level": "low",
  "living_environment": "indoor",
  "existing_conditions": ["chronic_kidney_disease", "dental_disease"],
  "food_allergies": [],
  "medications": ["kidney_supplement"],
  "current_food_type": "wet",
  "food_satisfaction": "picky",
  "treat_frequency": "rarely",
  "health_goal": "senior_wellness",
  "dietary_preference": "low_fat",
  "climate_zone": "temperate",
  "country": "FI"
}
```

---

## 1.2 – ModelOutput Schema

The `ModelOutput` schema defines the structured predictions returned by FAMMO's proprietary model. All outputs are deterministic given the same input and model version.

### Caloric Requirements

- **`calories_per_day`**
  - **Type:** `integer`
  - **Valid range:** `50 – 5000`
  - **Explanation:** Estimated daily energy requirement (DER) in kilocalories. Calculated using modified formulas for Resting Energy Requirement (RER) and activity multipliers. This is the primary nutritional output.

- **`calorie_range_min`**
  - **Type:** `integer`
  - **Valid range:** `40 – 4500`
  - **Explanation:** Lower bound of the safe caloric range (typically 90% of `calories_per_day`).

- **`calorie_range_max`**
  - **Type:** `integer`
  - **Valid range:** `60 – 5500`
  - **Explanation:** Upper bound of the safe caloric range (typically 110% of `calories_per_day`).

### Macronutrient Targets

- **`protein_percent`**
  - **Type:** `integer`
  - **Valid range:** `18 – 50`
  - **Explanation:** Recommended protein percentage of diet (dry matter basis). Higher for active dogs, lower for senior cats with kidney issues.

- **`fat_percent`**
  - **Type:** `integer`
  - **Valid range:** `8 – 35`
  - **Explanation:** Recommended fat percentage of diet (dry matter basis). Adjusted for weight goals and activity level.

- **`carbohydrate_percent`**
  - **Type:** `integer`
  - **Valid range:** `5 – 50`
  - **Explanation:** Recommended carbohydrate percentage of diet. Lower for cats (obligate carnivores), higher acceptable for dogs.

### Diet Style Recommendation

- **`diet_style`**
  - **Type:** `string` (enum)
  - **Valid values:** See section 1.3 for full list (e.g., `"weight_loss"`, `"maintenance"`, `"senior_wellness"`, `"high_protein_performance"`)
  - **Explanation:** The recommended diet style category that best matches the pet's profile and goals.

- **`diet_style_confidence`**
  - **Type:** `float`
  - **Valid range:** `0.0 – 1.0`
  - **Explanation:** Model's confidence score for the diet style recommendation. Values below 0.6 may trigger suggestions for veterinary consultation.

### Risk Assessment

- **`risks`**
  - **Type:** `object` (nested structure)
  - **Explanation:** Preventive health risk scores across multiple categories. Each category has a level and optional notes.

  **Structure:**
  - **`weight_risk`**
    - **Type:** `string` (enum)
    - **Valid values:** `"low"`, `"medium"`, `"high"`
    - **Explanation:** Risk of obesity or unhealthy weight. Based on body condition score, breed, and activity level.
  
  - **`joint_risk`**
    - **Type:** `string` (enum)
    - **Valid values:** `"low"`, `"medium"`, `"high"`
    - **Explanation:** Risk of joint issues (arthritis, hip dysplasia). Higher for large breeds, overweight pets, and seniors.
  
  - **`digestive_risk`**
    - **Type:** `string` (enum)
    - **Valid values:** `"low"`, `"medium"`, `"high"`
    - **Explanation:** Risk of digestive issues (IBD, food sensitivities). Based on allergies, current food satisfaction, and breed predispositions.
  
  - **`metabolic_risk`**
    - **Type:** `string` (enum)
    - **Valid values:** `"low"`, `"medium"`, `"high"`
    - **Explanation:** Risk of metabolic disorders (diabetes, hyperthyroidism in cats). Based on age, weight, breed, and existing conditions.
  
  - **`kidney_risk`**
    - **Type:** `string` (enum)
    - **Valid values:** `"low"`, `"medium"`, `"high"`
    - **Explanation:** Risk of kidney disease (especially relevant for cats and senior pets). Based on age, breed, existing conditions, and diet.
  
  - **`dental_risk`**
    - **Type:** `string` (enum)
    - **Valid values:** `"low"`, `"medium"`, `"high"`
    - **Explanation:** Risk of dental disease. Higher for small breeds, senior pets, and those on primarily wet food diets.

### Feeding Recommendations

- **`meals_per_day`**
  - **Type:** `integer`
  - **Valid range:** `1 – 4`
  - **Explanation:** Recommended number of meals per day. Puppies/kittens need 3-4; adults typically 2; some seniors do well with 1-2.

- **`portion_size_grams`**
  - **Type:** `integer`
  - **Valid range:** `20 – 1000`
  - **Explanation:** Approximate portion size per meal in grams (for dry food reference). Actual amount depends on food caloric density.

### Model Metadata

- **`model_version`**
  - **Type:** `string`
  - **Valid values:** Semantic version (e.g., `"1.0.0"`, `"1.1.2"`)
  - **Explanation:** Version of the proprietary model used for this prediction. Enables tracking and A/B testing.

- **`prediction_timestamp`**
  - **Type:** `string` (ISO 8601)
  - **Valid values:** Datetime string (e.g., `"2025-12-01T14:32:15Z"`)
  - **Explanation:** UTC timestamp when the prediction was generated.

- **`confidence_score`**
  - **Type:** `float`
  - **Valid range:** `0.0 – 1.0`
  - **Explanation:** Overall model confidence in the prediction. Aggregate of individual task confidences.

### Alerts & Flags

- **`veterinary_consultation_recommended`**
  - **Type:** `boolean`
  - **Valid values:** `true`, `false`
  - **Explanation:** Flag indicating whether the model recommends consulting a veterinarian before implementing the diet plan. Triggered by high risk scores, extreme values, or low confidence.

- **`alert_messages`**
  - **Type:** `array of strings`
  - **Valid values:** List of alert strings (e.g., `["High kidney risk detected - consult vet for protein levels", "Underweight pet - gradual increase recommended"]`)
  - **Explanation:** Human-readable alerts and warnings based on the prediction results.

---

### ModelOutput JSON Example

**Example 1: Weight Loss Dog**

```json
{
  "calories_per_day": 780,
  "calorie_range_min": 702,
  "calorie_range_max": 858,
  "protein_percent": 28,
  "fat_percent": 12,
  "carbohydrate_percent": 40,
  "diet_style": "weight_loss",
  "diet_style_confidence": 0.87,
  "risks": {
    "weight_risk": "high",
    "joint_risk": "medium",
    "digestive_risk": "low",
    "metabolic_risk": "medium",
    "kidney_risk": "low",
    "dental_risk": "low"
  },
  "meals_per_day": 2,
  "portion_size_grams": 195,
  "model_version": "1.0.0",
  "prediction_timestamp": "2025-12-01T14:32:15Z",
  "confidence_score": 0.85,
  "veterinary_consultation_recommended": false,
  "alert_messages": [
    "Weight loss target detected - reduce calories by 15-20% from maintenance",
    "Monitor weight weekly and adjust portions as needed"
  ]
}
```

**Example 2: Senior Cat with Kidney Disease**

```json
{
  "calories_per_day": 185,
  "calorie_range_min": 167,
  "calorie_range_max": 204,
  "protein_percent": 26,
  "fat_percent": 18,
  "carbohydrate_percent": 35,
  "diet_style": "senior_wellness_kidney",
  "diet_style_confidence": 0.92,
  "risks": {
    "weight_risk": "medium",
    "joint_risk": "low",
    "digestive_risk": "low",
    "metabolic_risk": "low",
    "kidney_risk": "high",
    "dental_risk": "high"
  },
  "meals_per_day": 3,
  "portion_size_grams": 45,
  "model_version": "1.0.0",
  "prediction_timestamp": "2025-12-01T14:35:22Z",
  "confidence_score": 0.89,
  "veterinary_consultation_recommended": true,
  "alert_messages": [
    "Chronic kidney disease detected - veterinary-prescribed diet recommended",
    "Protein restriction may be necessary - consult vet before changes",
    "High dental risk - consider dental cleaning and smaller kibble"
  ]
}
```

**Example 3: Active Puppy**

```json
{
  "calories_per_day": 1250,
  "calorie_range_min": 1125,
  "calorie_range_max": 1375,
  "protein_percent": 32,
  "fat_percent": 18,
  "carbohydrate_percent": 35,
  "diet_style": "growth_puppy",
  "diet_style_confidence": 0.94,
  "risks": {
    "weight_risk": "low",
    "joint_risk": "low",
    "digestive_risk": "medium",
    "metabolic_risk": "low",
    "kidney_risk": "low",
    "dental_risk": "low"
  },
  "meals_per_day": 3,
  "portion_size_grams": 130,
  "model_version": "1.0.0",
  "prediction_timestamp": "2025-12-01T14:38:45Z",
  "confidence_score": 0.91,
  "veterinary_consultation_recommended": false,
  "alert_messages": [
    "Growth stage - ensure food is labeled for puppies/growth",
    "Monitor weight gain - should gain 2-4 lbs per week for large breeds"
  ]
}
```

---

## 1.3 – Risk Categories & Diet Styles

### Risk Categories

FAMMO's proprietary model assesses **six preventive health risk categories**. These are not diagnoses but predictive indicators based on breed, age, lifestyle, and current health status.

#### 1. Weight Risk

- **What it represents:** Likelihood of obesity, unhealthy weight gain, or being underweight
- **Relevance to FAMMO:** Weight is the #1 modifiable risk factor for pet health. Obesity affects 50%+ of pets in developed countries.
- **Impact on nutrition:** 
  - High risk → Calorie reduction (10-20%), higher protein, lower fat
  - Low risk (underweight) → Calorie increase (10-30%), balanced macros
- **Input factors:** Body condition score, weight_kg, breed, age, activity level, neutered status
- **Levels:**
  - **Low:** Ideal body condition (BCS 3), appropriate weight for breed/age
  - **Medium:** Slightly over/underweight (BCS 2 or 4), trending toward issue
  - **High:** Obese (BCS 5) or emaciated (BCS 1), immediate intervention needed

#### 2. Joint Risk

- **What it represents:** Likelihood of developing or worsening joint issues (arthritis, hip dysplasia, ligament injuries)
- **Relevance to FAMMO:** Common in large breeds, overweight pets, and seniors. Joint health directly impacts quality of life and activity level.
- **Impact on nutrition:** 
  - High risk → Weight management critical, recommend omega-3 fatty acids, glucosamine/chondroitin, anti-inflammatory foods
  - Low risk → Standard macronutrient ratios, maintain healthy weight
- **Input factors:** Breed size category, breed-specific predispositions, weight_kg, body condition score, age, existing conditions (arthritis), activity level
- **Levels:**
  - **Low:** Small/medium breed, ideal weight, young adult, active
  - **Medium:** Large breed OR senior OR slight overweight, no existing issues
  - **High:** Giant breed + overweight OR existing arthritis OR breed-specific risk (e.g., German Shepherd, Labrador)

#### 3. Digestive Risk

- **What it represents:** Likelihood of digestive issues (inflammatory bowel disease, food sensitivities, chronic diarrhea, vomiting)
- **Relevance to FAMMO:** Digestive health affects nutrient absorption and overall well-being. Food allergies and sensitivities are increasingly common.
- **Impact on nutrition:** 
  - High risk → Limited ingredient diets, novel proteins, avoid known allergens, easily digestible carbs (rice, potato), probiotics
  - Low risk → Standard diverse diet acceptable
- **Input factors:** Food allergies, existing conditions (IBD, pancreatitis), breed (some breeds prone to sensitivities), food satisfaction (picky eaters may have digestive discomfort), current food type
- **Levels:**
  - **Low:** No allergies, no digestive conditions, satisfied with food, stable digestion
  - **Medium:** 1-2 food allergies OR breed with moderate sensitivity (e.g., French Bulldog) OR picky eater
  - **High:** Multiple food allergies OR existing IBD/pancreatitis OR frequent digestive upset

#### 4. Metabolic Risk

- **What it represents:** Likelihood of metabolic disorders (diabetes mellitus, hyperthyroidism in cats, Cushing's disease, hypothyroidism in dogs)
- **Relevance to FAMMO:** Metabolic diseases require specific dietary management. Early intervention through diet can delay or prevent some metabolic issues.
- **Impact on nutrition:** 
  - High risk → Controlled carbohydrates, consistent meal timing, high fiber for diabetes, specific macros for thyroid issues
  - Low risk → Standard diet flexibility
- **Input factors:** Age, weight_kg, body condition score (obesity = diabetes risk), breed (e.g., cats > dogs for diabetes, Poodles for Cushing's), neutered status, existing conditions
- **Levels:**
  - **Low:** Young adult, ideal weight, no family/breed history, no symptoms
  - **Medium:** Senior OR overweight OR neutered cat (higher diabetes risk) OR breed predisposition
  - **High:** Existing metabolic condition OR obese + senior OR strong breed predisposition + symptoms

#### 5. Kidney Risk

- **What it represents:** Likelihood of chronic kidney disease (CKD) or acute kidney injury
- **Relevance to FAMMO:** CKD is extremely common in senior cats (30-40%) and increasingly recognized in dogs. Diet is a primary management tool.
- **Impact on nutrition:** 
  - High risk → Controlled protein (quality over quantity), phosphorus restriction, omega-3s, increased moisture (wet food), avoid high-sodium
  - Low risk → Standard protein levels acceptable
- **Input factors:** Age (senior = higher risk), species (cats >> dogs), breed (Persian cats, some terriers), existing conditions, medications, current food type (dry vs wet)
- **Levels:**
  - **Low:** Young adult, no breed risk, well-hydrated, no symptoms
  - **Medium:** Senior (especially cats) OR breed predisposition OR borderline lab values
  - **High:** Existing CKD diagnosis OR very senior cat OR dehydration issues OR strong breed risk + age

#### 6. Dental Risk

- **What it represents:** Likelihood of dental disease (gingivitis, periodontitis, tooth decay, tooth loss)
- **Relevance to FAMMO:** Dental disease affects 80%+ of pets by age 3. Leads to pain, infection, and systemic health issues.
- **Impact on nutrition:** 
  - High risk → Dry kibble for mechanical cleaning, dental-specific foods, avoid sticky treats, consider dental chews
  - Low risk → Diet flexibility, maintain good oral hygiene
- **Input factors:** Age, breed (small breeds >> large breeds), current food type (wet food = higher risk), treat frequency, existing conditions (dental disease)
- **Levels:**
  - **Low:** Young adult, large breed, primarily dry food, no existing issues
  - **Medium:** Small breed OR senior OR primarily wet food OR frequent treats
  - **High:** Small breed + senior + wet food OR existing dental disease

---

### Diet Styles

FAMMO's proprietary model recommends one of **ten diet styles** based on the pet's profile and health goals. Diet styles are mutually exclusive categories that guide food selection.

#### 1. Maintenance Standard

- **What it represents:** Balanced, all-life-stages diet for healthy adult pets with no special needs
- **Target pets:** Healthy adults, ideal weight, moderate activity, no health issues
- **Caloric approach:** Standard DER calculation (RER × activity multiplier)
- **Macronutrient profile:** 
  - Dogs: 25-30% protein, 12-18% fat, 40-50% carbs
  - Cats: 30-35% protein, 15-20% fat, 25-35% carbs
- **Key characteristics:** Balanced, diverse ingredients, no restrictions
- **FAMMO recommendation strategy:** Wide food selection, emphasize quality and variety

#### 2. Weight Loss

- **What it represents:** Calorie-restricted, high-satiety diet for overweight/obese pets
- **Target pets:** BCS 4-5, high weight risk, health goal = weight_loss
- **Caloric approach:** Reduce DER by 15-25%, target 1-2% body weight loss per week
- **Macronutrient profile:** 
  - High protein (28-35%) for satiety and muscle preservation
  - Low fat (8-12%)
  - Moderate-high fiber (carbs with fiber, 45-55%)
- **Key characteristics:** Low calorie density, high volume, satiating
- **FAMMO recommendation strategy:** Weight management formulas, portion control emphasis, progress tracking

#### 3. Weight Gain

- **What it represents:** Calorie-dense, nutrient-rich diet for underweight or recovering pets
- **Target pets:** BCS 1-2, low weight risk (underweight), health goal = weight_gain
- **Caloric approach:** Increase DER by 20-40%, gradual increase to avoid digestive upset
- **Macronutrient profile:** 
  - High protein (30-40%) for muscle building
  - High fat (18-25%) for calorie density
  - Moderate carbs (30-40%)
- **Key characteristics:** High palatability, calorie-dense, easily digestible
- **FAMMO recommendation strategy:** Recovery formulas, frequent meals, veterinary monitoring

#### 4. High Protein Performance

- **What it represents:** Protein-rich, energy-dense diet for highly active working dogs or athletic pets
- **Target pets:** Very high activity level, working dogs, agility competitors, sporting breeds
- **Caloric approach:** Increase DER by 30-50% based on activity
- **Macronutrient profile:** 
  - Very high protein (35-45%) for muscle repair
  - Moderate-high fat (18-25%) for sustained energy
  - Lower carbs (25-35%)
- **Key characteristics:** Performance-oriented, high bioavailability, fast recovery
- **FAMMO recommendation strategy:** Sport/performance formulas, timing around activity, hydration emphasis

#### 5. Senior Wellness

- **What it represents:** Moderate protein, joint-supportive, easily digestible diet for healthy senior pets
- **Target pets:** Life stage = senior, no major health issues, health goal = senior_wellness
- **Caloric approach:** Reduce DER by 10-20% (lower metabolism), adjust for activity
- **Macronutrient profile:** 
  - Moderate protein (24-28%) to support muscle mass without kidney stress
  - Moderate fat (12-16%)
  - Moderate carbs with fiber (40-50%) for digestive health
- **Key characteristics:** Joint support (glucosamine), antioxidants, easily digestible, lower phosphorus
- **FAMMO recommendation strategy:** Senior-specific formulas, smaller portions, soft/wet options for dental issues

#### 6. Senior Wellness Kidney

- **What it represents:** Kidney-supportive diet with controlled protein and phosphorus for senior pets with kidney concerns
- **Target pets:** Senior with high kidney risk or existing CKD (stage 1-2)
- **Caloric approach:** Standard for age, focus on nutrient quality over quantity
- **Macronutrient profile:** 
  - Controlled protein (22-26%) - high quality, highly digestible
  - Moderate fat (16-20%) for energy
  - Restricted phosphorus (<0.5% dry matter)
  - Increased omega-3 fatty acids
- **Key characteristics:** Wet food preferred, low sodium, antioxidants, avoids protein excess
- **FAMMO recommendation strategy:** Veterinary kidney diets, prescription formulas, hydration monitoring

#### 7. Growth Puppy

- **What it represents:** Nutrient-dense, calcium-controlled diet for growing puppies
- **Target pets:** Life stage = puppy, large/giant breeds need special care
- **Caloric approach:** High DER (RER × 2.0-3.0), frequent meals
- **Macronutrient profile:** 
  - High protein (28-32%) for growth
  - Moderate-high fat (15-20%) for energy
  - Controlled calcium (1.0-1.8%) to avoid skeletal issues in large breeds
- **Key characteristics:** AAFCO growth-labeled, balanced Ca:P ratio, DHA for brain development
- **FAMMO recommendation strategy:** Puppy-specific formulas, large-breed puppy formulas for giant breeds, feeding schedule guidance

#### 8. Growth Kitten

- **What it represents:** High-protein, energy-dense diet for growing kittens
- **Target pets:** Life stage = kitten
- **Caloric approach:** Very high DER (RER × 2.5-3.0), frequent meals
- **Macronutrient profile:** 
  - Very high protein (35-40%) - obligate carnivore needs
  - High fat (18-25%) for energy
  - Low carbs (20-30%)
- **Key characteristics:** AAFCO growth-labeled, taurine-rich, DHA for development
- **FAMMO recommendation strategy:** Kitten-specific formulas, wet food for hydration, gradual transition to adult food at 1 year

#### 9. Digestive Sensitive

- **What it represents:** Limited ingredient, novel protein, easily digestible diet for pets with food sensitivities
- **Target pets:** High digestive risk, multiple food allergies, existing IBD, picky eaters with digestive issues
- **Caloric approach:** Standard DER, focus on digestibility
- **Macronutrient profile:** 
  - Single protein source (novel: duck, venison, rabbit, fish)
  - Limited ingredients (5-10 total)
  - Easily digestible carbs (rice, potato, pumpkin)
  - Prebiotics/probiotics
- **Key characteristics:** Hypoallergenic, minimal additives, hydrolyzed protein options
- **FAMMO recommendation strategy:** Limited ingredient diets (LID), elimination diet trials, gradual transitions

#### 10. Grain-Free High Protein

- **What it represents:** Grain-free, high-protein diet for pets with grain sensitivities or owners preferring grain-free
- **Target pets:** Dietary preference = grain_free, mild digestive sensitivity to grains
- **Caloric approach:** Standard DER
- **Macronutrient profile:** 
  - High protein (30-38%)
  - Moderate-high fat (15-20%)
  - Grain-free carbs (potato, sweet potato, legumes, 30-40%)
- **Key characteristics:** No wheat/corn/soy, meat-first formulas
- **FAMMO recommendation strategy:** Grain-free formulas (with DCM awareness note), diverse protein sources, legume-based vs potato-based options
- **Important note:** Model should flag potential DCM (dilated cardiomyopathy) risk for dogs on grain-free diets, especially with high legume content and breeds predisposed to DCM (Golden Retrievers, Dobermans). Recommend taurine monitoring.

---

## 1.4 – Define Initial Prediction Tasks (v1 Model)

FAMMO's proprietary model v1 will handle **four core prediction tasks**. These tasks are designed to be trainable with a small labeled dataset (20-30 pets initially, expanding to 100-200 for production).

### Task 1: Daily Calorie Estimation

- **Task name:** `calorie_prediction`
- **Type:** **Regression**
- **Description:** Predict the optimal daily caloric intake (DER) for a pet based on their profile

**Inputs used:**
- `species`
- `weight_kg`
- `body_condition_score`
- `age_years`
- `life_stage`
- `activity_level`
- `neutered`
- `breed_size_category`
- `health_goal`
- `climate_zone`

**Output produced:**
- `calories_per_day` (integer)
- `calorie_range_min` (integer)
- `calorie_range_max` (integer)

**Training approach:**
- **Baseline model:** Calculate using established veterinary formulas (RER = 70 × weight_kg^0.75; DER = RER × activity multiplier)
- **ML enhancement:** Learn corrections based on actual pet outcomes (weight loss/gain success), breed-specific metabolic rates, and owner-reported satisfaction
- **Target metric:** Mean Absolute Error (MAE) < 50 kcal/day

**Dependencies:**
- None (foundational task)

**v1 training data:**
- Label source: Calculated from veterinary formulas + expert review for 30 diverse pet profiles
- Validation: Compare against published guidelines and existing FAMMO OpenAI meal plans

---

### Task 2: Risk Category Classification (Multi-Task)

- **Task name:** `risk_assessment`
- **Type:** **Multi-task Multi-class Classification** (6 independent classifiers, one per risk category)
- **Description:** Classify each of the six risk categories (weight, joint, digestive, metabolic, kidney, dental) as low/medium/high

**Inputs used:**
- **All input fields** from `PetProfileInput` (comprehensive risk assessment)
- Special emphasis per risk:
  - Weight risk: `body_condition_score`, `weight_kg`, `activity_level`, `neutered`
  - Joint risk: `breed_size_category`, `breed`, `age_years`, `weight_kg`, `existing_conditions` (arthritis)
  - Digestive risk: `food_allergies`, `existing_conditions` (IBD), `food_satisfaction`, `breed`
  - Metabolic risk: `age_years`, `body_condition_score`, `breed`, `neutered`, `existing_conditions` (diabetes)
  - Kidney risk: `species`, `age_years`, `breed`, `existing_conditions` (CKD), `current_food_type`
  - Dental risk: `age_years`, `breed_size_category`, `current_food_type`, `existing_conditions` (dental disease)

**Output produced:**
- `risks.weight_risk` (low/medium/high)
- `risks.joint_risk` (low/medium/high)
- `risks.digestive_risk` (low/medium/high)
- `risks.metabolic_risk` (low/medium/high)
- `risks.kidney_risk` (low/medium/high)
- `risks.dental_risk` (low/medium/high)

**Training approach:**
- **Baseline model:** Rule-based decision trees based on veterinary guidelines (e.g., if `age_years` > 10 AND `species` == "cat" → `kidney_risk` = high)
- **ML enhancement:** Learn from expert veterinarian labels on diverse pet profiles, capture breed-specific nuances
- **Target metric:** Classification accuracy > 80% per category (macro-averaged)

**Dependencies:**
- None (can run independently of other tasks)

**v1 training data:**
- Label source: Veterinary team manually labels 30 pet profiles across risk categories
- Class balance: Ensure representation of low/medium/high in each category (may need stratified sampling)

---

### Task 3: Diet Style Recommendation

- **Task name:** `diet_style_classification`
- **Type:** **Multi-class Classification** (10 classes)
- **Description:** Recommend the most appropriate diet style from the 10 defined categories

**Inputs used:**
- `species`
- `life_stage`
- `body_condition_score`
- `activity_level`
- `health_goal`
- `dietary_preference`
- `existing_conditions`
- `food_allergies`
- Risk outputs from Task 2 (optional enhancement)

**Output produced:**
- `diet_style` (one of 10 styles)
- `diet_style_confidence` (float 0-1)

**Training approach:**
- **Baseline model:** Rule-based mapping:
  ```
  IF life_stage == "puppy" → "growth_puppy"
  IF life_stage == "kitten" → "growth_kitten"
  IF health_goal == "weight_loss" AND body_condition_score >= 4 → "weight_loss"
  IF kidney_risk == "high" AND life_stage == "senior" → "senior_wellness_kidney"
  ...
  ```
- **ML enhancement:** Multi-class classifier (Random Forest or Gradient Boosting) learns from labeled data, captures edge cases
- **Target metric:** Top-1 accuracy > 75%, Top-2 accuracy > 90% (second choice often acceptable)

**Dependencies:**
- **Soft dependency** on Task 2 (risk_assessment): Can use predicted risk levels as additional features for diet style classification (especially for senior_wellness_kidney, weight_loss)
- If Task 2 not run, diet style still works with direct input features

**v1 training data:**
- Label source: Expert nutritionist assigns diet style to 30 pet profiles + reviews 50 existing FAMMO meal plans and extracts diet style labels
- Class imbalance handling: "maintenance_standard" likely most common; oversample rare classes (weight_gain, senior_wellness_kidney)

---

### Task 4: Macronutrient Target Estimation

- **Task name:** `macronutrient_prediction`
- **Type:** **Multi-output Regression** (3 continuous outputs: protein %, fat %, carb %)
- **Description:** Predict the optimal macronutrient distribution (protein, fat, carbohydrate percentages) for the pet

**Inputs used:**
- `species` (critical: cats need higher protein, lower carbs)
- `life_stage`
- `activity_level`
- `body_condition_score`
- `health_goal`
- `existing_conditions`
- Diet style from Task 3 (primary driver)
- Calorie prediction from Task 1 (context for energy density)

**Output produced:**
- `protein_percent` (integer 18-50)
- `fat_percent` (integer 8-35)
- `carbohydrate_percent` (integer 5-50)
- (Note: These should sum to ~100% but model may need constraint enforcement)

**Training approach:**
- **Baseline model:** Lookup tables based on diet style and species:
  ```
  weight_loss + dog → [28, 12, 60]
  senior_wellness_kidney + cat → [26, 18, 56]
  high_protein_performance + dog → [38, 22, 40]
  ```
- **ML enhancement:** Multi-output regression learns adjustments for individual profiles, captures interactions
- **Target metric:** MAE < 3% per macronutrient

**Dependencies:**
- **Strong dependency** on Task 3 (diet_style_classification): Macros are heavily determined by diet style
- **Weak dependency** on Task 1 (calorie_prediction): Context for energy density considerations
- Can run with direct inputs if prior tasks not available

**v1 training data:**
- Label source: Extract macros from existing FAMMO meal plans (100+ available), nutritionist-defined targets for 30 profiles
- Validation: Ensure outputs align with AAFCO minimums and veterinary nutrition guidelines

---

### Task Execution Flow

The four tasks can be executed in the following order for optimal results:

```
1. Task 1 (Calorie Prediction) → Independent, always runs first
   ↓ (optional input to Task 4)

2. Task 2 (Risk Assessment) → Independent, can run in parallel with Task 1
   ↓ (optional input to Task 3)

3. Task 3 (Diet Style Classification) → Uses health_goal, preferences, optionally risk outputs
   ↓ (primary input to Task 4)

4. Task 4 (Macronutrient Prediction) → Uses diet style, calories, and profile inputs
```

**For v1 MVP, all tasks can run independently** with direct input features. Dependencies are enhancements that improve accuracy when task outputs are available.

---

### Training Data Requirements (v1)

To train and validate FAMMO's proprietary model v1, we need:

1. **Minimum labeled dataset:**
   - **30 diverse pet profiles** with expert labels for all tasks
   - Coverage: 15 dogs (various breeds/sizes/ages), 15 cats (various breeds/ages)
   - Ensure representation of all diet styles and risk levels

2. **Existing FAMMO data:**
   - **Extract labels from 50-100 historical meal plans** generated by OpenAI
   - Parse structured outputs to label: diet style, macros, calorie recommendations

3. **Expert validation:**
   - Veterinary nutritionist reviews all labels for consistency
   - Resolves ambiguous cases (e.g., borderline BCS, multiple applicable diet styles)

4. **Synthetic augmentation:**
   - Generate synthetic profiles by varying input features (e.g., change weight +/- 20%, adjust age +/- 2 years)
   - Apply label propagation rules (e.g., if weight increased and BCS unchanged → risk levels stay same)

5. **Iterative expansion:**
   - v1.0: Train with 30 labeled profiles
   - v1.1: Add 50 real user pets with outcomes (did weight loss succeed?)
   - v1.2: Reach 200 labeled profiles for production-grade accuracy

---

### Model Architecture Recommendations (Future Phase)

For implementation (not required now, but noted for planning):

- **Task 1 (Calories):** Gradient Boosting Regressor (XGBoost or LightGBM)
- **Task 2 (Risks):** 6 independent Random Forest Classifiers or single multi-task neural network
- **Task 3 (Diet Style):** Random Forest Classifier or Multi-class Logistic Regression with feature engineering
- **Task 4 (Macros):** Multi-output Gradient Boosting Regressor with sum-to-100 constraint post-processing

**Feature engineering:**
- One-hot encode categorical variables (`species`, `breed`, `life_stage`, etc.)
- Create interaction features (e.g., `weight_kg` × `activity_level`, `age_years` × `species`)
- Normalize continuous features (`age_years`, `weight_kg`) with StandardScaler

**Model evaluation:**
- 70% train / 30% test split (stratified by species and life_stage)
- Cross-validation (5-fold) for robust performance estimates
- Track per-class metrics for imbalanced categories (e.g., rare diet styles, high-risk levels)

---

## Summary

This specification defines the complete AI contracts for FAMMO's proprietary model v1:

- **Input:** `PetProfileInput` schema with 24 fields covering identity, health, lifestyle, and goals
- **Output:** `ModelOutput` schema with calorie estimates, macronutrient targets, diet style, risk assessment (6 categories), feeding recommendations, and confidence metadata
- **Risk Categories:** 6 preventive health areas (weight, joint, digestive, metabolic, kidney, dental) with 3-level classification (low/medium/high)
- **Diet Styles:** 10 distinct diet categories aligned with pet needs and owner preferences
- **Prediction Tasks:** 4 core ML tasks (calorie regression, risk classification, diet style classification, macronutrient regression) designed for small dataset training

This design prioritizes **preventive nutrition**, **actionable recommendations**, and **transparent, structured outputs** that integrate seamlessly with FAMMO's existing Django + Flutter architecture.

The next phases will involve:
1. Converting this spec to Python dataclasses/Pydantic models
2. Creating Django serializers for API integration
3. Building baseline rule-based models for each task
4. Collecting labeled training data (30+ pet profiles)
5. Training ML models with scikit-learn/XGBoost
6. Deploying as a microservice or integrated Django app

**End of AI Contracts Specification**
