"""Reproduce the complete 120-second storage film."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse
import json
import subprocess
import sys

parser=argparse.ArgumentParser()
parser.add_argument('--workers',type=int,default=4)
args=parser.parse_args()
assert 1 <= args.workers <= 16
root=Path(__file__).resolve().parents[1]
cfg=json.loads((root/'config.json').read_text())
build=root/'build'
build.mkdir(exist_ok=True)
duration=sum(cfg['timing'][key] for key in ['intro','race','hold','outro'])
frames=round(duration*cfg['video']['fps'])
chunk=(frames+args.workers-1)//args.workers

subprocess.run([sys.executable,'engine/render_storage.py','--config','config.json','--check'],cwd=root,check=True)

def render(i):
    with (build/f'full_{i}.log').open('w') as log:
        subprocess.run([sys.executable,'engine/render_storage.py','--config','config.json',
            '--start',str(i*chunk),'--end',str(min((i+1)*chunk,frames)),
            '--out',str(build/f'full_{i}.mp4')],cwd=root,
            stdout=log,stderr=subprocess.STDOUT,check=True)
    print(f'Segment {i+1}/{args.workers} ready',flush=True)

with ThreadPoolExecutor(max_workers=args.workers) as pool:
    list(pool.map(render,range(args.workers)))
(build/'full_concat.txt').write_text(''.join(f"file 'full_{i}.mp4'\n" for i in range(args.workers)))
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0',
    '-i','build/full_concat.txt','-c','copy','build/race_silent.mp4'],cwd=root,check=True)
subprocess.run([sys.executable,'engine/music.py','--config','config.json'],cwd=root,check=True)
subprocess.run([sys.executable,'scripts/master_and_mux.py'],cwd=root,check=True)
