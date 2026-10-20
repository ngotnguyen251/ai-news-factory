"""Create English narration with Kokoro: python scripts/kokoro_voice.py script_en.txt output/voice.wav"""
import sys
from pathlib import Path
import numpy as np
import soundfile as sf
from kokoro import KPipeline

if len(sys.argv) != 3:
    raise SystemExit("Usage: python scripts/kokoro_voice.py script_en.txt output/voice.wav")
script = Path(sys.argv[1]).read_text(encoding="utf-8")
pipeline = KPipeline(lang_code="a")
chunks = [audio for _, _, audio in pipeline(script, voice="af_heart", speed=1.0)]
if not chunks:
    raise RuntimeError("No audio produced")
output = Path(sys.argv[2])
output.parent.mkdir(parents=True, exist_ok=True)
sf.write(str(output), np.concatenate(chunks), 24000)
print(output)
