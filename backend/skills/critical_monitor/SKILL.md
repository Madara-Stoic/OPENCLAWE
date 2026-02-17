---
name: critical_condition_monitor
description: Monitors patient vitals for critical conditions. Triggers blockchain verification and hospital notification when thresholds exceeded.
version: 1.0.0
author: OmniHealth Guardian
metadata:
  openclaw:
    emoji: "🚨"
    requires:
      services: ["mongodb", "blockchain"]
      env: ["MONGO_URL"]
    triggers:
      - vital_reading
      - cron:5s
    actions:
      - record_alert
      - notify_hospital
      - hash_on_chain
    priority: critical
---

# Critical Condition Monitor

This OpenClaw skill monitors real-time patient vitals from medical IoT devices and triggers alerts when critical thresholds are exceeded.

## Thresholds

| Condition | Low Alert | High Alert |
|-----------|-----------|------------|
| Glucose (mg/dL) | < 70 | > 250 |
| Heart Rate (BPM) | < 50 | > 120 |
| Battery (%) | < 15 | N/A |

## Actions

1. **record_alert**: Store alert in MongoDB with SHA-256 hash
2. **notify_hospital**: Send notification to nearest hospital
3. **hash_on_chain**: Record hash on HealthAudit smart contract (opBNB)

## On-Chain Verification

All critical alerts are hashed using SHA-256 and recorded on the opBNB blockchain for tamper-proof audit trail.

## Usage

```bash
POST /api/moltbot/execute
Content-Type: application/json

{
  "skill": "critical_condition_monitor",
  "params": {
    "patient_id": "patient-123"
  }
}
```
