"""Kinetic typography news renderer. Storyboard generated from sourced editorial segments.
Requires Kokoro, ffmpeg (drawtext/libass), Pillow and DejaVu fonts.
No news footage is implied. Review required before publication.
"""
import json, math, re, subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont
from kokoro import KPipeline

ROOT=Path("output");ROOT.mkdir(exist_ok=True)
story=json.loads(Path("stories/france_2026_10_20.json").read_text(encoding="utf-8"))
W,H=720,1280
font="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
regular="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
voice=KPipeline(lang_code="a")
segments=[]
parts=[]
cursor=0.
for index,s in enumerate(story["segments"]):
    waves=[np.asarray(a) for _,_,a in voice(s["en"],voice="af_heart",speed=1.06)]
    if not waves:raise RuntimeError("Kokoro returned no audio")
    a=np.concatenate(waves)
    pause=np.zeros(7200,dtype=a.dtype)
    parts.extend([a,pause])
    duration=(len(a)+len(pause))/24000
    segments.append({"start":cursor,"end":cursor+duration,"duration":duration,**s})
    cursor+=duration
sf.write(str(ROOT/"motion_voice.wav"),np.concatenate(parts),24000)

def clock(t):
    v=round(t*1000);h,v=divmod(v,3600000);m,v=divmod(v,60000);s,ms=divmod(v,1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"
def assclock(t):
    v=round(t*100);h,v=divmod(v,360000);m,v=divmod(v,6000);s,cs=divmod(v,100)
    return f"{h}:{m:02}:{s:02}.{cs:02}"
# Per-segment subtitles; no fabricated word-level karaoke alignment.
srt=[]
ass=["[Script Info]","ScriptType: v4.00+","PlayResX: 720","PlayResY: 1280",
"[V4+ Styles]","Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
"Style: Subtitle,DejaVu Sans,30,&H00FFFFFF,&H0000FFFF,&H00000000,&H99000000,0,0,0,0,100,100,0,0,1,2,1,2,46,46,180,1",
"[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
for i,s in enumerate(segments,1):
    srt.append(f"{i}\n{clock(s['start'])} --> {clock(s['end'])}\n{s['vi']}\n")
    # ASS automatic line wrap; avoid escaping ASS line-break controls.
    ass.append(f"Dialogue: 0,{assclock(s['start'])},{assclock(s['end'])},Subtitle,,0,0,0,,{s['vi'].replace('{','').replace('}','')}")
(ROOT/"motion_vi.srt").write_text("\n".join(srt),encoding="utf-8")
(ROOT/"motion_vi.ass").write_text("\n".join(ass)+"\n",encoding="utf-8")

def fit(draw,text,maxwidth,maxsize=76):
    for size in range(maxsize,24,-2):
        f=ImageFont.truetype(font,size)
        if draw.textbbox((0,0),text,font=f)[2] <=maxwidth:return f
    return ImageFont.truetype(font,24)
def art(i,s):
    im=Image.new("RGB",(W,H),(10,15,26))
    d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,115),fill=(206,35,58))
    d.text((45,34),"WORLD  /  NEWS",font=ImageFont.truetype(font,35),fill="white")
    d.text((48,166),f"0{i+1} / 0{len(segments)}",font=ImageFont.truetype(regular,28),fill=(255,204,84))
    words=s["heading"].split()
    lines=[];line=""
    for word in words:
        candidate=(line+" "+word).strip()
        if len(candidate)>15 and line:lines.append(line);line=word
        else:line=candidate
    if line:lines.append(line)
    for j,line in enumerate(lines):
        f=fit(d,line,620,78)
        d.text((48,330+j*112),line,font=f,fill=(255,255,255))
    d.rectangle((48,665,672,674),fill=(255,204,84))
    f=fit(d,s["detail"],620,37)
    d.text((48,708),s["detail"],font=f,fill=(255,204,84))
    d.text((48,1020),"EDITORIAL GRAPHICS • NOT EVENT FOOTAGE",font=ImageFont.truetype(regular,18),fill=(174,185,203))
    d.text((48,1060),"20 OCT 2026   •   REUTERS / AP",font=ImageFont.truetype(regular,20),fill=(174,185,203))
    path=ROOT/f"motion_card_{i:02}.png";im.save(path);return path

clips=[]
for i,s in enumerate(segments):
    card=art(i,s);clip=ROOT/f"motion_scene_{i:02}.mp4"
    dur=s["duration"]
    # Continuous animated crop/zoom; fade in/out with timing matched to narration.
    fadeout=max(0,dur-0.3)
    vf=(f"zoompan=z='min(zoom+0.0007,1.12)':x='iw/2-(iw/zoom/2)':"
        f"y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps=24,"
        f"fade=t=in:st=0:d=0.25,fade=t=out:st={fadeout:.3f}:d=0.3,"
        "format=yuv420p")
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-loop","1","-framerate","24",
        "-i",str(card),"-t",f"{dur:.3f}","-vf",vf,"-an","-c:v","libx264","-preset","veryfast",
        "-crf","25",str(clip)],check=True)
    clips.append(clip)
(ROOT/"motion_concat.txt").write_text("".join(f"file '{p.name}'\n" for p in clips),encoding="utf-8")
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0",
    "-i",str(ROOT/"motion_concat.txt"),"-i",str(ROOT/"motion_voice.wav"),
    "-c:v","libx264","-preset","veryfast","-crf","24",
    "-c:a","aac","-b:a","128k","-shortest","-movflags","+faststart",
    str(ROOT/"motion_news_review.mp4")],check=True)
(ROOT/"motion_storyboard.json").write_text(json.dumps({"status":"REVIEW_REQUIRED","story":story["title"],
 "shots":[{"heading":s["heading"],"detail":s["detail"],"start":s["start"],"end":s["end"]} for s in segments],
 "visual_method":"animated editorial title cards, not event footage"},indent=2),encoding="utf-8")
print("Video ready for editorial review:",ROOT/"motion_news_review.mp4")
