import re
from pathlib import Path

version_file = Path(__file__).parent / "js/src/version.js"
__version__ = re.search(
    r"const\s+version\s*=\s*['\"]([^'\"]+)['\"]", version_file.read_text()
).group(1)
