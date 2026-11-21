# Why Orbit

## The question Orbit is built to answer

**Which time-local speech or audio conditions accompanied a real production failure, how did the agent respond, and did a change improve the outcome?**

An agent-to-agent voice test usually stages a simulated caller and a voice agent in a spoken scenario. This is a strong way to create repeatable coverage: the test can control the goal, caller behavior, audio perturbations, and expected result. Current open evaluation systems can capture both sides' audio, transcripts, latency, and tool or scenario outcomes. Orbit does not dismiss or replace those capabilities.

Orbit's intended difference is the **source of the baseline and the unit of analysis**:

| Agent-to-agent scenario testing | Orbit's production-grounded loop |
|---|---|
| Starts with an authored or generated scenario and a simulated caller | Starts with consented, privacy-controlled production calls and measured outcomes |
| Asks whether the agent handles that test scenario | Asks what happened in real traffic and whether the current system improved |
| Usually reports scenario or conversation results | Uses a temporal speech graph to connect time-aligned events, audio conditions, agent actions, and later outcomes |
| Adds synthetic perturbations to expand controlled coverage | Uses synthetic perturbations for stress tests, then validates conclusions on held-out production calls |

The temporal graph is important because a call-level pass/fail or transcript can hide **when** an issue happened and how events related. A graph can link a pause, overlap, uncertain speech segment, or measured audio window to the agent action that followed and to a later correction, confirmation, escalation, or task outcome. Each observation carries its timing and source; a transcript is optional evidence attached to that timeline.

## Why this can improve continual improvement

1. **Grounded baseline:** real callers, devices, networks, and tasks define the current performance reference.
2. **Localizable evidence:** event timing makes it possible to inspect the part of a call associated with a failure rather than relying only on a whole-call score.
3. **Outcome linkage:** Orbit can compare a signal with the agent response and the observed result, then check whether an intervention helped.
4. **Controlled development:** simulation and synthetic audio expand repeatable coverage around cases seen in production.
5. **Safer promotion:** candidate signals and policies can run offline or in shadow mode before they are allowed to affect live behavior.

These are design advantages, not established empirical results. Production data can be biased, expensive to review, and sensitive. Simulators can be repeatable and broad, but their behavior and scenario distribution may not match real callers. Use both, and report where each provides evidence.

## Interview version

> “Agent-to-agent testing is great for repeatable scenarios. Orbit adds a production-grounded improvement loop: each call becomes a time-aligned speech graph, so we can connect audio and turn-taking events to the agent's response and the actual outcome. We use real production calls as the baseline, use synthetic and simulated calls to stress-test specific conditions, and validate changes on held-out real traffic. The current repo is an experimental post-call foundation; it does not yet prove a live intervention improves outcomes.”

## Public boundary

The open repository shares the event schema, initial evaluators, integration contracts, and baseline methodology so contributors can build compatible tools. It intentionally contains no customer recordings or transcripts. Product-specific production thresholds, private training data, and any non-public scoring or intervention policies are outside this starter repository.

## References

- [NVIDIA NeMo Labs Voice Agent evaluation overview](https://docs.nvidia.com/nemo/labs-voice-agent/evaluate-voice-agents/overview/): describes live spoken evaluation with a simulated user, audio and transcript capture, latency measurement, and scenario scoring.
- [ServiceNow EVA repository](https://github.com/ServiceNow/eva): describes end-to-end bot-to-bot evaluation across task accuracy and conversational experience, with audio perturbations and conversation artifacts.

