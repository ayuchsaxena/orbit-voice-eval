# Synthetic audio for development

Synthetic audio is for controlled coverage and early adaptation. It does not replace production-call validation or human ratings.

## Build paired examples

Start with speech audio whose use and redistribution terms allow the experiment. Preserve the clean source and create paired variants with one known change at a time:

- additive noise at recorded signal-to-noise ratios;
- room impulse response/reverb;
- gain and clipping;
- codec and sample-rate changes;
- time-varying dropouts, jitter, and frame loss;
- competing speech, with overlap start/end known.

Record source ID and license, transform, parameters, random seed, sample rate, target labels, and tool version in a dataset card. Split by source speaker and source recording before augmentation to avoid train/test leakage.

## Labels

Known transform parameters give ground truth for the synthetic condition (for example, the requested SNR or dropout interval). They do **not** give a ground-truth downstream agent failure or a human-perceived quality score. Collect separate blinded human ratings and run the actual voice agent to label task success, critical errors, interruption behavior, and repair outcomes.

Keep synthetic and production evaluations separate in reports. Calibrate on production calls and reserve real calls for final validation. A model that performs well only on generated distortions has not established real-world usefulness.

## Avoid shortcuts

- Do not train and test on adjacent chunks or transformed variants of the same source speaker.
- Do not use one metric's own pseudo-labels as the sole proof that a model learned quality.
- Do not overrepresent clean synthetic speech relative to actual production traffic.
- Do not assume reverberation, packet loss, or codec impairments can all be inferred from a final decoded waveform; use provider telemetry when available.
- Do not release source speech or derived recordings without verifying rights and privacy.

