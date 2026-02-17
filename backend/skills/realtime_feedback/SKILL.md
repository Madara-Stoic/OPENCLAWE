---
name: realtime_feedback
description: Provides real-time feedback and coaching based on current vitals and trends.
version: 1.0.0
author: OmniHealth Guardian
metadata:
  openclaw:
    emoji: "💬"
    requires:
      services: ["mongodb"]
      env: ["MONGO_URL"]
    triggers:
      - vital_reading
      - cron:30s
    actions:
      - analyze_trend
      - generate_feedback
      - coaching_tips
    priority: normal
---

# Real-time Feedback

This OpenClaw skill provides immediate, personalized coaching and feedback based on current vital signs and historical trends.

## Analysis Components

### Trend Analysis
- Compares recent readings (last 5) with previous readings (5-10)
- Identifies rising, falling, or stable patterns
- Flags concerning changes

### Feedback Types
- **Immediate Actions**: What to do right now
- **Status Updates**: Current health status
- **Warnings**: Potential issues to watch

### Coaching Tips
- Condition-specific lifestyle recommendations
- Activity suggestions
- Medication reminders

## Response Format

```json
{
  "feedback": ["array of feedback messages"],
  "trend_analysis": {
    "status": "stable|concerning|improving",
    "direction": "rising|falling|flat"
  },
  "coaching_tips": ["array of personalized tips"]
}
```

## Usage

```bash
POST /api/moltbot/execute
Content-Type: application/json

{
  "skill": "realtime_feedback",
  "params": {
    "patient_id": "patient-123"
  }
}
```
