# Shared JSON Schema Spec

## Common Conventions
- Use snake_case for all keys
- Timestamps must be ISO 8601 UTC strings
- Scores should be in [0, 1]
- asset_id, zone_id, incident_id are strings
- message_type is mandatory for all inter-module messages

## Message Types
1. processed_telemetry
2. anomaly_result
3. predictive_result
4. diagnosis_result
5. decision_result
6. incident_summary

## Ownership
- processed_telemetry: data pipeline owner
- anomaly_result / predictive_result: model owner
- diagnosis_result / decision_result / incident_summary: orchestration owner
- dashboard reads incident_summary