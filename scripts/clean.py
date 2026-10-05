"""Remove only lab-generated directories after the Make target stops containers."""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
for relative in ('security/runtime', 'artifacts'):
    target = root / relative
    if target.is_symlink() or not target.resolve().is_relative_to(root):
        raise RuntimeError(f'Refusing cleanup outside the repository: {target}')
    if target.exists():
        shutil.rmtree(target)
(root / 'artifacts').mkdir()
(root / 'artifacts/.gitkeep').touch()
