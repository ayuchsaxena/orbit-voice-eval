# Contributing to Orbit

Thanks for helping make voice-agent evaluation more reliable and useful.

## Before you contribute

- Open an issue for substantial changes so scope and evaluation criteria are visible.
- Keep measurements, interpretations, and actions separate.
- Include provenance and license information for external code, weights, and data.
- Never add private call recordings, credentials, or identifiable transcripts.
- Treat sentiment, emotion, and behavior attributes as uncertain observations, not facts.

## Contribution areas

- Audio metric adapters with reproducible CPU/GPU and latency measurements.
- Outcome labels and evaluation protocols tied to real agent behavior.
- Synthetic perturbation recipes with known parameters and held-out conditions.
- Live-agent signal integrations that preserve timing and avoid blocking audio callbacks.
- Documentation, examples, and independent human-review studies.

## Pull requests

Describe the user problem, changes, evidence, known limitations, and applicable third-party licenses. For a new metric, state its input assumptions, output calibration, training/evaluation domains, runtime cost, and failure modes. Keep datasets out of pull requests; provide a dataset card and acquisition instructions instead.

By submitting a contribution, you agree that it is provided under the repository's MIT license.

