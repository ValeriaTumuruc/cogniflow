"""Build a GitHub Pages artifact from an explicit public-file allowlist."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parent
PUBLIC=('index.html','privacy.html','styles.css','app.js','config.js','mark.svg','.nojekyll')
dest=ROOT/'dist';dest.mkdir(exist_ok=True)
for name in PUBLIC:shutil.copyfile(ROOT/name,dest/name)
unexpected=set(p.name for p in dest.iterdir())-set(PUBLIC)
if unexpected:raise SystemExit('Unexpected build files; use a fresh dist folder: '+str(unexpected))
print('GitHub Pages artifact: '+str(dest))
