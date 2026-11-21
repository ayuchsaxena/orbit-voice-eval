"""ModelOrbit post-call audio analysis service.

Uses Brouhaha for speech activity, speech-to-noise ratio, and C50 measurements.
It deliberately does not synthesize a Tyto-like downstream risk probability.
"""

from __future__ import annotations

import io
import os
import tempfile
import threading
import wave
from pathlib import Path
from typing import Any

import av
import numpy as np
from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

SERVICE_VERSION = "modelorbit-audio-0.1.0"
WINDOW_MS = 5_000
MAX_AUDIO_BYTES = 50 * 1024 * 1024
TARGET_SAMPLE_RATE = 16_000
VAD_THRESHOLD = 0.78  # Brouhaha's development-set default threshold.

app = FastAPI(title="ModelOrbit Audio Analysis", version=SERVICE_VERSION)
model_lock = threading.Lock()
pipeline: Any | None = None


def load_pipeline():
    global pipeline
    if pipeline is not None:
        return pipeline
    with model_lock:
        if pipeline is not None:
            return pipeline
        checkpoint = os.getenv("MODELORBIT_BROUHAHA_CHECKPOINT", "").strip()
        if checkpoint:
            checkpoint_path = Path(checkpoint)
        else:
            try:
                from huggingface_hub import hf_hub_download
            except ImportError as error:
                raise RuntimeError("Install huggingface_hub or set MODELORBIT_BROUHAHA_CHECKPOINT.") from error
            checkpoint_path = Path(hf_hub_download(repo_id="ylacombe/brouhaha-best", filename="best.ckpt"))
        try:
            from pyannote.audio import Model
            from brouhaha.pipeline import RegressiveActivityDetectionPipeline
        except ImportError as error:
            raise RuntimeError("Install the optional Brouhaha and pyannote.audio dependencies.") from error
        model = Model.from_pretrained(checkpoint_path, strict=False)
        pipeline = RegressiveActivityDetectionPipeline(segmentation=model)
        return pipeline


def decode_audio(data: bytes) -> tuple[np.ndarray, int]:
    try:
        chunks: list[np.ndarray] = []
        decoded_samples = 0
        with av.open(io.BytesIO(data), mode="r") as container:
            stream = next((candidate for candidate in container.streams if candidate.type == "audio"), None)
            if stream is None:
                raise ValueError("No audio track found in the uploaded recording.")
            resampler = av.AudioResampler(format="fltp", layout="mono", rate=TARGET_SAMPLE_RATE)
            for frame in container.decode(stream):
                for converted in resampler.resample(frame):
                    chunk = converted.to_ndarray().reshape(-1).astype(np.float32, copy=False)
                    decoded_samples += chunk.size
                    if decoded_samples > TARGET_SAMPLE_RATE * 2 * 60 * 60:
                        raise ValueError("Audio track exceeds the two-hour analysis limit.")
                    chunks.append(chunk)
            for converted in resampler.resample(None):
                chunk = converted.to_ndarray().reshape(-1).astype(np.float32, copy=False)
                decoded_samples += chunk.size
                if decoded_samples > TARGET_SAMPLE_RATE * 2 * 60 * 60:
                    raise ValueError("Audio track exceeds the two-hour analysis limit.")
                chunks.append(chunk)
    except ValueError:
        raise
    except Exception as error:
        raise ValueError("Could not decode this audio track. Supported formats include WAV, MP3, M4A, OGG/Opus, and WebM/Opus.") from error
    samples = np.concatenate(chunks) if chunks else np.array([], dtype=np.float32)
    return np.clip(samples, -1.0, 1.0), TARGET_SAMPLE_RATE


def signal_window(samples: np.ndarray, sample_rate: int) -> dict[str, float]:
    if not samples.size:
        return {"rmsDbfs": -120.0, "peakDbfs": -120.0, "clippedSampleRatio": 0.0}
    rms = float(np.sqrt(np.mean(np.square(samples, dtype=np.float64))))
    peak = float(np.max(np.abs(samples)))
    return {
        "rmsDbfs": round(20.0 * np.log10(max(rms, 1e-6)), 2),
        "peakDbfs": round(20.0 * np.log10(max(peak, 1e-6)), 2),
        "clippedSampleRatio": round(float(np.mean(np.abs(samples) >= 0.999)), 6),
    }


