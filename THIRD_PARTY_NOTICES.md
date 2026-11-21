# Third-party components and model terms

Orbit does not bundle third-party model checkpoints or datasets. Integrators must verify the current license and usage terms for each component they download or call.

- The optional audio worker uses [Brouhaha](https://github.com/marianne-m/brouhaha-vad) and the `ylacombe/brouhaha-best` checkpoint. The source repository and model card currently identify MIT terms; verify the exact release artifacts and preserve attribution.
- [NISQA](https://github.com/gabrielmittag/NISQA) is a candidate evaluator. Its repository states that code is MIT, while released weights are CC BY-NC-SA 4.0. Those weights are not included and may not suit commercial deployment.
- [VERSA](https://github.com/wavlab-speech/versa) is an MIT-licensed metrics toolkit, but individual metric backends and downloaded weights can carry separate terms.
- [DNS Challenge data](https://github.com/microsoft/DNS-Challenge) and other public audio datasets retain their own source-speech and noise licenses. Review each asset's terms before use.

This file is an implementation note, not legal advice. Please submit corrections with the exact version and license evidence.

