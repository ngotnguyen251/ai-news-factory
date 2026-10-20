"""Render a 9:16 video with English Kokoro voice and Vietnamese subtitles.
Requires ffmpeg, ffprobe, and libass-enabled ffmpeg.
"""
import json
import subprocess
from pathlib import Path

OUT = Path("output")
OUT.mkdir(exist_ok=True)
voice = OUT / "demo_voice.wav"
if not voice.exists():
    raise SystemExit("Missing output/demo_voice.wav")
duration = float(json.loads(subprocess.check_output([
    "ffprobe", "-v", "error", "-show_entries", "format=duration",
    "-of", "json", str(voice)
]))["format"]["duration"])
lines = [
    "Chào mừng đến với AI News Factory.",
    "Đây là bản thử nghiệm hệ thống đọc tin bằng tiếng Anh.",
    "Trước khi đăng tin thật, chúng tôi kiểm tra ngày tháng, nguồn gốc và bằng chứng.",
    "Video sẽ có giọng đọc tiếng Anh và phụ đề tiếng Việt.",
    "Cảm ơn bạn đã theo dõi."
]
# Approximate subtitle timing for this demo only. Production requires forced alignment.
weights = [7, 15, 23, 15, 5]
def timestamp(seconds):
    millis = round(seconds * 1000)
    h, rem = divmod(millis, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"
start = 0.0
subs = []
for index, (line, weight) in enumerate(zip(lines, weights), 1):
    end = duration if index == len(lines) else start + duration * weight / sum(weights)
    subs.append(f"{index}\n{timestamp(start)} --> {timestamp(end)}\n{line}\n")
    start = end
(OUT / "demo_vi_timed.srt").write_text("\n".join(subs), encoding="utf-8")
cmd = [
    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
    "-f", "lavfi", "-i", "color=c=0x101c35:s=1080x1920:r=30",
    "-i", str(voice),
    "-vf", "drawtext=text='AI NEWS FACTORY':fontcolor=white:fontsize=74:x=(w-text_w)/2:y=360,"
           "drawtext=text='ENGLISH VOICE  |  VIETNAMESE SUBTITLES':fontcolor=yellow:fontsize=35:x=(w-text_w)/2:y=500,"
           "subtitles=output/demo_vi_timed.srt:force_style='FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,MarginV=250'",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "27",
    "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart",
    str(OUT / "demo_news.mp4")
]
subprocess.run(cmd, check=True)
print(f"Created {OUT / 'demo_news.mp4'} ({duration:.1f}s)")
