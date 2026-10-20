# AI News Factory

Free-tier prototype for news video production.

**Current stage:** collects fresh English-language headline candidates at 19:00 Vietnam time and saves JSON artifacts for editorial review. It does **not** automatically claim news is verified, create videos, or publish to YouTube.

Planned pipeline: RSS -> source verification -> English script -> Kokoro TTS -> Vietnamese subtitles -> OpenMontage render -> human review.

## Test
Open Actions > Daily news candidate > Run workflow. Download the `news-candidates` artifact when the run completes.

## Local Kokoro test
Install Python 3.12, eSpeak NG, then `pip install kokoro soundfile numpy`.
Run `python scripts/kokoro_voice.py script_en.txt output/voice.wav`.

The OpenMontage CLI/API must be confirmed before integration. GitHub Actions scheduled workflows may be delayed. No paid API keys are required for the current RSS stage.
