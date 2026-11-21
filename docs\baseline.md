# Production-call baseline

The baseline is the **current production system before Orbit changes its behavior**. It describes the distribution of calls and outcomes that candidate Orbit versions must improve without causing regressions.

## Capture a baseline cohort

1. Select a representative time window and document agent version, provider, telephony path, locale, device/channel, and business outcome definitions.
2. Capture the temporal speech graph: aligned audio spans, speaker segments, pauses, overlap, agent actions, available transport telemetry, optional transcript confidence, and final outcomes.
3. Compute call-level and window-level summaries without interventions. Preserve raw per-window measures so averages do not hide short failures.
4. Label a stratified sample with human review: task success, misunderstood critical details, repair success, interruption appropriateness, and whether the audio plausibly contributed.
5. Split train/calibration/test by caller or conversation and by time. Do not put windows from one call in multiple splits.
6. Publish a dataset card and aggregate report; keep recordings private and out of Git.

## Baseline measures

- Task success and completion without correction.
- Critical-detail error rate (names, numbers, addresses, commitments).
- Repair/confirmation rate and time to successful repair.
- Unwanted interruption and missed-turn rate.
- Response latency and silence/overlap distributions.
- Human-rated speech intelligibility and perceived interaction quality on a reviewed subset.
- Audio condition distributions per dimension and by traffic segment.
- Agent intervention frequency, acceptance, and observed outcome.

For any quality signal, report rank correlation and calibration against **measured outcomes**, plus false-positive rates at the proposed operating threshold. A score of 0.5 is not a 50% failure probability unless a separate calibration study establishes that meaning.

## Compare an Orbit candidate

Use a frozen holdout and paired replay when possible. Compare the baseline agent with the candidate policy/model on the same scenarios. Report absolute changes, uncertainty intervals, subgroup results, latency/cost, and regressions. Keep live intervention disabled until the offline result and a shadow-mode run meet predeclared acceptance criteria.

## Privacy and access

Use consented and minimized production data under the existing call retention policy. Prefer derived event graphs with opaque IDs for routine evaluation. Restrict raw audio access, redact transcripts, set deletion windows, and record who accessed each cohort. Open-source schemas and aggregate findings; do not publish customer calls or re-identifiable data.

