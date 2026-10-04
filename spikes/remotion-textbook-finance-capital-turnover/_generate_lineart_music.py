"""Generate a quiet deterministic xylophone/plucked backing track (22050 Hz mono)."""
import math
import struct
import wave
from pathlib import Path

RATE=22050
DURATION=280.0
OUT=Path(__file__).resolve().parent/'lineart-final'/'public'/'audio'/'music.wav'
notes=[261.63,329.63,392.00,523.25,440.00,392.00,329.63,293.66]
beat=1.5
samples=[]
for n in range(int(RATE*DURATION)):
    t=n/RATE
    idx=int(t/beat)%len(notes)
    local=t%beat
    env=math.exp(-3.6*local)*(1-math.exp(-35*local))
    f=notes[idx]
    tone=(math.sin(2*math.pi*f*t)+0.34*math.sin(2*math.pi*2*f*t)+0.12*math.sin(2*math.pi*3*f*t))*env
    pad=0.18*math.sin(2*math.pi*(f/4)*t)*(0.6+0.4*math.sin(2*math.pi*t/24))
    v=max(-1,min(1,0.20*tone+0.07*pad))
    samples.append(struct.pack('<h',int(v*32767)))
OUT.parent.mkdir(parents=True,exist_ok=True)
with wave.open(str(OUT),'wb') as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(b''.join(samples))
print(OUT, OUT.stat().st_size)
