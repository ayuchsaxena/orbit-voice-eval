# Orbit audio worker

This optional FastAPI service runs post-call analysis on separated human and agent tracks. It returns five-second speech activity, estimated SNR and C50, plus direct RMS, peak, and clipping measures. It is a starter adapter, not yet a streaming service or a Tyto-equivalent risk model.

## Run

Use Python 3.10 or 3.11 in an isolated environment:

```bash
python -m pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8001
```

Configure `MODELORBIT_SERVICE_TOKEN` and pass it as a Bearer token to `/analyze`. Set `MODELORBIT_BROUHAHA_CHECKPOINT` to a local checkpoint path to avoid a first-run download. Keep the service on a trusted network and configure request limits before deployment.

## Inputs and outputs

`POST /analyze` accepts `human` and `agent` audio files. Supported decoding depends on PyAV/FFmpeg. Audio is decoded to mono 16 kHz. The current implementation caps each file at 50 MB and two hours. `/health` reports service status.

## Limits

- Analysis is post-call and uses a fixed five-second summary window.
- SNR and C50 are model estimates; RMS and clipping are signal measurements.
- The worker does not detect competing speech, infer packet loss, diagnose codec settings, or estimate an agent failure probability.
- Do not use a waveform-only guess to name the network or codec root cause; attach actual transport telemetry to the temporal graph.
- The current worker uses private pyannote pipeline internals; pin dependencies and replace with a stable adapter before production use.

