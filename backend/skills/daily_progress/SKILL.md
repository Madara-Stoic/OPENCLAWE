---
name: daily_progress_tracker
description: Tracks daily health progress, aggregates metrics, and generates daily health reports.
version: 1.0.0
author: OmniHealth Guardian
metadata:
  openclaw:
    emoji: "📊"
    requires:
      services: ["mongodb"]
      env: ["MONGO_URL"]
    triggers:
      - end_of_day
      - manual
      - cron:24h
    actions:
      - aggregate_metrics
      - calculate_scores
      - generate_report
      - store_greenfield
    priority: normal
---

# Daily Progress Tracker

This OpenClaw skill generates comprehensive daily health reports by aggregating all readings, alerts, and activities from the day.

## Metrics Calculated

### Vital Metrics
- Average glucose level
- Min/Max glucose
- Time in range (70-180 mg/dL)
- Average heart rate
- Heart rate variability

### Compliance Metrics
- Diet compliance score (0-100%)
- Activity score (0-100%)
- Medication adherence

### Health Score
- Overall daily health score (0-100)
- Based on:
  - Time in glucose range (+15 if >70%)
  - Critical events (-5 per event)
  - Diet compliance
  - Activity level

## Report Contents

1. **Daily Summary**: Key metrics at a glance
2. **Alerts Summary**: Critical events from the day
3. **Recommendations**: Personalized suggestions for improvement
4. **Trend Comparison**: Today vs previous days

## Storage

Reports are stored on BNB Greenfield for permanent, decentralized access.

## Usage

```bash
POST /api/moltbot/execute
Content-Type: application/json

{
  "skill": "daily_progress_tracker",
  "params": {
    "patient_id": "patient-123",
    "date": "2025-12-15"
  }
}
```
