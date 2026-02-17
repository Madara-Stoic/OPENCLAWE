---
name: ai_diet_suggestion
description: Generates personalized AI diet plans based on patient condition and recent vitals. Verified by OpenClaw.
version: 1.0.0
author: OmniHealth Guardian
metadata:
  openclaw:
    emoji: "🥗"
    requires:
      services: ["llm", "mongodb"]
      env: ["EMERGENT_LLM_KEY", "MONGO_URL"]
      bins: ["python3"]
    triggers:
      - meal_time
      - manual
      - cron:1h
    actions:
      - generate_diet
      - verify_openclaw
      - store_greenfield
    priority: normal
---

# AI Diet Suggestion

This OpenClaw skill generates personalized dietary recommendations using AI, based on the patient's medical condition and recent vital readings.

## Supported Conditions

- **diabetes_type1**: Low-carb, insulin-aware meal planning
- **diabetes_type2**: Glycemic index-focused, portion control
- **heart_condition**: Low sodium, heart-healthy fats

## Meal Types

- `daily`: Full day meal plan (breakfast, lunch, dinner, snacks)
- `breakfast`: Morning meal suggestions
- `lunch`: Midday meal suggestions
- `dinner`: Evening meal suggestions
- `snack`: Between-meal options

## AI Model

Uses GPT-4o via Emergent Integrations for intelligent diet generation with medical context awareness.

## Verification

All diet plans are:
1. Hashed with SHA-256
2. Recorded on opBNB blockchain
3. Stored on BNB Greenfield for permanent access

## Usage

```bash
POST /api/moltbot/execute
Content-Type: application/json

{
  "skill": "ai_diet_suggestion",
  "params": {
    "patient_id": "patient-123",
    "meal_type": "daily"
  }
}
```
