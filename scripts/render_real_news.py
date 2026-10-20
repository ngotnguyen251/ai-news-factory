"""Create a sourced 9:16 graphic news video with per-segment Kokoro audio and Vietnamese subtitles.
Visuals are explicitly editorial graphics, not purported footage.
"""
import json, subprocess, textwrap
from pathlib import Path
import numpy as np
import soundfile as sf
from kokoro import KPipeline

story=json.loads(Path("stories/france_2026_10_20.json").read_text(encoding="utf-8"))
out=Path("output"); out.mkdir(exist_ok=True)
pipeline=KPipeline(lang_code="a")
all_audio=[]; timings=[]; position=0
for i,seg in enumerate(story["segments"]):
    chunks=[np.asarray(audio) for _,_,audio in pipeline(seg["en"],voice="af_heart",speed=1.06)]
    if not chunks: raise RuntimeError(f"No voice for segment {i}")
    samples=np.concatenate(chunks)
    pause=np.zeros(6000,dtype=samples.dtype)
    all_audio.extend([samples,pause])
    duration=(len(samples)+len(pause))/24000
    timings.append((position,position+duration,seg))
    position+=duration
sf.write(str(out/"france_voice.wav"),np.concatenate(all_audio),24000)
def stamp(t):
    ms=round(t*1000); h,rem=divmod(ms,3600000);m,rem=divmod(rem,60000);s,ms=divmod(rem,1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"
srt=[]
for i,(start,end,seg) in enumerate(timings,1):
    srt.append(f"{i}\n{stamp(start)} --> {stamp(end)}\n{seg['vi']}\n")
(out/"france_vi.srt").write_text("\n".join(srt),encoding="utf-8")
# ASS subtitles allow reliable Vietnamese rendering with a Unicode font.
def ass_time(t):
    cs=round(t*100);h,rem=divmod(cs,360000);m,rem=divmod(rem,6000);s,cs=divmod(rem,100)
    return f"{h}:{m:02}:{s:02}.{cs:02}"
def ass_escape(t):
    return t.replace("{","").replace("}","")
ass=["[Script Info]","ScriptType: v4.00+","PlayResX: 1080","PlayResY: 1920",
"[V4+ Styles]","Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
"Style: Default,DejaVu Sans,36,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,3,1,2,70,70,320,1",
"[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
for start,end,seg in timings:
    # Wrap Vietnamese at sensible boundaries for 9:16.
    wrapped="\\N".join(textwrap.wrap(seg["vi"],width=39,break_long_words=False))
    ass.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Default,,0,0,0,,{ass_escape(wrapped)}")
(out/"france_vi.ass").write_text("\n".join(ass)+"\n",encoding="utf-8")
# Create a different motion graphic per narration segment.
clips=[]
for i,(start,end,seg) in enumerate(timings):
    dur=end-start
    # drawtext receives ASCII editorial headlines; real reporting attribution remains in script and metadata.
    heading=seg["heading"].replace(":","\\:")
    detail=seg["detail"].replace(":","\\:")
    filters=(
      "drawbox=x=0:y=0:w=iw:h=170:color=0x8b1734:t=fill,"
      "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='WORLD NEWS':fontsize=72:fontcolor=white:x=65:y=52,"
      f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='{heading}':fontsize=58:fontcolor=white:x=(w-text_w)/2:y=590,"
      f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='{detail}':fontsize=38:fontcolor=0xFFD166:x=(w-text_w)/2:y=710,"
      "drawbox=x=75:y=850:w=930:h=4:color=0xFFD166:t=fill,"
      "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='EDITORIAL GRAPHIC - NOT EVENT FOOTAGE':fontsize=26:fontcolor=white:x=(w-text_w)/2:y=1520,"
      "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='20 OCT 2026  |  REUTERS + AP':fontsize=30:fontcolor=white:x=(w-text_w)/2:y=1620"
    )
    clip=out/f"scene_{i:02}.mp4"
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","lavfi","-i",
        f"color=c=0x101c35:s=1080x1920:r=30:d={dur:.3f}","-vf",filters,
        "-an","-c:v","libx264","-preset","ultrafast","-crf","30",str(clip)],check=True)
    clips.append(clip)
(out/"concat.txt").write_text("".join(f"file '{p.name}'\n" for p in clips),encoding="utf-8")
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0",
    "-i",str(out/"concat.txt"),"-i",str(out/"france_voice.wav"),"-vf",
    "ass=output/france_vi.ass","-c:v","libx264","-preset","veryfast","-crf","26",
    "-c:a","aac","-b:a","128k","-shortest","-movflags","+faststart",str(out/"france_news_review.mp4")],check=True)
(out/"sources.json").write_text(json.dumps({"title":story["title"],"status":story["status"],
 "sources":story["sources"],"created_from":"manually sourced reporting 2026-10-20",
 "visual_note":"Editorial motion graphics only; no licensed news footage"},indent=2),encoding="utf-8")
print("Created:",out/"france_news_review.mp4")
