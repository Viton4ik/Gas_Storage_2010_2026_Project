"""Master the generated soundtrack and mux it with the unchanged engine render."""
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
cfg = json.loads((ROOT/'config.json').read_text())
build = ROOT/'build'
target = cfg['music'].get('lufs',-14)
first = subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(build/'music.wav'),
    '-af',f'loudnorm=I={target}:TP=-2.0:LRA=9:print_format=json','-f','null','-'],
    capture_output=True,text=True,check=True)
(build/'loudnorm-pass1.log').write_text(first.stderr)
measured, _ = json.JSONDecoder().raw_decode(first.stderr[first.stderr.rfind('{'):])
audio_filter = (f"loudnorm=I={target}:TP=-2.0:LRA=9:"
    f"measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:"
    f"measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:"
    f"offset={measured['target_offset']}:linear=true:print_format=json,"
    "aresample=48000,alimiter=limit=0.7:level=false:latency=true")
out=ROOT/cfg['output'];out.parent.mkdir(parents=True,exist_ok=True)
second = subprocess.run(['ffmpeg','-y','-hide_banner','-nostats',
    '-i',str(build/'race_silent.mp4'),'-i',str(build/'music.wav'),
    '-map','0:v:0','-map','1:a:0','-af',audio_filter,
    '-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000',
    '-shortest','-movflags','+faststart',str(out)],capture_output=True,text=True,check=True)
(build/'mastering.log').write_text(second.stderr)
print(out)