def analyze_track(data: bytes, speaker: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    samples, sample_rate = decode_audio(data)
    if not samples.size:
        raise ValueError(f"The {speaker} audio track is empty.")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temporary:
        temporary_path = Path(temporary.name)
    try:
        pcm = np.clip(samples * 32767.0, -32768, 32767).astype("<i2")
        with wave.open(str(temporary_path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(pcm.tobytes())
        active_pipeline = load_pipeline()
        with model_lock:
            inference = active_pipeline._segmentation({"uri": speaker, "audio": str(temporary_path)})
        matrix = np.asarray(inference.data, dtype=np.float64)
        if matrix.ndim != 2 or matrix.shape[1] < 3:
            raise RuntimeError("Brouhaha returned an unexpected output shape.")
        stride_s = float(inference.sliding_window.step)
        frame_s = float(inference.sliding_window.duration)
        start_s = float(inference.sliding_window.start)
        duration_ms = int(round(samples.size * 1000 / sample_rate))
        window_count = max(1, int(np.ceil(duration_ms / WINDOW_MS)))
        grouped: list[list[int]] = [[] for _ in range(window_count)]
        for index in range(matrix.shape[0]):
            center_ms = (start_s + index * stride_s + frame_s / 2) * 1000
            grouped[min(window_count - 1, max(0, int(center_ms // WINDOW_MS)))].append(index)

        windows: list[dict[str, Any]] = []
        for bucket, indices in enumerate(grouped):
            begin_ms = bucket * WINDOW_MS
            end_ms = min(duration_ms, begin_ms + WINDOW_MS)
            signal_start = int(begin_ms * sample_rate / 1000)
            signal_end = int(end_ms * sample_rate / 1000)
            metrics = signal_window(samples[signal_start:signal_end], sample_rate)
            if indices:
                block = matrix[indices]
                vad = block[:, 0]
                snr = block[:, 1]
                c50 = block[:, 2]
                speech_mask = vad >= VAD_THRESHOLD
                speech_ratio = float(np.mean(speech_mask))
                snr_value = float(np.mean(snr[speech_mask])) if np.any(speech_mask) else None
                c50_value = float(np.mean(c50[speech_mask])) if np.any(speech_mask) else None
                vad_mean = float(np.mean(vad))
            else:
                speech_ratio = 0.0
                snr_value = None
                c50_value = None
                vad_mean = 0.0
            windows.append({
                "startMs": begin_ms,
                "endMs": end_ms,
                "speechActivityRatio": round(speech_ratio, 4),
                "speechToNoiseRatioDb": round(snr_value, 2) if snr_value is not None else None,
                "c50Db": round(c50_value, 2) if c50_value is not None else None,
                "vadConfidenceMean": round(vad_mean, 4),
                **metrics,
            })

        all_vad = matrix[:, 0]
        all_snr = matrix[:, 1]
        all_c50 = matrix[:, 2]
        voiced = all_vad >= VAD_THRESHOLD
        summary = {
            "durationMs": duration_ms,
            "sampleRateHz": sample_rate,
            "speechActivityRatio": round(float(np.mean(voiced)), 4),
            "speechToNoiseRatioDb": round(float(np.mean(all_snr[voiced])), 2) if np.any(voiced) else None,
            "c50Db": round(float(np.mean(all_c50[voiced])), 2) if np.any(voiced) else None,
            **signal_window(samples, sample_rate),
        }
        return summary, windows
    finally:
        temporary_path.unlink(missing_ok=True)


def require_service_token(authorization: str | None) -> None:
    expected = os.getenv("MODELORBIT_SERVICE_TOKEN", "").strip()
    if not expected:
        raise HTTPException(status_code=503, detail="MODELORBIT_SERVICE_TOKEN is not configured.")
    if expected and authorization != f"Bearer {expected}":
        raise HTTPException(status_code=401, detail="Invalid service token.")


@app.get("/health")
def health():
    return {"ok": True, "serviceVersion": SERVICE_VERSION}


@app.post("/analyze")
async def analyze(
    human: UploadFile = File(...),
    agent: UploadFile = File(...),
    authorization: str | None = Header(default=None),
):
    require_service_token(authorization)
    uploads: dict[str, bytes] = {}
    for speaker, upload in (("human", human), ("agent", agent)):
        contents = await upload.read(MAX_AUDIO_BYTES + 1)
        if len(contents) > MAX_AUDIO_BYTES:
            raise HTTPException(status_code=413, detail=f"The {speaker} track exceeds 50 MB.")
        uploads[speaker] = contents
    try:
        human_result, human_windows = await run_in_threadpool(analyze_track, uploads["human"], "human")
        agent_result, agent_windows = await run_in_threadpool(analyze_track, uploads["agent"], "agent")
    except ValueError as error:
        raise HTTPException(status_code=415, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail="ModelOrbit audio analysis failed.") from error

    audio_windows = [
        {"speaker": speaker, **window}
        for speaker, windows in (("human", human_windows), ("agent", agent_windows))
        for window in windows
    ]
    def voice_signals(summary: dict[str, Any], windows: list[dict[str, Any]]) -> dict[str, Any]:
        amplitudes = [10 ** (window["rmsDbfs"] / 20) for window in windows]
        return {
            **summary,
            "rmsMean": 10 ** (summary["rmsDbfs"] / 20),
            "rmsVariation": float(np.std(amplitudes)) if amplitudes else None,
            "pauseRatio": 1.0 - summary["speechActivityRatio"],
            "voicedRatio": summary["speechActivityRatio"],
            "pitchMeanHz": None,
            "pitchVariationHz": None,
            "pitchRangeHz": None,
            "confidence": None,
        }

    return {
        "serviceVersion": SERVICE_VERSION,
        "human": voice_signals(human_result, human_windows),
        "agent": voice_signals(agent_result, agent_windows),
        "audioAnalysis": {
            "riskScore": None,
            "percentDegraded": None,
            "primaryDriver": None,
            "dimensions": {},
            "windows": [],
            "signalMetrics": {"human": human_result, "agent": agent_result},
            "signalWindows": audio_windows,
            "unavailableDimensions": ["interfering_speech", "packet_loss", "codec_degradation", "downstream_risk"],
            "model": "brouhaha-vad-c50-snr+signal-core",
            "limitations": [
                "These are speech, SNR, C50, level, and clipping measurements; they are not Tyto risk predictions.",
                "Competing-speech detection and network/codec diagnosis are not supplied by this analysis.",
            ],
        },
    }

