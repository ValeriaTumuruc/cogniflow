"""Build a GitHub Pages artifact from an explicit public-file allowlist."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parent
PUBLIC=('index.html','privacy.html','styles.css','app.js','config.js','mark.svg','.nojekyll','assets/Barlow-Bold.ttf','assets/Barlow-Regular.ttf','assets/Barlow-OFL.txt')
dest=ROOT/'dist';dest.mkdir(exist_ok=True)
for name in PUBLIC:
    (dest/name).parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(ROOT/name,dest/name)
unexpected=set(p.relative_to(dest).as_posix() for p in dest.rglob('*') if p.is_file())-set(PUBLIC)
if unexpected:raise SystemExit('Unexpected build files; use a fresh dist folder: '+str(unexpected))
print('GitHub Pages artifact: '+str(dest))
