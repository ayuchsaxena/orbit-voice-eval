# Starting models and evaluation tools

Orbit should begin with frozen, swappable evaluators—not a newly trained monolithic model. No single open model currently supplies calibrated audio risk, conversation timing, task outcomes, and useful in-call actions together.

| Component | Best initial use | Limitation / terms |
|---|---|---|
| Brouhaha VAD/SNR/C50 worker (included) | Initial speech activity and acoustic measurements | Estimates are not downstream failure probabilities; verify checkpoint terms and runtime cost |
| NISQA | Candidate non-intrusive speech-quality model; can be fine-tuned | Repository says code MIT, released weights CC BY-NC-SA 4.0; released weights may not fit commercial use |
| VERSA | Offline comparison harness across multiple audio metrics | Toolkit is MIT; inspect each backend and model's own terms |
| DNS Challenge resources | Noise suppression and controlled degradation research | Data and source assets retain their own terms; enhancement quality is not the same as agent success |
| ServiceNow EVA | Reference for end-to-end multi-turn voice-agent evaluation | Evaluation framework, not a live audio quality model |

Suggested sequence:

1. Establish the production-call temporal graph and baseline outcomes.
2. Run existing eligible metrics in shadow mode and compare them with graph events and reviewed outcomes.
3. Select a model based on domain match, language, license, CPU/latency, and calibration—not leaderboard score alone.
4. Fine-tune or train a small task-specific scorer only after collecting reliable real-call labels; keep a held-out test set untouched.
5. Add an intervention policy and measure the action's effect separately from the signal's predictive value.

See [`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md) for known license cautions. This table is a starting point; verify current upstream terms before adoption.

