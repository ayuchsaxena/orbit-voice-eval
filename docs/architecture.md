# Orbit architecture

## Canonical representation: temporal speech graph

Orbit treats the **temporal speech graph** as the primary record for a call. A transcript is one optional evidence stream attached to graph events; it is not the call itself. This lets evaluation include silence, overlap, interruptions, clipped or uncertain speech, timing, acoustic conditions, and what the agent did in response.

The graph is an append-only timeline of typed events. Every event carries a time interval (or point), speaker/source, provenance, confidence, and links to related events. Store raw media separately under the host application's retention and consent policy; graph nodes should reference media spans rather than copy audio bytes.

Suggested event types:

| Event | Example fields | What it supports |
|---|---|---|
| `speech_segment` | speaker, start/end, media span, optional words | Turn timing and speech activity |
| `pause` / `silence` | start/end, preceding/following turn IDs | Delay, hesitation, endpointing |
| `overlap` / `barge_in` | both speaker IDs, start/end | Interruption and turn-taking |
| `audio_condition` | dimension, value, unit, window, evaluator | Noise, reverb, loudness, discontinuity |
| `transport_event` | packet/jitter/codec telemetry, source | Network or codec diagnosis from actual telemetry |
| `agent_action` | action type, trigger signal IDs, policy version | What the agent changed and why |
| `repair` / `confirmation` | linked user issue, agent response, resolution | Recovery and confirmation quality |
| `outcome` | task result, correction, escalation, human review | Ground truth for calibration |

### Graph invariants

- Preserve original timestamps and clock domains; record any alignment transform.
- Do not force uncertain events into precise labels. Use null/unknown plus a reason.
- Keep raw measurements, model estimates, human annotations, and inferences distinguishable.
- Link each claim to the event IDs and audio spans that support it.
- Represent missing or unavailable audio explicitly. Never infer packet loss from a decoded recording alone.
- Version the graph schema, evaluator, rubric, and intervention policy independently.

## Processing layers

1. **Capture:** ingest audio frames, timestamps, provider events, and optional transcript tokens without blocking the real-time audio callback.
2. **Event extraction:** generate speech segments, pauses, overlaps, quality windows, and transport events. Each extractor is an adapter with its own provenance.
3. **Graph assembly:** align observations on a shared call clock; keep both source time and aligned time when clocks differ.
4. **Evaluation:** compute graph features, transcript-supported semantic observations when text exists, and outcome labels after the call.
5. **Signal delivery:** publish a compact, typed signal to the agent with evidence IDs, confidence, expiry, and a suggested action class.
6. **Policy and agent response:** the agent decides whether/how to act; record the selected action and graph evidence that triggered it.
7. **Learning loop:** compare outcomes against the production baseline, review errors, and promote validated evaluator/policy versions offline.

## Live signal contract (proposed)

```json
{
  "schema": "orbit.signal.v1",
  "callId": "opaque-call-id",
  "createdAtMs": 12500,
  "expiresAtMs": 17500,
  "signal": "speech_competition",
  "value": 0.82,
  "unit": "score_0_1",
  "confidence": 0.74,
  "evidenceEventIds": ["evt_18", "evt_19"],
  "suggestedAction": "confirm_critical_detail",
  "limitations": ["background speaker source is unknown"]
}
```

This contract is a proposal, not a stable API. Signals should be short-lived and non-blocking. The model should not silently rewrite the agent's goals or change policy. Record the agent's response as another graph event for later evaluation.

## Where transcripts fit

Transcripts help with lexical accuracy, correction detection, intent/task evidence, and content-grounded response evaluation. They are optional graph annotations, not the canonical timing structure. When transcripts are unavailable or low-confidence, audio/timing evaluation still runs and semantic fields remain unscored.

## Current implementation boundary

The included evaluator and Brouhaha worker analyze completed captures. They are useful seeds for graph-aligned offline evaluation, but they do not yet produce the full event graph or support validated live intervention. The next implementation step is defining the event schema and ingestion adapters, then proving graph alignment on production calls.

