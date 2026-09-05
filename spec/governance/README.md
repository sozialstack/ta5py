# Format Spec Governance

Durable state for publication detection, integration candidates, and live-version approval.

- `live-version.yaml` — approved default package label (human go-live only)
- `detections/` — DetectionRun records
- `candidates/` — IntegrationCandidate records

No Sozialdaten. Automatic detect/integrate **must not** change `live-version.yaml`.
