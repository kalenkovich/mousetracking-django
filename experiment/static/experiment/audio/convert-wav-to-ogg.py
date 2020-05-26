# This has to be run in the conda environment, not the venv one.
from pathlib import Path

import pydub

wav_dir = Path('wav')
ogg_dir = Path('ogg')

for wav in wav_dir.glob('*.wav'):
    ogg = ogg_dir / wav.relative_to(wav_dir).with_suffix('.ogg')
    pydub.AudioSegment.from_wav(wav).export(ogg, format="ogg")

