# Orbit

**Open tools for measuring and improving voice-agent quality.**

Orbit is an early, community-built project for evaluating the audio and speech quality of voice agents, identifying likely failure conditions, and giving agents useful signals during a call. It combines an evidence-based conversation evaluator, an optional audio-analysis worker, a production baseline protocol, and a path for model adapters and safe interventions.

> **Status: experimental.** The included evaluator is a post-call research baseline. It is not a calibrated failure predictor, and it does not yet make live interventions. Do not use its provisional behavior labels as facts about a person. Live adaptation and risk thresholds require validation against real outcomes.

## What is here

- `packages/evaluator/`: provider-neutral TypeScript evaluator for turn-level transcript cues, temporal measures, evidence, confidence, and limitations.
- `services/audio-worker/`: optional FastAPI worker that extracts five-second audio measurements using Brouhaha plus direct signal measurements.
- `docs/architecture.md`: target system architecture, including a live signal and intervention contract.
- `schemas/` and `examples/`: an initial temporal event schema and an illustrative graph showing how evidence, agent action, and outcome connect.
- `docs/baseline.md`: how to define the current production call as the comparison baseline.
- `docs/synthetic-data.md`: a controlled synthetic audio recipe and its limits.
- `docs/model-selection.md`: open-source model strategy and licensing notes.

## Quick start

The evaluator source is in `packages/evaluator/src`. To use it in a TypeScript project, install the package dependencies and build it:

```bash
npm install
npm run build
```

```ts
import { buildModelOrbitEvaluation } from '@orbit/evaluator';

const result = buildModelOrbitEvaluation({
  transcript: [
    { speaker: 'human', text: 'I need help', startedAtMs: 0, endedAtMs: 900 },
    { speaker: 'agent', text: 'I can help with that', startedAtMs: 1200, endedAtMs: 2200 },
  ],
});
```

The optional audio worker needs Python 3.10 or 3.11 and native/model dependencies. See [`services/audio-worker/README.md`](services/audio-worker/README.md). The first inference may download a model checkpoint; production deployments should provision model files ahead of time and review their licenses.

## Design principles

1. **Separate measurement from action.** An evaluator emits signals and evidence. A policy or voice agent chooses whether to act.
2. **Keep provenance.** Every observation should carry its source, confidence, time span, and evidence. Missing evidence stays missing.
3. **Do not confuse audio condition with failure probability.** Noise, loudness, SNR, or model scores are not calibrated probabilities of an agent failing.
4. **Production calls ground the baseline.** Synthetic audio expands controlled coverage; real call outcomes determine whether a signal or intervention matters.
5. **Learn offline, deploy deliberately.** Do not update model weights during an active call. Evaluate candidate changes against a held-out baseline before deployment.
6. **Make privacy the default.** Never commit call recordings, transcripts, credentials, or personal data. Use consented, minimized, access-controlled data.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md), the architecture notes, and the open roadmap. Helpful first contributions include metric adapters, evaluation datasets with clear provenance, baseline reports, integration examples, and reproducible intervention studies.

## License

Orbit's original code is released under the [MIT License](LICENSE). Third-party model code, checkpoints, and datasets are not bundled and keep their own terms. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) before adopting an adapter or weight file.

